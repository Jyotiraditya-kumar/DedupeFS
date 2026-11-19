#pragma once

#include "core/types.hpp"
#include <vector>
#include <cstddef>
#include <cstdint>
#include <utility>

namespace dedupfs {
namespace ds {

struct PriorityQueueDiagnostics {
    size_t total_clusters{0};
    uintmax_t total_wasted_bytes{0};
    uintmax_t max_single_cluster_wasted{0};
    size_t top_k_count{0};
    uintmax_t top_k_wasted_bytes{0};
    double top_k_share_percent{0.0};
};

/**
 * Advanced Data Structure: Binary Max-Heap Priority Queue
 * Prioritizes duplicate equivalence classes by total wasted physical storage.
 * Enables O(log N) cluster ranking, Top-K selective deduplication under I/O constraints,
 * and Pareto storage reclamation analysis.
 */
class DuplicateMaxHeap {
public:
    DuplicateMaxHeap() = default;
    explicit DuplicateMaxHeap(std::vector<DuplicateGroup> groups);

    // Core Heap Primitives
    void push(DuplicateGroup group);
    DuplicateGroup pop();
    const DuplicateGroup& top() const;
    bool empty() const { return heap_.empty(); }
    size_t size() const { return heap_.size(); }
    void clear() { heap_.clear(); }

    // Advanced Heap & Pareto Algorithms
    // 1. Top-K duplicate group extraction (O(K log N))
    std::vector<DuplicateGroup> extract_top_k(size_t k);

    // 2. Cumulative Pareto Distribution (analyzes 80/20 storage rule)
    // Returns list of (cluster_percent, cumulative_wasted_storage_percent) points
    std::vector<std::pair<double, double>> compute_pareto_distribution() const;

    // 3. Diagnostics & Telemetry
    PriorityQueueDiagnostics get_diagnostics(size_t k = 10) const;

private:
    std::vector<DuplicateGroup> heap_;

    // Sift operations preserving max-heap invariant
    void sift_up(size_t index);
    void sift_down(size_t index);
    void heapify();
};

} // namespace ds
} // namespace dedupfs
