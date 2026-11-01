#pragma once

#include "core/types.hpp"
#include "core/storage_optimizer.hpp"
#include "ds/bloom_filter.hpp"
#include "ds/hash_table.hpp"

#include <string>
#include <vector>

namespace dedupfs {
namespace utils {

class Reporter {
public:
    // Generates both summary run report and file-level duplicate report
    static void generate_reports(
        const std::string& reports_dir,
        const std::string& target_dir,
        core::DedupMode mode,
        uintmax_t min_file_size,
        double bloom_target_fpr,
        const DedupStats& stats,
        const ds::BloomFilter& bloom_filter,
        const ds::FingerprintHashTable& hash_table,
        const std::vector<DuplicateGroup>& duplicate_groups,
        std::string& out_summary_path,
        std::string& out_duplicates_path
    );

private:
    static std::string get_datetime_stamp();
    static std::string get_formatted_time();
};

} // namespace utils
} // namespace dedupfs
