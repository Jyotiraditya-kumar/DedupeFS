#pragma once

#include "core/types.hpp"
#include <vector>
#include <list>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <memory>
#include <string>

namespace dedupfs {
namespace ds {

struct HashTableDiagnostics {
    size_t total_elements{0};
    size_t bucket_count{0};
    double load_factor{0.0};
    size_t empty_buckets{0};
    size_t collisions{0};
    size_t max_chain_length{0};
    double avg_non_empty_chain_length{0.0};
    double chain_length_variance{0.0};
    size_t rehash_count{0};
};

// Specialized high-performance hash table for Fingerprint -> std::vector<FileInfo>
class FingerprintHashTable {
public:
    struct Entry {
        Hash256 key;
        std::vector<FileInfo> files;
    };

    explicit FingerprintHashTable(size_t initial_buckets = 1024, double max_load_factor = 0.75);

    // Inserts a file associated with the given fingerprint.
    // If the fingerprint already exists, appends to the existing file list and returns pointer to entry.
    // is_duplicate is set to true if fingerprint was already present.
    Entry* insert(const Hash256& key, const FileInfo& file, bool& is_duplicate);

    // Lookup entries by fingerprint
    Entry* find(const Hash256& key);
    const Entry* find(const Hash256& key) const;
    bool contains(const Hash256& key) const;

    // Retrieve all duplicate groups found in the table
    std::vector<DuplicateGroup> get_duplicate_groups() const;

    // Diagnostics & telemetry
    HashTableDiagnostics get_diagnostics() const;
    size_t size() const { return size_; }
    size_t bucket_count() const { return bucket_count_; }
    double load_factor() const { return static_cast<double>(size_) / static_cast<double>(bucket_count_); }

    void clear();

private:
    void rehash(size_t new_bucket_count);
    size_t hash_to_bucket(const Hash256& key, size_t num_buckets) const;

    size_t bucket_count_{1024};
    size_t size_{0};
    double max_load_factor_{0.75};
    size_t rehash_count_{0};

    // Separate chaining: each bucket contains contiguous cache-friendly entries
    std::vector<std::vector<Entry>> buckets_;
};

} // namespace ds
} // namespace dedupfs
