#include "utils/metrics.hpp"
#include <fstream>
#include <unistd.h>
#include <sys/resource.h>

namespace dedupfs {
namespace utils {

Timer::Timer() {
    reset();
}

void Timer::reset() {
    start_time_ = std::chrono::high_resolution_clock::now();
}

double Timer::elapsed_ms() const {
    auto now = std::chrono::high_resolution_clock::now();
    return std::chrono::duration<double, std::milli>(now - start_time_).count();
}

double Timer::elapsed_seconds() const {
    auto now = std::chrono::high_resolution_clock::now();
    return std::chrono::duration<double>(now - start_time_).count();
}

uintmax_t MemoryProfiler::get_current_rss_bytes() {
    // Read /proc/self/statm on Linux: [size, resident, shared, text, lib, data, dt]
    std::ifstream statm("/proc/self/statm");
    if (!statm.is_open()) {
        return 0;
    }
    long total_pages = 0;
    long resident_pages = 0;
    statm >> total_pages >> resident_pages;
    long page_size_bytes = sysconf(_SC_PAGESIZE);
    if (page_size_bytes <= 0) {
        page_size_bytes = 4096;
    }
    return static_cast<uintmax_t>(resident_pages) * page_size_bytes;
}

uintmax_t MemoryProfiler::get_peak_rss_bytes() {
    struct rusage usage;
    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        // ru_maxrss is in kilobytes on Linux
        return static_cast<uintmax_t>(usage.ru_maxrss) * 1024ULL;
    }
    return 0;
}

} // namespace utils
} // namespace dedupfs
