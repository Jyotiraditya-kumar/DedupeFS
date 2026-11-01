#include "core/pipeline.hpp"
#include "utils/logger.hpp"
#include "utils/metrics.hpp"
#include "utils/reporter.hpp"

#include <iostream>
#include <iomanip>
#include <unordered_map>
#include <filesystem>

namespace dedupfs {
namespace core {

DedupPipeline::DedupPipeline(PipelineConfig config)
    : config_(std::move(config)),
      bloom_filter_(100000, config.bloom_target_fpr),
      hash_table_(config.hash_table_initial_buckets, 0.75) {
    utils::Logger::set_verbose(config_.verbose);
}

void DedupPipeline::process_size_bucket(uintmax_t /*size*/, std::vector<FileInfo>& files) {
    // Tier 2: Group by 4KB prefix hash
    std::unordered_map<Hash128, std::vector<FileInfo>> prefix_map;

    for (auto& file : files) {
        stats_.prefix_hash_evaluated++;
        if (HashEngine::compute_prefix_hash(file)) {
            prefix_map[file.prefix_hash].push_back(std::move(file));
        }
    }

    // Process clusters that share the exact same prefix hash
    for (auto& [prefix_hash, candidate_files] : prefix_map) {
        if (candidate_files.size() < 2) {
            stats_.prefix_hash_mismatches += candidate_files.size();
            continue; // Mismatch in first 4KB: unique files!
        }

        // Tier 3: Compute Full Cryptographic SHA-256
        for (auto& file : candidate_files) {
            stats_.full_hash_evaluated++;
            if (!HashEngine::compute_full_sha256(file)) {
                continue;
            }

            // Bloom Filter Fast Existence Check
            stats_.bloom_filter_queries++;
            bool might_exist = bloom_filter_.might_contain(file.full_hash);

            if (!might_exist) {
                // Guaranteed unique so far: Insert into Bloom Filter & Primary Hash Table
                stats_.bloom_filter_negatives++;
                bloom_filter_.insert(file.full_hash);

                bool is_dup = false;
                hash_table_.insert(file.full_hash, file, is_dup);
            } else {
                // Potential duplicate: Query Primary Hash Table
                stats_.bloom_filter_positives++;
                auto* entry = hash_table_.find(file.full_hash);

                if (entry != nullptr) {
                    // Candidate duplicate found in table!
                    // Verify byte-by-byte to guarantee zero hash collision risk
                    bool identical = ByteVerifier::verify_identical(entry->files.front(), file, stats_);
                    if (identical) {
                        entry->files.push_back(file);
                    } else {
                        // Rare SHA-256 collision or file changed during run
                        utils::Logger::warning("Hash matched but byte verifier rejected: " + file.path);
                    }
                } else {
                    // Bloom filter false positive! (BF returned true, but key not in hash table)
                    stats_.bloom_filter_false_positives++;
                    bloom_filter_.record_false_positive();

                    // Insert key into hash table
                    bool is_dup = false;
                    hash_table_.insert(file.full_hash, file, is_dup);
                }
            }
        }
    }
}

DedupStats DedupPipeline::run() {
    utils::Timer total_timer;
    utils::Logger::header("DEDUPFS PIPELINE INITIALIZATION");
    utils::Logger::info("Target Directory: " + config_.root_path);
    utils::Logger::info("Execution Mode:   " + std::string(config_.mode == DedupMode::DRY_RUN ? "DRY-RUN (Audit only)" : "OPTIMIZE (Hard-link consolidation)"));
    utils::Logger::info("Bloom Target FPR: " + std::to_string(config_.bloom_target_fpr * 100.0) + "%");

    // Step 1: Directory Scanning & Size Filtering
    utils::Logger::info("Scanning directory and building size buckets...");
    utils::Timer scan_timer;
    ScannerOptions scan_opts;
    scan_opts.min_file_size = config_.min_file_size;
    FileScanner scanner(scan_opts);

    SizeBucketMap candidate_map = scanner.scan_directory(config_.root_path, stats_);
    stats_.scan_time_ms = scan_timer.elapsed_ms();
    utils::Logger::success("Directory scan complete in " + utils::Logger::format_time_ms(stats_.scan_time_ms));
    utils::Logger::info("Total files found: " + std::to_string(stats_.total_files_scanned) + 
                        " (" + utils::Logger::format_bytes(stats_.total_bytes_scanned) + ")");
    utils::Logger::info("Files with unique size discarded immediately: " + std::to_string(stats_.unique_size_files_skipped));
    utils::Logger::info("Candidate size buckets to investigate: " + std::to_string(candidate_map.size()));

    // Step 2: Multi-Tier Hashing & Bloom Filter Indexing
    utils::Logger::info("Executing multi-tier hashing and Bloom filter deduplication...");
    utils::Timer hash_timer;

    for (auto& [size, file_list] : candidate_map) {
        process_size_bucket(size, file_list);
    }
    stats_.hash_time_ms = hash_timer.elapsed_ms();
    utils::Logger::success("Fingerprint indexing complete in " + utils::Logger::format_time_ms(stats_.hash_time_ms));

    // Step 3: Extract Verified Duplicate Groups
    duplicate_groups_ = hash_table_.get_duplicate_groups();
    stats_.duplicate_groups_count = duplicate_groups_.size();

    size_t total_dup_files = 0;
    uintmax_t total_dup_bytes = 0;
    for (const auto& group : duplicate_groups_) {
        total_dup_files += group.duplicates.size();
        total_dup_bytes += group.total_wasted_bytes();

        // Categorize duplicate space savings by extension and subfolder
        for (const auto& dup : group.duplicates) {
            std::string ext = std::filesystem::path(dup.path).extension().string();
            for (char& c : ext) c = static_cast<char>(std::tolower(c));
            if (ext.empty()) ext = "(no ext)";
            stats_.file_type_metrics[ext].duplicate_count++;
            stats_.file_type_metrics[ext].wasted_bytes += group.file_size;

            std::string rel_path;
            try {
                rel_path = std::filesystem::relative(dup.path, config_.root_path).string();
            } catch (...) {
                rel_path = dup.path;
            }
            auto slash_pos = rel_path.find('/');
            std::string folder = (slash_pos != std::string::npos) ? rel_path.substr(0, slash_pos) : "(root)";
            stats_.subfolder_metrics[folder].duplicate_count++;
            stats_.subfolder_metrics[folder].wasted_bytes += group.file_size;
        }
    }
    stats_.duplicate_files_count = total_dup_files;
    stats_.potential_reclaimed_bytes = total_dup_bytes;

    // Step 4: Storage Optimization
    utils::Logger::info("Running Storage Optimizer...");
    utils::Timer dedup_timer;
    StorageOptimizer optimizer(config_.mode);
    (void)optimizer.optimize_all(duplicate_groups_, stats_);
    stats_.dedup_time_ms = dedup_timer.elapsed_ms();

    stats_.total_time_ms = total_timer.elapsed_ms();
    utils::Logger::success("Deduplication run finished in " + utils::Logger::format_time_ms(stats_.total_time_ms));

    // Step 5: Generate Run Report and File-Level Duplicate Report
    if (config_.enable_reports) {
        utils::Reporter::generate_reports(
            config_.reports_dir,
            config_.root_path,
            config_.mode,
            config_.min_file_size,
            config_.bloom_target_fpr,
            stats_,
            bloom_filter_,
            hash_table_,
            duplicate_groups_,
            summary_report_path_,
            duplicate_report_path_
        );
        utils::Logger::info("Summary report generated: " + summary_report_path_);
        utils::Logger::info("File-level duplicate report: " + duplicate_report_path_);
    }

    return stats_;
}

void DedupPipeline::print_report() const {
    utils::Logger::header("DEDUPFS EXECUTION REPORT & TELEMETRY");

    std::cout << std::left;
    std::cout << "\n--- SCANNING & I/O SAVINGS ---\n";
    std::cout << std::setw(38) << "Total Files Scanned:" << stats_.total_files_scanned << "\n";
    std::cout << std::setw(38) << "Total Raw Data Scanned:" << utils::Logger::format_bytes(stats_.total_bytes_scanned) << "\n";
    std::cout << std::setw(38) << "Unique Size Files Discarded (Tier 1):" << stats_.unique_size_files_skipped;
    if (stats_.total_files_scanned > 0) {
        double pct = (static_cast<double>(stats_.unique_size_files_skipped) / stats_.total_files_scanned) * 100.0;
        std::cout << " (" << std::fixed << std::setprecision(1) << pct << "%)";
    }
    std::cout << "\n";
    std::cout << std::setw(38) << "4KB Prefix Hashes Evaluated (Tier 2):" << stats_.prefix_hash_evaluated << "\n";
    std::cout << std::setw(38) << "Prefix Mismatches Discarded:" << stats_.prefix_hash_mismatches << "\n";
    std::cout << std::setw(38) << "Full SHA-256 Hashes Computed (Tier 3):" << stats_.full_hash_evaluated << "\n";

    std::cout << "\n--- PROBABILISTIC BLOOM FILTER TELEMETRY ---\n";
    std::cout << std::setw(38) << "Bloom Filter Total Bits (m):" << bloom_filter_.num_bits() 
              << " (" << utils::Logger::format_bytes(bloom_filter_.memory_bytes()) << ")\n";
    std::cout << std::setw(38) << "Hash Functions Count (k):" << bloom_filter_.num_hashes() << "\n";
    std::cout << std::setw(38) << "Bloom Filter Fill Ratio (1-bits):" 
              << std::fixed << std::setprecision(2) << (bloom_filter_.fill_ratio() * 100.0) << "%\n";
    std::cout << std::setw(38) << "Total Membership Queries:" << stats_.bloom_filter_queries << "\n";
    std::cout << std::setw(38) << "True Negative Rejections (O(k)):" << stats_.bloom_filter_negatives << "\n";
    std::cout << std::setw(38) << "Reported Positives (Lookups):" << stats_.bloom_filter_positives << "\n";
    std::cout << std::setw(38) << "Observed False Positives:" << stats_.bloom_filter_false_positives << "\n";
    std::cout << std::setw(38) << "Theoretical False Positive Rate:" 
              << std::scientific << bloom_filter_.theoretical_fpr() << std::defaultfloat << "\n";
    std::cout << std::setw(38) << "Empirical False Positive Rate:" 
              << std::scientific << bloom_filter_.telemetry().empirical_fpr() << std::defaultfloat << "\n";

    std::cout << "\n--- PRIMARY HASH TABLE DIAGNOSTICS ---\n";
    auto ht_diag = hash_table_.get_diagnostics();
    std::cout << std::setw(38) << "Primary Index Elements:" << ht_diag.total_elements << "\n";
    std::cout << std::setw(38) << "Allocated Buckets:" << ht_diag.bucket_count << "\n";
    std::cout << std::setw(38) << "Current Load Factor:" << std::fixed << std::setprecision(3) << ht_diag.load_factor << "\n";
    std::cout << std::setw(38) << "Rehash Expansions:" << ht_diag.rehash_count << "\n";
    std::cout << std::setw(38) << "Collisions in Buckets:" << ht_diag.collisions << "\n";
    std::cout << std::setw(38) << "Max Bucket Chain Length:" << ht_diag.max_chain_length << "\n";
    std::cout << std::setw(38) << "Avg Non-Empty Chain Length:" << std::fixed << std::setprecision(2) << ht_diag.avg_non_empty_chain_length << "\n";

    std::cout << "\n--- VERIFICATION & DEDUPLICATION RESULTS ---\n";
    std::cout << std::setw(38) << "Byte Verifications Performed:" << stats_.byte_verifications_performed << "\n";
    std::cout << std::setw(38) << "Byte-by-Byte Confirmed Matches:" << stats_.byte_verifications_matched << "\n";
    std::cout << std::setw(38) << "Duplicate Equivalence Classes:" << stats_.duplicate_groups_count << "\n";
    std::cout << std::setw(38) << "Redundant Duplicate Files:" << stats_.duplicate_files_count << "\n";
    std::cout << std::setw(38) << "Storage Savings Potential:" << utils::Logger::format_bytes(stats_.potential_reclaimed_bytes) << "\n";

    if (config_.mode == DedupMode::HARD_LINK) {
        std::cout << std::setw(38) << "Actually Reclaimed Physical Storage:" 
                  << utils::Logger::format_bytes(stats_.actually_reclaimed_bytes) << "\n";
    }

    if (stats_.total_bytes_scanned > 0 && stats_.potential_reclaimed_bytes > 0) {
        uintmax_t post_dedup_bytes = stats_.total_bytes_scanned - stats_.potential_reclaimed_bytes;
        double dedup_ratio = static_cast<double>(stats_.total_bytes_scanned) / static_cast<double>(post_dedup_bytes);
        double space_saved_pct = (1.0 - (1.0 / dedup_ratio)) * 100.0;
        std::cout << std::setw(38) << "Deduplication Ratio (DR):" << std::fixed << std::setprecision(2) << dedup_ratio << "x\n";
        std::cout << std::setw(38) << "Space Savings Percentage:" << std::fixed << std::setprecision(2) << space_saved_pct << "%\n";
    }

    std::cout << "\n--- EXECUTION TIMING & THROUGHPUT ---\n";
    std::cout << std::setw(38) << "Scan Time:" << utils::Logger::format_time_ms(stats_.scan_time_ms) << "\n";
    std::cout << std::setw(38) << "Hash & Index Time:" << utils::Logger::format_time_ms(stats_.hash_time_ms) << "\n";
    std::cout << std::setw(38) << "Optimization Time:" << utils::Logger::format_time_ms(stats_.dedup_time_ms) << "\n";
    std::cout << std::setw(38) << "Total Runtime:" << utils::Logger::format_time_ms(stats_.total_time_ms) << "\n";

    if (stats_.total_time_ms > 0.0) {
        double throughput_mbs = (static_cast<double>(stats_.total_bytes_scanned) / (1024.0 * 1024.0)) / (stats_.total_time_ms / 1000.0);
        std::cout << std::setw(38) << "Overall Throughput:" << std::fixed << std::setprecision(2) << throughput_mbs << " MB/s\n";
    }

    uintmax_t peak_ram = utils::MemoryProfiler::get_peak_rss_bytes();
    if (peak_ram > 0) {
        std::cout << std::setw(38) << "Peak Process Memory (RSS):" << utils::Logger::format_bytes(peak_ram) << "\n";
    }

    std::cout << "\n";
}

} // namespace core
} // namespace dedupfs
