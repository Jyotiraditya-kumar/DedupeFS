#include "ds/bloom_filter.hpp"
#include "ds/murmur3.hpp"
#include <algorithm>
#include <stdexcept>

namespace dedupfs {
namespace ds {

size_t BloomFilter::calculate_optimal_m(size_t n, double p) {
    if (n == 0 || p <= 0.0 || p >= 1.0) {
        return 64;
    }
    double ln2 = std::log(2.0);
    double m = -static_cast<double>(n) * std::log(p) / (ln2 * ln2);
    size_t bits = static_cast<size_t>(std::ceil(m));
    return std::max<size_t>(bits, 64);
}

size_t BloomFilter::calculate_optimal_k(size_t m, size_t n) {
    if (n == 0) return 1;
    double ln2 = std::log(2.0);
    double k = (static_cast<double>(m) / static_cast<double>(n)) * ln2;
    size_t hashes = static_cast<size_t>(std::round(k));
    return std::max<size_t>(hashes, 1);
}

BloomFilter::BloomFilter(size_t expected_elements, double target_fpr)
    : expected_elements_(expected_elements), target_fpr_(target_fpr) {
    num_bits_ = calculate_optimal_m(expected_elements_, target_fpr_);
    num_hashes_ = calculate_optimal_k(num_bits_, expected_elements_);

    size_t words = (num_bits_ + 63) / 64;
    bit_array_.assign(words, 0);
}

BloomFilter::BloomFilter(size_t num_bits, size_t num_hashes, bool /*is_explicit*/)
    : num_bits_(std::max<size_t>(num_bits, 64)), num_hashes_(std::max<size_t>(num_hashes, 1)) {
    expected_elements_ = static_cast<size_t>(static_cast<double>(num_bits_) * std::log(2.0) / static_cast<double>(num_hashes_));
    target_fpr_ = std::pow(0.5, static_cast<double>(num_hashes_));

    size_t words = (num_bits_ + 63) / 64;
    bit_array_.assign(words, 0);
}

void BloomFilter::set_bit(size_t bit_index) {
    bit_index %= num_bits_;
    bit_array_[bit_index / 64] |= (1ULL << (bit_index % 64));
}

bool BloomFilter::test_bit(size_t bit_index) const {
    bit_index %= num_bits_;
    return (bit_array_[bit_index / 64] & (1ULL << (bit_index % 64))) != 0;
}

std::pair<uint64_t, uint64_t> BloomFilter::get_seeds(const Hash256& hash) const {
    return hash.to_words();
}

std::pair<uint64_t, uint64_t> BloomFilter::get_seeds(const Hash128& hash) const {
    return {hash.h1, hash.h2};
}

std::pair<uint64_t, uint64_t> BloomFilter::get_seeds(const void* data, size_t len) const {
    Hash128 h = MurmurHash3::hash128(data, len, 0x9747b28c);
    return {h.h1, h.h2};
}

void BloomFilter::insert(const Hash256& hash) {
    auto [h1, h2] = get_seeds(hash);
    for (size_t i = 0; i < num_hashes_; ++i) {
        uint64_t combined = h1 + i * h2;
        set_bit(combined);
    }
    telemetry_.total_insertions++;
}

void BloomFilter::insert(const Hash128& hash) {
    auto [h1, h2] = get_seeds(hash);
    for (size_t i = 0; i < num_hashes_; ++i) {
        uint64_t combined = h1 + i * h2;
        set_bit(combined);
    }
    telemetry_.total_insertions++;
}

void BloomFilter::insert(const void* data, size_t len) {
    auto [h1, h2] = get_seeds(data, len);
    for (size_t i = 0; i < num_hashes_; ++i) {
        uint64_t combined = h1 + i * h2;
        set_bit(combined);
    }
    telemetry_.total_insertions++;
}

bool BloomFilter::might_contain(const Hash256& hash) {
    telemetry_.total_queries++;
    auto [h1, h2] = get_seeds(hash);
    for (size_t i = 0; i < num_hashes_; ++i) {
        uint64_t combined = h1 + i * h2;
        if (!test_bit(combined)) {
            telemetry_.true_negatives++;
            return false;
        }
    }
    telemetry_.reported_positives++;
    return true;
}

bool BloomFilter::might_contain(const Hash128& hash) {
    telemetry_.total_queries++;
    auto [h1, h2] = get_seeds(hash);
    for (size_t i = 0; i < num_hashes_; ++i) {
        uint64_t combined = h1 + i * h2;
        if (!test_bit(combined)) {
            telemetry_.true_negatives++;
            return false;
        }
    }
    telemetry_.reported_positives++;
    return true;
}

bool BloomFilter::might_contain(const void* data, size_t len) {
    telemetry_.total_queries++;
    auto [h1, h2] = get_seeds(data, len);
    for (size_t i = 0; i < num_hashes_; ++i) {
        uint64_t combined = h1 + i * h2;
        if (!test_bit(combined)) {
            telemetry_.true_negatives++;
            return false;
        }
    }
    telemetry_.reported_positives++;
    return true;
}

void BloomFilter::record_false_positive() {
    telemetry_.false_positives++;
}

void BloomFilter::clear() {
    std::fill(bit_array_.begin(), bit_array_.end(), 0);
    telemetry_ = BloomFilterTelemetry{};
}

double BloomFilter::theoretical_fpr() const {
    if (num_bits_ == 0 || telemetry_.total_insertions == 0) return 0.0;
    double exp_term = -static_cast<double>(num_hashes_ * telemetry_.total_insertions) / static_cast<double>(num_bits_);
    double prob_bit_zero = std::exp(exp_term);
    return std::pow(1.0 - prob_bit_zero, static_cast<double>(num_hashes_));
}

double BloomFilter::fill_ratio() const {
    if (num_bits_ == 0) return 0.0;
    size_t set_bits = 0;
    for (uint64_t word : bit_array_) {
        set_bits += __builtin_popcountll(word);
    }
    return static_cast<double>(set_bits) / static_cast<double>(num_bits_);
}

size_t BloomFilter::memory_bytes() const {
    return bit_array_.size() * sizeof(uint64_t);
}

} // namespace ds
} // namespace dedupfs
