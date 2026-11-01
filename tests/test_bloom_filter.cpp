#include "ds/bloom_filter.hpp"
#include "ds/murmur3.hpp"
#include "utils/logger.hpp"

#include <cassert>
#include <iostream>
#include <vector>
#include <string>

namespace dedupfs {
namespace tests {

bool run_bloom_filter_tests() {
    utils::Logger::info("Running Bloom Filter Unit Tests...");

    // Test 1: Zero False Negatives (Invariant)
    const size_t num_keys = 5000;
    const double target_fpr = 0.01;
    ds::BloomFilter bf(num_keys, target_fpr);

    std::vector<Hash256> inserted_hashes;
    inserted_hashes.reserve(num_keys);

    for (size_t i = 0; i < num_keys; ++i) {
        std::string key_str = "test_key_item_" + std::to_string(i);
        Hash128 h128 = ds::MurmurHash3::hash128(key_str.data(), key_str.size(), 1234);
        Hash256 h256{};
        // pack h128 into h256
        for (size_t b = 0; b < 8; ++b) {
            h256.bytes[b] = static_cast<uint8_t>((h128.h1 >> (b * 8)) & 0xFF);
            h256.bytes[8 + b] = static_cast<uint8_t>((h128.h2 >> (b * 8)) & 0xFF);
        }
        bf.insert(h256);
        inserted_hashes.push_back(h256);
    }

    // Verify all inserted keys return true
    for (size_t i = 0; i < num_keys; ++i) {
        if (!bf.might_contain(inserted_hashes[i])) {
            utils::Logger::error("Bloom Filter failed Invariant TC-01: False negative detected!");
            return false;
        }
    }
    utils::Logger::success("TC-01 PASSED: Zero False Negatives (FN = 0) verified across 5,000 keys.");

    // Test 2: Empirical False Positive Rate Bound
    size_t fp_count = 0;
    const size_t unseen_queries = 20000;

    for (size_t i = 0; i < unseen_queries; ++i) {
        std::string unseen_key = "unseen_random_query_item_" + std::to_string(i + 100000);
        Hash128 h128 = ds::MurmurHash3::hash128(unseen_key.data(), unseen_key.size(), 9999);
        Hash256 h256{};
        for (size_t b = 0; b < 8; ++b) {
            h256.bytes[b] = static_cast<uint8_t>((h128.h1 >> (b * 8)) & 0xFF);
            h256.bytes[8 + b] = static_cast<uint8_t>((h128.h2 >> (b * 8)) & 0xFF);
        }

        if (bf.might_contain(h256)) {
            fp_count++;
            bf.record_false_positive();
        }
    }

    double empirical_fpr = static_cast<double>(fp_count) / static_cast<double>(unseen_queries);
    double theoretical_fpr = bf.theoretical_fpr();

    utils::Logger::info("Observed FPR: " + std::to_string(empirical_fpr * 100.0) + 
                        "% (Theoretical: " + std::to_string(theoretical_fpr * 100.0) + "%)");

    // Must be reasonably close to target FPR (allow statistical tolerance < 2.5 * target_fpr)
    if (empirical_fpr > (target_fpr * 2.5)) {
        utils::Logger::error("Bloom Filter failed TC-02: Empirical FPR exceeded acceptable bounds!");
        return false;
    }
    utils::Logger::success("TC-02 PASSED: Empirical FPR is within theoretical bounds.");

    // Test 3: Clear and Fill Ratio
    if (bf.fill_ratio() <= 0.0 || bf.fill_ratio() >= 1.0) {
        utils::Logger::error("Bloom Filter failed TC-03: Invalid fill ratio.");
        return false;
    }
    bf.clear();
    if (bf.fill_ratio() != 0.0) {
        utils::Logger::error("Bloom Filter failed TC-03: clear() did not reset bit array.");
        return false;
    }
    utils::Logger::success("TC-03 PASSED: Fill ratio and clear() verified.");

    return true;
}

} // namespace tests
} // namespace dedupfs
