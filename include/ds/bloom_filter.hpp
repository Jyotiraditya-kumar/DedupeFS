#pragma once

#include "core/types.hpp"
#include <vector>
#include <cstdint>
#include <cstddef>
#include <cmath>
#include <string>

namespace dedupfs {
namespace ds {

struct BloomFilterTelemetry {
    size_t total_insertions{0};
    size_t total_queries{0};
    size_t true_negatives{0};
    size_t reported_positives{0};
    size_t false_positives{0};

    double empirical_fpr() const {
        size_t non_members = true_negatives + false_positives;
        if (non_members == 0) return 0.0;
        return static_cast<double>(false_positives) / static_cast<double>(non_members);
    }
};

class BloomFilter {
public:
    // Construct Bloom filter with expected capacity n and target false positive rate p (e.g. 0.01)
    BloomFilter(size_t expected_elements = 100000, double target_fpr = 0.01);

    // Construct with explicit bit count m and hash function count k
    BloomFilter(size_t num_bits, size_t num_hashes, bool is_explicit);

    // Insert fingerprints
    void insert(const Hash256& hash);
    void insert(const Hash128& hash);
    void insert(const void* data, size_t len);

    // Query membership
    // Returns FALSE: definitely not present (0 false negatives)
    // Returns TRUE: probably present (subject to FPR)
    bool might_contain(const Hash256& hash);
    bool might_contain(const Hash128& hash);
    bool might_contain(const void* data, size_t len);

    // Record an empirical false positive observation (when verified against secondary index)
    void record_false_positive();

    // Reset filter
    void clear();

    // Accessors & Diagnostics
    size_t num_bits() const { return num_bits_; }
    size_t num_hashes() const { return num_hashes_; }
    size_t capacity() const { return expected_elements_; }
    double target_fpr() const { return target_fpr_; }

    double theoretical_fpr() const;
    double fill_ratio() const; // Fraction of bits set to 1
    size_t memory_bytes() const;

    const BloomFilterTelemetry& telemetry() const { return telemetry_; }

    // Static math utilities
    static size_t calculate_optimal_m(size_t n, double p);
    static size_t calculate_optimal_k(size_t m, size_t n);

private:
    std::pair<uint64_t, uint64_t> get_seeds(const Hash256& hash) const;
    std::pair<uint64_t, uint64_t> get_seeds(const Hash128& hash) const;
    std::pair<uint64_t, uint64_t> get_seeds(const void* data, size_t len) const;

    void set_bit(size_t bit_index);
    bool test_bit(size_t bit_index) const;

    size_t expected_elements_{100000};
    double target_fpr_{0.01};
    size_t num_bits_{0};
    size_t num_hashes_{0};

    std::vector<uint64_t> bit_array_;
    BloomFilterTelemetry telemetry_;
};

} // namespace ds
} // namespace dedupfs
