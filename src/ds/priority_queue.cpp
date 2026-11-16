#include "ds/priority_queue.hpp"
#include <algorithm>
#include <stdexcept>

namespace dedupfs {
namespace ds {

DuplicateMaxHeap::DuplicateMaxHeap(std::vector<DuplicateGroup> groups)
    : heap_(std::move(groups)) {
    heapify();
}

void DuplicateMaxHeap::push(DuplicateGroup group) {
    heap_.push_back(std::move(group));
    sift_up(heap_.size() - 1);
}

DuplicateGroup DuplicateMaxHeap::pop() {
    if (heap_.empty()) {
        throw std::runtime_error("Attempted to pop from empty DuplicateMaxHeap");
    }

    DuplicateGroup max_item = std::move(heap_[0]);
    if (heap_.size() > 1) {
        heap_[0] = std::move(heap_.back());
        heap_.pop_back();
        sift_down(0);
    } else {
        heap_.pop_back();
    }

    return max_item;
}

const DuplicateGroup& DuplicateMaxHeap::top() const {
    if (heap_.empty()) {
        throw std::runtime_error("Attempted to access top of empty DuplicateMaxHeap");
    }
    return heap_[0];
}

void DuplicateMaxHeap::sift_up(size_t index) {
    while (index > 0) {
        size_t parent = (index - 1) / 2;
        if (heap_[index].total_wasted_bytes() > heap_[parent].total_wasted_bytes()) {
            std::swap(heap_[index], heap_[parent]);
            index = parent;
        } else {
            break;
        }
    }
}

void DuplicateMaxHeap::sift_down(size_t index) {
    size_t n = heap_.size();
    while (true) {
        size_t largest = index;
        size_t left = 2 * index + 1;
        size_t right = 2 * index + 2;

        if (left < n && heap_[left].total_wasted_bytes() > heap_[largest].total_wasted_bytes()) {
            largest = left;
        }
        if (right < n && heap_[right].total_wasted_bytes() > heap_[largest].total_wasted_bytes()) {
            largest = right;
        }

        if (largest != index) {
            std::swap(heap_[index], heap_[largest]);
            index = largest;
        } else {
            break;
        }
    }
}

void DuplicateMaxHeap::heapify() {
    if (heap_.size() <= 1) return;
    // Floyd's algorithm starting from the last internal node
    for (int i = static_cast<int>(heap_.size() / 2) - 1; i >= 0; --i) {
        sift_down(static_cast<size_t>(i));
    }
}

std::vector<DuplicateGroup> DuplicateMaxHeap::extract_top_k(size_t k) {
    // Clone heap to avoid destructive extraction of original state
    DuplicateMaxHeap temp = *this;
    std::vector<DuplicateGroup> top_k;
    size_t count = std::min(k, temp.size());
    top_k.reserve(count);

    for (size_t i = 0; i < count; ++i) {
        top_k.push_back(temp.pop());
    }

    return top_k;
}

std::vector<std::pair<double, double>> DuplicateMaxHeap::compute_pareto_distribution() const {
    if (heap_.empty()) return {};

    // Clone and sort descending
    DuplicateMaxHeap temp = *this;
    std::vector<uintmax_t> wasted_sizes;
    wasted_sizes.reserve(temp.size());

    uintmax_t total_wasted = 0;
    while (!temp.empty()) {
        uintmax_t w = temp.pop().total_wasted_bytes();
        wasted_sizes.push_back(w);
        total_wasted += w;
    }

    if (total_wasted == 0) return {};

    std::vector<std::pair<double, double>> curve;
    uintmax_t running_sum = 0;
    size_t total_n = wasted_sizes.size();

    // Sample 10 intervals (10%, 20%, ..., 100%)
    size_t interval = std::max<size_t>(1, total_n / 10);
    for (size_t i = 0; i < total_n; ++i) {
        running_sum += wasted_sizes[i];
        if ((i + 1) % interval == 0 || i == total_n - 1) {
            double cluster_pct = (static_cast<double>(i + 1) / total_n) * 100.0;
            double space_pct = (static_cast<double>(running_sum) / total_wasted) * 100.0;
            curve.emplace_back(cluster_pct, space_pct);
        }
    }

    return curve;
}

PriorityQueueDiagnostics DuplicateMaxHeap::get_diagnostics(size_t k) const {
    PriorityQueueDiagnostics diag;
    diag.total_clusters = heap_.size();
    if (heap_.empty()) return diag;

    diag.max_single_cluster_wasted = heap_[0].total_wasted_bytes();

    uintmax_t total_wasted = 0;
    for (const auto& g : heap_) {
        total_wasted += g.total_wasted_bytes();
    }
    diag.total_wasted_bytes = total_wasted;

    // Top-K analysis
    DuplicateMaxHeap temp = *this;
    size_t actual_k = std::min(k, temp.size());
    diag.top_k_count = actual_k;

    uintmax_t top_k_wasted = 0;
    for (size_t i = 0; i < actual_k; ++i) {
        top_k_wasted += temp.pop().total_wasted_bytes();
    }
    diag.top_k_wasted_bytes = top_k_wasted;

    if (total_wasted > 0) {
        diag.top_k_share_percent = (static_cast<double>(top_k_wasted) / total_wasted) * 100.0;
    }

    return diag;
}

} // namespace ds
} // namespace dedupfs
