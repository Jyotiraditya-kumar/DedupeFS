#include "utils/reporter.hpp"
#include "utils/logger.hpp"
#include "utils/metrics.hpp"

#include <chrono>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <algorithm>

namespace dedupfs {
namespace utils {

std::string Reporter::get_datetime_stamp() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm_buf;
    localtime_r(&t, &tm_buf);

    char buf[64];
    std::strftime(buf, sizeof(buf), "%Y%m%d_%H%M%S", &tm_buf);
    return std::string(buf);
}

std::string Reporter::get_formatted_time() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm_buf;
    localtime_r(&t, &tm_buf);

    char buf[64];
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &tm_buf);
    return std::string(buf);
}

void Reporter::generate_reports(
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
) {
    std::filesystem::create_directories(reports_dir);
    std::string ts = get_datetime_stamp();
    std::string time_str = get_formatted_time();

    out_summary_path = (std::filesystem::path(reports_dir) / ("report_" + ts + ".txt")).string();
    out_duplicates_path = (std::filesystem::path(reports_dir) / ("duplicates_" + ts + ".txt")).string();

    std::string mode_str = (mode == core::DedupMode::HARD_LINK) ? "OPTIMIZE (POSIX Hard-Link Consolidation)" : "DRY-RUN (Non-Destructive Audit)";

    // ------------------------------------------------------------------
    // 1. Generate Summary Run Report
    // ------------------------------------------------------------------
    {
        std::ofstream ofs(out_summary_path);
        if (ofs.is_open()) {
            ofs << "================================================================================\n"
                << "                     DEDUPFS STORAGE EXECUTION REPORT\n"
                << "            High-Performance Deduplication Engine (M.Tech Sem 1)\n"
                << "================================================================================\n"
                << "Execution Timestamp:    " << time_str << "\n"
                << "Target Directory:       " << target_dir << "\n"
                << "Execution Mode:         " << mode_str << "\n"
                << "Bloom Filter Target FPR:" << std::fixed << std::setprecision(4) << (bloom_target_fpr * 100.0) << "%\n"
                << "Minimum File Size:      " << Logger::format_bytes(min_file_size) << " (" << min_file_size << " bytes)\n"
                << "--------------------------------------------------------------------------------\n\n";

            ofs << "1. SCANNING & TIER 1/2 I/O SAVINGS\n"
                << "--------------------------------------------------------------------------------\n"
                << std::left << std::setw(42) << "Total Files Scanned:" << stats.total_files_scanned << "\n"
                << std::setw(42) << "Total Raw Data Scanned:" << Logger::format_bytes(stats.total_bytes_scanned) << " (" << stats.total_bytes_scanned << " bytes)\n"
                << std::setw(42) << "Unique Size Files Discarded (Tier 1):" << stats.unique_size_files_skipped;
            if (stats.total_files_scanned > 0) {
                double pct = (static_cast<double>(stats.unique_size_files_skipped) / stats.total_files_scanned) * 100.0;
                ofs << " (" << std::fixed << std::setprecision(1) << pct << "%)";
            }
            ofs << "\n"
                << std::setw(42) << "4KB Prefix Hashes Evaluated (Tier 2):" << stats.prefix_hash_evaluated << "\n"
                << std::setw(42) << "Prefix Mismatches Discarded:" << stats.prefix_hash_mismatches << "\n"
                << std::setw(42) << "Full SHA-256 Hashes Computed (Tier 3):" << stats.full_hash_evaluated << "\n\n";

            ofs << "2. PROBABILISTIC BLOOM FILTER TELEMETRY\n"
                << "--------------------------------------------------------------------------------\n"
                << std::setw(42) << "Bloom Filter Total Bits (m):" << bloom_filter.num_bits() 
                << " (" << Logger::format_bytes(bloom_filter.memory_bytes()) << ")\n"
                << std::setw(42) << "Optimal Hash Functions Count (k):" << bloom_filter.num_hashes() << "\n"
                << std::setw(42) << "Bloom Filter Fill Ratio (1-bits):" 
                << std::fixed << std::setprecision(2) << (bloom_filter.fill_ratio() * 100.0) << "%\n"
                << std::setw(42) << "Total Membership Queries:" << stats.bloom_filter_queries << "\n"
                << std::setw(42) << "True Negative Rejections (O(k)):" << stats.bloom_filter_negatives << "\n"
                << std::setw(42) << "Reported Positives (Hash Lookups):" << stats.bloom_filter_positives << "\n"
                << std::setw(42) << "Observed False Positives:" << stats.bloom_filter_false_positives << "\n"
                << std::setw(42) << "Theoretical False Positive Rate:" << std::scientific << bloom_filter.theoretical_fpr() << std::defaultfloat << "\n"
                << std::setw(42) << "Empirical False Positive Rate:" << std::scientific << bloom_filter.telemetry().empirical_fpr() << std::defaultfloat << "\n\n";

            auto ht_diag = hash_table.get_diagnostics();
            ofs << "3. PRIMARY HASH TABLE INVERTED INDEX DIAGNOSTICS\n"
                << "--------------------------------------------------------------------------------\n"
                << std::setw(42) << "Primary Index Stored Elements:" << ht_diag.total_elements << "\n"
                << std::setw(42) << "Allocated Power-of-Two Buckets:" << ht_diag.bucket_count << "\n"
                << std::setw(42) << "Current Load Factor (lambda):" << std::fixed << std::setprecision(3) << ht_diag.load_factor << "\n"
                << std::setw(42) << "Dynamic Rehash Expansions:" << ht_diag.rehash_count << "\n"
                << std::setw(42) << "Bucket Hash Collisions Resolved:" << ht_diag.collisions << "\n"
                << std::setw(42) << "Max Collision Chain Depth:" << ht_diag.max_chain_length << "\n"
                << std::setw(42) << "Avg Non-Empty Chain Length:" << std::fixed << std::setprecision(2) << ht_diag.avg_non_empty_chain_length << "\n\n";

            ofs << "4. BYTE VERIFICATION & STORAGE DEDUPLICATION RESULTS\n"
                << "--------------------------------------------------------------------------------\n"
                << std::setw(42) << "Byte Verifications Performed:" << stats.byte_verifications_performed << "\n"
                << std::setw(42) << "Byte-by-Byte Confirmed Matches:" << stats.byte_verifications_matched << "\n"
                << std::setw(42) << "Duplicate Equivalence Classes:" << stats.duplicate_groups_count << "\n"
                << std::setw(42) << "Redundant Duplicate Files:" << stats.duplicate_files_count << "\n"
                << std::setw(42) << "Storage Savings Potential:" << Logger::format_bytes(stats.potential_reclaimed_bytes) << "\n";

            if (mode == core::DedupMode::HARD_LINK) {
                ofs << std::setw(42) << "Actually Reclaimed Physical Storage:" 
                    << Logger::format_bytes(stats.actually_reclaimed_bytes) << "\n";
            }

            if (stats.total_bytes_scanned > 0 && stats.potential_reclaimed_bytes > 0) {
                uintmax_t post_dedup_bytes = stats.total_bytes_scanned - stats.potential_reclaimed_bytes;
                double dedup_ratio = static_cast<double>(stats.total_bytes_scanned) / static_cast<double>(post_dedup_bytes);
                double space_saved_pct = (1.0 - (1.0 / dedup_ratio)) * 100.0;
                ofs << std::setw(42) << "Deduplication Ratio (DR):" << std::fixed << std::setprecision(2) << dedup_ratio << "x\n"
                    << std::setw(42) << "Physical Space Savings Percentage:" << std::fixed << std::setprecision(2) << space_saved_pct << "%\n";
            }
            ofs << "\n";

            ofs << "5. EXECUTION LATENCY & THROUGHPUT TELEMETRY\n"
                << "--------------------------------------------------------------------------------\n"
                << std::setw(42) << "Directory Scan Latency:" << Logger::format_time_ms(stats.scan_time_ms) << "\n"
                << std::setw(42) << "Hash, Bloom & Index Latency:" << Logger::format_time_ms(stats.hash_time_ms) << "\n"
                << std::setw(42) << "Storage Optimization Latency:" << Logger::format_time_ms(stats.dedup_time_ms) << "\n"
                << std::setw(42) << "End-to-End Total Runtime:" << Logger::format_time_ms(stats.total_time_ms) << "\n";

            if (stats.total_time_ms > 0.0) {
                double throughput_mbs = (static_cast<double>(stats.total_bytes_scanned) / (1024.0 * 1024.0)) / (stats.total_time_ms / 1000.0);
                ofs << std::setw(42) << "Overall Processing Throughput:" << std::fixed << std::setprecision(2) << throughput_mbs << " MB/s\n";
            }

            uintmax_t peak_ram = MemoryProfiler::get_peak_rss_bytes();
            if (peak_ram > 0) {
                ofs << std::setw(42) << "Peak Process Memory (RSS):" << Logger::format_bytes(peak_ram) << "\n";
            }
            ofs << "\n"
                << "Associated File-Level Duplicate Report: " << out_duplicates_path << "\n"
                << "================================================================================\n";
        }
    }

    // Copy to report_latest.txt
    {
        std::string latest_summary = (std::filesystem::path(reports_dir) / "report_latest.txt").string();
        std::error_code ec;
        std::filesystem::copy_file(out_summary_path, latest_summary, std::filesystem::copy_options::overwrite_existing, ec);
    }

    // ------------------------------------------------------------------
    // 2. Generate Separate File-Level Duplicate Report
    // ------------------------------------------------------------------
    {
        std::ofstream ofs(out_duplicates_path);
        if (ofs.is_open()) {
            ofs << "================================================================================\n"
                << "                DEDUPFS FILE-LEVEL DUPLICATE REPORT & AUDIT\n"
                << "            Detailed Equivalence Groups and Duplicate Paths Mapping\n"
                << "================================================================================\n"
                << "Execution Timestamp:    " << time_str << "\n"
                << "Target Directory:       " << target_dir << "\n"
                << "Execution Mode:         " << mode_str << "\n"
                << "Total Duplicate Groups: " << duplicate_groups.size() << "\n"
                << "Total Redundant Files:  " << stats.duplicate_files_count << "\n"
                << "Total Wasted Storage:   " << Logger::format_bytes(stats.potential_reclaimed_bytes) << " (" << stats.potential_reclaimed_bytes << " bytes)\n"
                << "================================================================================\n\n";

            if (duplicate_groups.empty()) {
                ofs << "[STATUS: NO DUPLICATE FILES DETECTED]\n\n"
                    << "Every scanned file in the target directory contains distinct, unique content.\n"
                    << "No redundant physical disk space is currently occupied.\n";
            } else {
                // Sort duplicate groups by wasted bytes descending
                auto sorted_groups = duplicate_groups;
                std::sort(sorted_groups.begin(), sorted_groups.end(), [](const DuplicateGroup& a, const DuplicateGroup& b) {
                    return a.total_wasted_bytes() > b.total_wasted_bytes();
                });

                size_t group_idx = 1;
                for (const auto& group : sorted_groups) {
                    ofs << "--------------------------------------------------------------------------------\n"
                        << "DUPLICATE GROUP #" << group_idx++ << "\n"
                        << "--------------------------------------------------------------------------------\n"
                        << "  SHA-256 Fingerprint: " << group.canonical_file.full_hash.to_hex() << "\n"
                        << "  4KB Prefix Murmur3:  " << group.canonical_file.prefix_hash.to_hex() << "\n"
                        << "  File Size:           " << Logger::format_bytes(group.file_size) << " (" << group.file_size << " bytes)\n"
                        << "  Cluster Cardinality: " << (group.duplicates.size() + 1) << " files (1 original + " << group.duplicates.size() << " redundant)\n"
                        << "  Wasted Storage:      " << Logger::format_bytes(group.total_wasted_bytes()) << "\n"
                        << "  Members:\n";

                    // Original file
                    ofs << "    [ORIGINAL]  " << group.canonical_file.path 
                        << " (inode: " << group.canonical_file.inode << ", links: " << group.canonical_file.nlink << ")\n";

                    // Duplicates
                    size_t dup_i = 1;
                    for (const auto& dup : group.duplicates) {
                        std::string status = (mode == core::DedupMode::HARD_LINK) ? "[CONSOLIDATED]" : "[AUDITED]";
                        ofs << "    [DUP #" << dup_i++ << "]    " << dup.path 
                            << " (inode: " << dup.inode << ", links: " << dup.nlink << ") " << status << "\n";
                    }
                    ofs << "\n";
                }

                ofs << "================================================================================\n"
                    << "                             END OF DUPLICATE REPORT\n"
                    << "================================================================================\n";
            }
        }
    }

    // Copy to duplicates_latest.txt
    {
        std::string latest_dups = (std::filesystem::path(reports_dir) / "duplicates_latest.txt").string();
        std::error_code ec;
        std::filesystem::copy_file(out_duplicates_path, latest_dups, std::filesystem::copy_options::overwrite_existing, ec);
    }
}

} // namespace utils
} // namespace dedupfs
