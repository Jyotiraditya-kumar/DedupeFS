#include "ds/hash_table.hpp"
#include <algorithm>
#include <numeric>
#include <cmath>

namespace dedupfs {
namespace ds {

FingerprintHashTable::FingerprintHashTable(size_t initial_buckets, double max_load_factor)
    : bucket_count_(std::max<size_t>(initial_buckets, 16)),
      size_(0),
      max_load_factor_(max_load_factor),
      rehash_count_(0) {
    buckets_.resize(bucket_count_);
}

size_t FingerprintHashTable::hash_to_bucket(const Hash256& key, size_t num_buckets) const {
    return std::hash<Hash256>{}(key) % num_buckets;
}

FingerprintHashTable::Entry* FingerprintHashTable::insert(const Hash256& key, const FileInfo& file, bool& is_duplicate) {
    // Check if resizing is necessary
    if (static_cast<double>(size_ + 1) / static_cast<double>(bucket_count_) > max_load_factor_) {
        rehash(bucket_count_ * 2);
    }

    size_t idx = hash_to_bucket(key, bucket_count_);
    auto& bucket = buckets_[idx];

    for (auto& entry : bucket) {
        if (entry.key == key) {
            is_duplicate = true;
            entry.files.push_back(file);
            return &entry;
        }
    }

    // New key
    is_duplicate = false;
    bucket.push_back(Entry{key, {file}});
    size_++;
    return &bucket.back();
}

FingerprintHashTable::Entry* FingerprintHashTable::find(const Hash256& key) {
    size_t idx = hash_to_bucket(key, bucket_count_);
    auto& bucket = buckets_[idx];

    for (auto& entry : bucket) {
        if (entry.key == key) {
            return &entry;
        }
    }
    return nullptr;
}

const FingerprintHashTable::Entry* FingerprintHashTable::find(const Hash256& key) const {
    size_t idx = hash_to_bucket(key, bucket_count_);
    const auto& bucket = buckets_[idx];

    for (const auto& entry : bucket) {
        if (entry.key == key) {
            return &entry;
        }
    }
    return nullptr;
}

bool FingerprintHashTable::contains(const Hash256& key) const {
    return find(key) != nullptr;
}

std::vector<DuplicateGroup> FingerprintHashTable::get_duplicate_groups() const {
    std::vector<DuplicateGroup> groups;

    for (const auto& bucket : buckets_) {
        for (const auto& entry : bucket) {
            if (entry.files.size() > 1) {
                DuplicateGroup group;
                group.canonical_file = entry.files.front();
                group.file_size = group.canonical_file.size;
                // Files beyond the first one are redundant duplicates
                for (size_t i = 1; i < entry.files.size(); ++i) {
                    group.duplicates.push_back(entry.files[i]);
                }
                groups.push_back(std::move(group));
            }
        }
    }

    return groups;
}

void FingerprintHashTable::rehash(size_t new_bucket_count) {
    std::vector<std::vector<Entry>> new_buckets(new_bucket_count);

    for (auto& bucket : buckets_) {
        for (auto& entry : bucket) {
            size_t new_idx = hash_to_bucket(entry.key, new_bucket_count);
            new_buckets[new_idx].push_back(std::move(entry));
        }
    }

    buckets_ = std::move(new_buckets);
    bucket_count_ = new_bucket_count;
    rehash_count_++;
}

void FingerprintHashTable::clear() {
    for (auto& bucket : buckets_) {
        bucket.clear();
    }
    size_ = 0;
}

HashTableDiagnostics FingerprintHashTable::get_diagnostics() const {
    HashTableDiagnostics diag;
    diag.total_elements = size_;
    diag.bucket_count = bucket_count_;
    diag.load_factor = load_factor();
    diag.rehash_count = rehash_count_;

    size_t empty = 0;
    size_t max_chain = 0;
    size_t collisions = 0;
    size_t total_chain_len_non_empty = 0;
    size_t non_empty_buckets = 0;

    for (const auto& bucket : buckets_) {
        size_t len = bucket.size();
        if (len == 0) {
            empty++;
        } else {
            non_empty_buckets++;
            total_chain_len_non_empty += len;
            if (len > 1) {
                collisions += (len - 1);
            }
            if (len > max_chain) {
                max_chain = len;
            }
        }
    }

    diag.empty_buckets = empty;
    diag.collisions = collisions;
    diag.max_chain_length = max_chain;

    if (non_empty_buckets > 0) {
        diag.avg_non_empty_chain_length = static_cast<double>(total_chain_len_non_empty) / static_cast<double>(non_empty_buckets);

        double variance_sum = 0.0;
        for (const auto& bucket : buckets_) {
            if (!bucket.empty()) {
                double diff = static_cast<double>(bucket.size()) - diag.avg_non_empty_chain_length;
                variance_sum += (diff * diff);
            }
        }
        diag.chain_length_variance = variance_sum / static_cast<double>(non_empty_buckets);
    }

    return diag;
}

} // namespace ds
} // namespace dedupfs
