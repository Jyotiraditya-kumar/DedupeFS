#pragma once

#include "core/types.hpp"
#include "core/file_scanner.hpp"
#include "core/hash_engine.hpp"
#include "core/byte_verifier.hpp"
#include "core/storage_optimizer.hpp"
#include "ds/bloom_filter.hpp"
#include "ds/hash_table.hpp"

#include <string>
#include <vector>

namespace dedupfs {
namespace core {

struct PipelineConfig {
    std::string root_path;
    DedupMode mode{DedupMode::DRY_RUN};
    bool verbose{false};
    uintmax_t min_file_size{1};
    double bloom_target_fpr{0.01};
    size_t hash_table_initial_buckets{4096};
    std::string reports_dir{"reports"};
    bool enable_reports{true};
};

class DedupPipeline {
public:
    explicit DedupPipeline(PipelineConfig config);

    // Executes the complete multi-tier deduplication workflow
    DedupStats run();

    // Accessors
    const DedupStats& stats() const { return stats_; }
    const ds::BloomFilter& bloom_filter() const { return bloom_filter_; }
    const ds::FingerprintHashTable& hash_table() const { return hash_table_; }
    const std::vector<DuplicateGroup>& duplicate_groups() const { return duplicate_groups_; }
    const std::string& summary_report_path() const { return summary_report_path_; }
    const std::string& duplicate_report_path() const { return duplicate_report_path_; }

    // Print formatted summary report
    void print_report() const;

private:
    void process_size_bucket(uintmax_t size, std::vector<FileInfo>& files);

    PipelineConfig config_;
    DedupStats stats_;
    ds::BloomFilter bloom_filter_;
    ds::FingerprintHashTable hash_table_;
    std::vector<DuplicateGroup> duplicate_groups_;
    std::string summary_report_path_;
    std::string duplicate_report_path_;
};

} // namespace core
} // namespace dedupfs
