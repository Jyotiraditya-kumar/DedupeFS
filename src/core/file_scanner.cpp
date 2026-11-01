#include "core/file_scanner.hpp"
#include "utils/logger.hpp"
#include <filesystem>
#include <sys/stat.h>
#include <unistd.h>

namespace fs = std::filesystem;

namespace dedupfs {
namespace core {

FileScanner::FileScanner(ScannerOptions options)
    : options_(std::move(options)) {}

uint64_t FileScanner::make_inode_key(dev_t dev, ino_t ino) const {
    // 64-bit combination of device and inode
    uint64_t d = static_cast<uint64_t>(dev);
    uint64_t i = static_cast<uint64_t>(ino);
    return (d << 32) ^ i ^ 0x9e3779b97f4a7c15ULL;
}

bool FileScanner::is_excluded(const std::string& path) const {
    for (const auto& excl : options_.exclude_dirs) {
        if (path.find(excl) != std::string::npos) {
            return true;
        }
    }
    return false;
}

SizeBucketMap FileScanner::scan_directory(const std::string& root_path, DedupStats& stats) {
    SizeBucketMap raw_size_map;
    visited_inodes_.clear();

    std::error_code ec;
    if (!fs::exists(root_path, ec) || !fs::is_directory(root_path, ec)) {
        utils::Logger::error("Scan path does not exist or is not a directory: " + root_path);
        return {};
    }

    auto dir_options = fs::directory_options::skip_permission_denied;
    if (options_.follow_symlinks) {
        dir_options |= fs::directory_options::follow_directory_symlink;
    }

    fs::recursive_directory_iterator it(root_path, dir_options, ec);
    fs::recursive_directory_iterator end;

    while (it != end) {
        if (ec) {
            utils::Logger::debug("Skipping inaccessible entry: " + ec.message());
            it.increment(ec);
            continue;
        }

        const auto& entry = *it;
        std::string current_path = entry.path().string();

        if (is_excluded(current_path)) {
            it.disable_recursion_pending();
            it.increment(ec);
            continue;
        }

        if (entry.is_directory(ec)) {
            stats.total_dirs_scanned++;
            it.increment(ec);
            continue;
        }

        if (entry.is_regular_file(ec)) {
            struct stat st;
            int stat_res = options_.follow_symlinks ? stat(current_path.c_str(), &st) : lstat(current_path.c_str(), &st);

            if (stat_res == 0) {
                // If it's a symlink and we are not following symlinks, skip
                if (S_ISLNK(st.st_mode) && !options_.follow_symlinks) {
                    it.increment(ec);
                    continue;
                }

                uintmax_t file_size = static_cast<uintmax_t>(st.st_size);

                // Track global scanned counts
                stats.total_files_scanned++;
                stats.total_bytes_scanned += file_size;

                // Check size bounds
                if (file_size < options_.min_file_size || file_size > options_.max_file_size) {
                    it.increment(ec);
                    continue;
                }

                // Inode cycle & existing hard-link detection
                uint64_t inode_key = make_inode_key(st.st_dev, st.st_ino);
                if (st.st_nlink > 1 && visited_inodes_.find(inode_key) != visited_inodes_.end()) {
                    utils::Logger::debug("File already hard-linked, skipping: " + current_path);
                    it.increment(ec);
                    continue;
                }
                visited_inodes_.insert(inode_key);

                FileInfo info;
                info.path = current_path;
                info.size = file_size;
                info.inode = st.st_ino;
                info.device = st.st_dev;
                info.mtime = st.st_mtime;
                info.nlink = st.st_nlink;

                raw_size_map[file_size].push_back(std::move(info));
            }
        }

        it.increment(ec);
    }

    // Tier 1 Elimination: Filter out files with unique sizes
    SizeBucketMap candidate_map;
    for (auto& [size, file_list] : raw_size_map) {
        if (file_list.size() > 1) {
            candidate_map[size] = std::move(file_list);
        } else {
            stats.unique_size_files_skipped += file_list.size();
        }
    }

    return candidate_map;
}

} // namespace core
} // namespace dedupfs
