#pragma once

#include "core/types.hpp"
#include <string>
#include <vector>
#include <cstdint>

namespace dedupfs {
namespace core {

struct NaiveBenchmarkResult {
    uint64_t total_comparisons{0};
    double in_memory_time_s{0.0};
    double cold_disk_time_s{0.0};
    uintmax_t bytes_read{0};
    size_t files_evaluated{0};
};

struct FullHashBenchmarkResult {
    double hash_only_time_s{0.0};
    double total_time_s{0.0};
    double scan_time_s{0.0};
    uintmax_t bytes_read{0};
    double throughput_mbs{0.0};
    size_t duplicates_found{0};
    size_t files_evaluated{0};
};

struct DedupFSBenchmarkResult {
    double hash_only_time_s{0.0};
    double core_time_s{0.0};
    double total_time_s{0.0};
    double merkle_time_s{0.0};
    uintmax_t bytes_read{0};
    double throughput_mbs{0.0};
    size_t files_scanned{0};
    size_t pruned_files_count{0};
    size_t full_hash_count{0};
    size_t duplicates_count{0};
    uintmax_t reclaimed_bytes{0};
    std::string merkle_root;
    size_t duplicate_subtrees{0};
};

struct ScalabilityPoint {
    size_t file_count{0};
    double naive_seconds{0.0};
    double full_hash_seconds{0.0};
    double dedupfs_seconds{0.0};
    double speedup_factor{0.0};
};

struct BenchmarkSuiteResult {
    std::string dataset_path;
    size_t files_count{0};
    uintmax_t total_bytes{0};
    NaiveBenchmarkResult naive;
    FullHashBenchmarkResult full_hash;
    DedupFSBenchmarkResult dedupfs;
    double speedup_vs_naive_cold{0.0};
    double speedup_hash_phase{0.0};
    double speedup_core_vs_full{0.0};
    double speedup_total_vs_full{0.0};
    double disk_io_saved_percent{0.0};
    std::vector<ScalabilityPoint> scalability_projection;
};

/**
 * Native C++17 Benchmarking Engine
 * Evaluates algorithmic efficiency across:
 *   1. Naive O(N^2) Pairwise Byte Verifier
 *   2. Traditional Full SHA-256 Hashing (Single-pass linear scan)
 *   3. DedupFS Multi-Tier Engine (Tiers 1-3, Bloom Filter, Chained Hash Table, Heap, Merkle)
 *
 * Guarantees 100% apples-to-apples language and I/O fairness:
 * Compiled with g++ -O3, identical OpenSSL EVP streaming C API, and identical POSIX file buffers.
 */
class BenchmarkEngine {
public:
    explicit BenchmarkEngine(std::string target_dir, std::string output_json_path = "benchmarks/benchmark_results.json");

    BenchmarkSuiteResult run_full_benchmark();
    bool export_json(const std::string& path = "") const;
    void print_summary_table() const;

    const BenchmarkSuiteResult& results() const { return results_; }

private:
    NaiveBenchmarkResult run_naive_pairwise(const std::vector<FileInfo>& files);
    FullHashBenchmarkResult run_traditional_full_sha256(const std::vector<FileInfo>& files, double scan_time_s);
    DedupFSBenchmarkResult run_dedupfs_multitier();
    std::vector<ScalabilityPoint> compute_scalability_curve(double avg_file_size_kb);

    std::string target_dir_;
    std::string output_json_path_;
    BenchmarkSuiteResult results_;
};

} // namespace core
} // namespace dedupfs
