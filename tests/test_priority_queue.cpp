#include "ds/priority_queue.hpp"
#include "utils/logger.hpp"
#include <cassert>
#include <iostream>

namespace dedupfs {
namespace tests {

bool run_priority_queue_tests() {
    utils::Logger::info("Running Binary Max-Heap Priority Queue Unit Tests...");

    // Setup mock duplicate groups with different wasted capacities
    std::vector<DuplicateGroup> groups;
    
    // Group 1: 100 KB wasted (10KB file, 10 copies)
    DuplicateGroup g1;
    g1.file_size = 10 * 1024;
    for (int i = 0; i < 10; ++i) {
        FileInfo f;
        f.path = "/path/g1/dup" + std::to_string(i);
        g1.duplicates.push_back(f);
    }
    groups.push_back(g1);

    // Group 2: 500 KB wasted (50KB file, 10 copies)
    DuplicateGroup g2;
    g2.file_size = 50 * 1024;
    for (int i = 0; i < 10; ++i) {
        FileInfo f;
        f.path = "/path/g2/dup" + std::to_string(i);
        g2.duplicates.push_back(f);
    }
    groups.push_back(g2);

    // Group 3: 50 KB wasted (5KB file, 10 copies)
    DuplicateGroup g3;
    g3.file_size = 5 * 1024;
    for (int i = 0; i < 10; ++i) {
        FileInfo f;
        f.path = "/path/g3/dup" + std::to_string(i);
        g3.duplicates.push_back(f);
    }
    groups.push_back(g3);

    // Group 4: 1 MB wasted (100KB file, 10 copies)
    DuplicateGroup g4;
    g4.file_size = 100 * 1024;
    for (int i = 0; i < 10; ++i) {
        FileInfo f;
        f.path = "/path/g4/dup" + std::to_string(i);
        g4.duplicates.push_back(f);
    }
    groups.push_back(g4);

    // TC-PQ-01: Floyd's O(N) heapify and Top element invariant
    ds::DuplicateMaxHeap max_heap(groups);
    if (max_heap.size() != 4) {
        utils::Logger::error("Max-Heap size mismatch after batch construction!");
        return false;
    }

    if (max_heap.top().total_wasted_bytes() != 100 * 1024 * 10) {
        utils::Logger::error("Max-Heap root is not the maximum element!");
        return false;
    }
    utils::Logger::success("TC-PQ-01 PASSED: Floyd's O(N) heapify correctly positioned largest cluster at root.");

    // TC-PQ-02: Sequential Pop in strictly descending order
    uintmax_t expected_wasted[] = {
        100 * 1024 * 10, // 1000 KB (g4)
        50 * 1024 * 10,  // 500 KB (g2)
        10 * 1024 * 10,  // 100 KB (g1)
        5 * 1024 * 10    // 50 KB (g3)
    };

    ds::DuplicateMaxHeap heap_copy = max_heap;
    for (int i = 0; i < 4; ++i) {
        DuplicateGroup top = heap_copy.pop();
        if (top.total_wasted_bytes() != expected_wasted[i]) {
            utils::Logger::error("Max-Heap pop order violation at index " + std::to_string(i));
            return false;
        }
    }
    if (!heap_copy.empty()) {
        utils::Logger::error("Max-Heap should be empty after popping all elements!");
        return false;
    }
    utils::Logger::success("TC-PQ-02 PASSED: Max-Heap pop yields strictly descending order of storage footprint.");

    // TC-PQ-03: Extract Top-K (K=2)
    auto top2 = max_heap.extract_top_k(2);
    if (top2.size() != 2 || top2[0].total_wasted_bytes() != expected_wasted[0] || top2[1].total_wasted_bytes() != expected_wasted[1]) {
        utils::Logger::error("extract_top_k(2) returned incorrect subset!");
        return false;
    }
    utils::Logger::success("TC-PQ-03 PASSED: O(K log N) Top-K cluster extraction verified.");

    // TC-PQ-04: Pareto Distribution Analysis
    auto pareto = max_heap.compute_pareto_distribution();
    if (pareto.empty() || pareto.back().second < 99.9) {
        utils::Logger::error("Pareto cumulative distribution did not converge to 100%!");
        return false;
    }
    auto diag = max_heap.get_diagnostics(2);
    if (diag.total_clusters != 4 || diag.top_k_count != 2) {
        utils::Logger::error("Priority Queue diagnostics mismatch!");
        return false;
    }
    utils::Logger::success("TC-PQ-04 PASSED: Pareto distribution and priority queue telemetry verified.");

    return true;
}

} // namespace tests
} // namespace dedupfs
