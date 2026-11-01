#pragma once

#include <string>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <cstdint>
#include <mutex>

namespace dedupfs {
namespace utils {

enum class LogLevel {
    DEBUG,
    INFO,
    SUCCESS,
    WARNING,
    ERR
};

class Logger {
public:
    // Initialize console and file logging.
    // If log_file_path is empty, defaults to logs/dedupfs_<timestamp>.log
    static void init(const std::string& log_file_path = "", bool verbose = false);
    static void close();

    static void set_verbose(bool verbose);
    static bool is_verbose();
    static void set_log_file(const std::string& path);

    static void log(LogLevel level, const std::string& message);
    static void debug(const std::string& message);
    static void info(const std::string& message);
    static void success(const std::string& message);
    static void warning(const std::string& message);
    static void error(const std::string& message);

    // Format byte count to human readable (e.g. "14.25 MB")
    static std::string format_bytes(uintmax_t bytes);

    // Format duration in ms (e.g. "124.50 ms" or "2.34 s")
    static std::string format_time_ms(double ms);

    // Print a section header banner to console and log file
    static void header(const std::string& title);

    // Get active log file path
    static std::string get_current_log_path();

private:
    static std::string get_timestamp_str();
    static std::string get_datetime_stamp();
};

} // namespace utils
} // namespace dedupfs
