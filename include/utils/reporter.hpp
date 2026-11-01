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
    // Generates academic summary report, file-level duplicate report, HTML interactive report, and JSON telemetry
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
    static std::string render_ascii_bar(double pct, int width = 24);
    static void generate_html_report(
        const std::string& html_path,
        const std::string& target_dir,
        const std::string& mode_str,
        const std::string& time_str,
        double bloom_target_fpr,
        uintmax_t min_file_size,
        const DedupStats& stats,
        const ds::BloomFilter& bloom_filter,
        const ds::HashTableDiagnostics& ht_diag,
        const std::vector<DuplicateGroup>& duplicate_groups
    );
    static void generate_json_report(
        const std::string& json_path,
        const std::string& target_dir,
        const std::string& mode_str,
        const std::string& time_str,
        double bloom_target_fpr,
        uintmax_t min_file_size,
        const DedupStats& stats,
        const ds::BloomFilter& bloom_filter,
        const ds::HashTableDiagnostics& ht_diag,
        const std::vector<DuplicateGroup>& duplicate_groups
    );
};

} // namespace utils
} // namespace dedupfs
