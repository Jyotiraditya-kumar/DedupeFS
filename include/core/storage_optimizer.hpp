#pragma once

#include "core/types.hpp"
#include <string>
#include <vector>

namespace dedupfs {
namespace core {

enum class DedupMode {
    DRY_RUN,
    HARD_LINK
};

struct OptimizationReport {
    size_t groups_processed{0};
    size_t files_consolidated{0};
    size_t files_failed{0};
    size_t cross_device_skipped{0};
    uintmax_t bytes_reclaimed{0};
};

class StorageOptimizer {
public:
    explicit StorageOptimizer(DedupMode mode = DedupMode::DRY_RUN);

    // Consolidates duplicates in a group
    OptimizationReport optimize_group(const DuplicateGroup& group, DedupStats& stats);

    // Consolidates all groups
    OptimizationReport optimize_all(const std::vector<DuplicateGroup>& groups, DedupStats& stats);

    DedupMode mode() const { return mode_; }
    void set_mode(DedupMode mode) { mode_ = mode; }

private:
    bool consolidate_file(const std::string& canonical_path, const std::string& duplicate_path);

    DedupMode mode_{DedupMode::DRY_RUN};
};

} // namespace core
} // namespace dedupfs
