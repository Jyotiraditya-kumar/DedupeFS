#include "core/storage_optimizer.hpp"
#include "utils/logger.hpp"

#include <unistd.h>
#include <cstdio>
#include <cerrno>
#include <cstring>
#include <sys/stat.h>

namespace dedupfs {
namespace core {

StorageOptimizer::StorageOptimizer(DedupMode mode)
    : mode_(mode) {}

bool StorageOptimizer::consolidate_file(const std::string& canonical_path, const std::string& duplicate_path) {
    struct stat st_canon;
    struct stat st_dup;

    if (stat(canonical_path.c_str(), &st_canon) != 0) {
        utils::Logger::error("Cannot stat canonical file: " + canonical_path);
        return false;
    }

    if (stat(duplicate_path.c_str(), &st_dup) != 0) {
        utils::Logger::error("Cannot stat duplicate file: " + duplicate_path);
        return false;
    }

    // Check cross-device filesystem boundary
    if (st_canon.st_dev != st_dup.st_dev) {
        utils::Logger::warning("Cannot hard-link across different filesystem devices: " + duplicate_path);
        return false;
    }

    // If they already share the exact same inode, they are already linked!
    if (st_canon.st_ino == st_dup.st_ino) {
        return true;
    }

    // Atomic replacement pattern:
    // 1. Create temporary hard link to canonical file in the same directory as duplicate
    std::string temp_link = duplicate_path + ".dedupfs_tmp";

    // Clean up any stale temp link
    unlink(temp_link.c_str());

    if (link(canonical_path.c_str(), temp_link.c_str()) != 0) {
        utils::Logger::error("Failed to link() " + canonical_path + " to " + temp_link + ": " + std::strerror(errno));
        return false;
    }

    // 2. Atomically rename temporary link over duplicate file
    if (rename(temp_link.c_str(), duplicate_path.c_str()) != 0) {
        utils::Logger::error("Failed to rename() temp link over " + duplicate_path + ": " + std::strerror(errno));
        unlink(temp_link.c_str());
        return false;
    }

    return true;
}

OptimizationReport StorageOptimizer::optimize_group(const DuplicateGroup& group, DedupStats& stats) {
    OptimizationReport report;
    report.groups_processed = 1;

    for (const auto& dup : group.duplicates) {
        if (group.canonical_file.device != dup.device) {
            report.cross_device_skipped++;
            continue;
        }

        if (mode_ == DedupMode::DRY_RUN) {
            report.files_consolidated++;
            report.bytes_reclaimed += group.file_size;
            utils::Logger::debug("[DRY-RUN] Would replace: " + dup.path + " -> " + group.canonical_file.path);
        } else {
            if (consolidate_file(group.canonical_file.path, dup.path)) {
                report.files_consolidated++;
                report.bytes_reclaimed += group.file_size;
                stats.actually_reclaimed_bytes += group.file_size;
                utils::Logger::debug("[OPTIMIZED] Replaced: " + dup.path + " -> " + group.canonical_file.path);
            } else {
                report.files_failed++;
            }
        }
    }

    return report;
}

OptimizationReport StorageOptimizer::optimize_all(const std::vector<DuplicateGroup>& groups, DedupStats& stats) {
    OptimizationReport total_report;

    for (const auto& group : groups) {
        OptimizationReport rep = optimize_group(group, stats);
        total_report.groups_processed += rep.groups_processed;
        total_report.files_consolidated += rep.files_consolidated;
        total_report.files_failed += rep.files_failed;
        total_report.cross_device_skipped += rep.cross_device_skipped;
        total_report.bytes_reclaimed += rep.bytes_reclaimed;
    }

    return total_report;
}

} // namespace core
} // namespace dedupfs
