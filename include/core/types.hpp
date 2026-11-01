#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <cstdint>
#include <array>
#include <iomanip>
#include <sstream>
#include <sys/types.h>

namespace dedupfs {

// Breakdown metrics for a category (subfolder or file extension)
struct UsageMetric {
    size_t file_count{0};
    uintmax_t total_bytes{0};
    size_t duplicate_count{0};
    uintmax_t wasted_bytes{0};
};

// 128-bit hash used for fast pre-filtering (e.g., MurmurHash3)
struct Hash128 {
    uint64_t h1{0};
    uint64_t h2{0};

    bool operator==(const Hash128& other) const {
        return h1 == other.h1 && h2 == other.h2;
    }

    bool operator!=(const Hash128& other) const {
        return !(*this == other);
    }

    std::string to_hex() const {
        std::ostringstream oss;
        oss << std::hex << std::setfill('0')
            << std::setw(16) << h1
            << std::setw(16) << h2;
        return oss.str();
    }
};

// 256-bit cryptographic hash (SHA-256)
struct Hash256 {
    std::array<uint8_t, 32> bytes{};

    bool operator==(const Hash256& other) const {
        return bytes == other.bytes;
    }

    bool operator!=(const Hash256& other) const {
        return !(*this == other);
    }

    bool operator<(const Hash256& other) const {
        return bytes < other.bytes;
    }

    std::string to_hex() const {
        std::ostringstream oss;
        oss << std::hex << std::setfill('0');
        for (uint8_t b : bytes) {
            oss << std::setw(2) << static_cast<int>(b);
        }
        return oss.str();
    }

    // Extract two 64-bit words for double hashing in Bloom filter
    std::pair<uint64_t, uint64_t> to_words() const {
        uint64_t w1 = 0;
        uint64_t w2 = 0;
        for (size_t i = 0; i < 8; ++i) {
            w1 = (w1 << 8) | bytes[i];
            w2 = (w2 << 8) | bytes[8 + i];
        }
        return {w1, w2};
    }
};

// Metadata representation for a scanned file
struct FileInfo {
    std::string path;
    uintmax_t size{0};
    ino_t inode{0};
    dev_t device{0};
    time_t mtime{0};
    nlink_t nlink{1};

    // Staged hash values
    bool has_prefix_hash{false};
    Hash128 prefix_hash{};

    bool has_full_hash{false};
    Hash256 full_hash{};
};

// Group of duplicate files sharing the same content
struct DuplicateGroup {
    FileInfo canonical_file;
    std::vector<FileInfo> duplicates;
    uintmax_t file_size{0};

    uintmax_t total_wasted_bytes() const {
        return duplicates.size() * file_size;
    }
};

// Overall execution statistics
struct DedupStats {
    size_t total_files_scanned{0};
    size_t total_dirs_scanned{0};
    uintmax_t total_bytes_scanned{0};

    size_t unique_size_files_skipped{0};
    size_t prefix_hash_evaluated{0};
    size_t prefix_hash_mismatches{0};
    size_t full_hash_evaluated{0};

    size_t bloom_filter_queries{0};
    size_t bloom_filter_negatives{0};
    size_t bloom_filter_positives{0};
    size_t bloom_filter_false_positives{0};

    size_t byte_verifications_performed{0};
    size_t byte_verifications_matched{0};
    size_t byte_verifications_failed{0};

    size_t duplicate_groups_count{0};
    size_t duplicate_files_count{0};
    uintmax_t potential_reclaimed_bytes{0};
    uintmax_t actually_reclaimed_bytes{0};

    double scan_time_ms{0.0};
    double hash_time_ms{0.0};
    double dedup_time_ms{0.0};
    double total_time_ms{0.0};

    // Granular breakdowns for academic reporting and UI visualization
    std::unordered_map<std::string, UsageMetric> file_type_metrics;
    std::unordered_map<std::string, UsageMetric> subfolder_metrics;
};

} // namespace dedupfs

namespace std {
    template <>
    struct hash<dedupfs::Hash256> {
        size_t operator()(const dedupfs::Hash256& h) const noexcept {
            // Combine first two 64-bit words
            auto [w1, w2] = h.to_words();
            return static_cast<size_t>(w1 ^ (w2 + 0x9e3779b97f4a7c15ULL + (w1 << 6) + (w1 >> 2)));
        }
    };

    template <>
    struct hash<dedupfs::Hash128> {
        size_t operator()(const dedupfs::Hash128& h) const noexcept {
            return static_cast<size_t>(h.h1 ^ (h.h2 + 0x9e3779b97f4a7c15ULL + (h.h1 << 6) + (h.h1 >> 2)));
        }
    };
}
