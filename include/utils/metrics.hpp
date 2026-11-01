#pragma once

#include <chrono>
#include <string>
#include <cstdint>

namespace dedupfs {
namespace utils {

class Timer {
public:
    Timer();
    void reset();
    double elapsed_ms() const;
    double elapsed_seconds() const;

private:
    std::chrono::high_resolution_clock::time_point start_time_;
};

class MemoryProfiler {
public:
    // Returns current resident set size (RSS) in bytes
    static uintmax_t get_current_rss_bytes();

    // Returns peak resident set size in bytes
    static uintmax_t get_peak_rss_bytes();
};

} // namespace utils
} // namespace dedupfs
