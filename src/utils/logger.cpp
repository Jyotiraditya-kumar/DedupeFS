#include "utils/logger.hpp"

#include <chrono>
#include <ctime>
#include <filesystem>

namespace dedupfs {
namespace utils {

static bool s_verbose = false;
static std::ofstream s_file_stream;
static std::string s_active_log_path;
static std::mutex s_log_mutex;
static bool s_initialized = false;

// ANSI escape codes for console output
namespace Color {
    const char* RESET   = "\033[0m";
    const char* BOLD    = "\033[1m";
    const char* RED     = "\033[31m";
    const char* GREEN   = "\033[32m";
    const char* YELLOW  = "\033[33m";
    const char* BLUE    = "\033[34m";
    const char* MAGENTA = "\033[35m";
    const char* CYAN    = "\033[36m";
    const char* WHITE   = "\033[37m";
    const char* GRAY    = "\033[90m";
}

std::string Logger::get_timestamp_str() {
    auto now = std::chrono::system_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm_buf;
    localtime_r(&t, &tm_buf);

    char buf[64];
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &tm_buf);
    std::ostringstream oss;
    oss << buf << "." << std::setfill('0') << std::setw(3) << ms.count();
    return oss.str();
}

std::string Logger::get_datetime_stamp() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm_buf;
    localtime_r(&t, &tm_buf);

    char buf[64];
    std::strftime(buf, sizeof(buf), "%Y%m%d_%H%M%S", &tm_buf);
    return std::string(buf);
}

void Logger::init(const std::string& log_file_path, bool verbose) {
    std::lock_guard<std::mutex> lock(s_log_mutex);
    s_verbose = verbose;

    if (s_file_stream.is_open()) {
        s_file_stream.close();
    }

    std::string path = log_file_path;
    if (path.empty()) {
        std::filesystem::create_directories("logs");
        path = "logs/dedupfs_" + get_datetime_stamp() + ".log";
    } else {
        std::filesystem::path p(path);
        if (p.has_parent_path()) {
            std::filesystem::create_directories(p.parent_path());
        }
    }

    s_file_stream.open(path, std::ios::out | std::ios::app);
    if (s_file_stream.is_open()) {
        s_active_log_path = path;
        s_file_stream << "=== DedupFS Log Session Started: " << get_timestamp_str() << " ===\n";
        s_file_stream.flush();

        // Also update latest link / file if inside logs/
        if (path.find("logs/") == 0 || path.find("./logs/") == 0) {
            std::string latest_path = "logs/dedupfs_latest.log";
            std::ofstream latest_ofs(latest_path, std::ios::out | std::ios::trunc);
            if (latest_ofs.is_open()) {
                latest_ofs << "Active session log: " << path << "\n";
                latest_ofs << "Started at: " << get_timestamp_str() << "\n";
            }
        }
    }
    s_initialized = true;
}

void Logger::close() {
    std::lock_guard<std::mutex> lock(s_log_mutex);
    if (s_file_stream.is_open()) {
        s_file_stream << "=== DedupFS Log Session Ended: " << get_timestamp_str() << " ===\n\n";
        s_file_stream.close();

        // Overwrite latest.log with the complete log file
        if (s_active_log_path.find("logs/") == 0 || s_active_log_path.find("./logs/") == 0) {
            std::string latest_path = "logs/dedupfs_latest.log";
            std::error_code ec;
            std::filesystem::copy_file(s_active_log_path, latest_path, std::filesystem::copy_options::overwrite_existing, ec);
        }
    }
    s_initialized = false;
}

void Logger::set_verbose(bool verbose) {
    std::lock_guard<std::mutex> lock(s_log_mutex);
    s_verbose = verbose;
}

bool Logger::is_verbose() {
    std::lock_guard<std::mutex> lock(s_log_mutex);
    return s_verbose;
}

void Logger::set_log_file(const std::string& path) {
    init(path, s_verbose);
}

std::string Logger::get_current_log_path() {
    std::lock_guard<std::mutex> lock(s_log_mutex);
    return s_active_log_path;
}

void Logger::log(LogLevel level, const std::string& message) {
    std::lock_guard<std::mutex> lock(s_log_mutex);

    // Auto-init if not already initialized
    if (!s_initialized) {
        std::filesystem::create_directories("logs");
        std::string default_path = "logs/dedupfs_" + get_datetime_stamp() + ".log";
        s_file_stream.open(default_path, std::ios::out | std::ios::app);
        if (s_file_stream.is_open()) {
            s_active_log_path = default_path;
            s_file_stream << "=== DedupFS Log Session Started: " << get_timestamp_str() << " ===\n";
        }
        s_initialized = true;
    }

    const char* level_tag = "[INFO] ";
    const char* color_code = Color::RESET;

    switch (level) {
        case LogLevel::DEBUG:
            level_tag = "[DEBUG]";
            color_code = Color::GRAY;
            break;
        case LogLevel::INFO:
            level_tag = "[INFO] ";
            color_code = Color::CYAN;
            break;
        case LogLevel::SUCCESS:
            level_tag = "[OK]   ";
            color_code = Color::GREEN;
            break;
        case LogLevel::WARNING:
            level_tag = "[WARN] ";
            color_code = Color::YELLOW;
            break;
        case LogLevel::ERR:
            level_tag = "[ERROR]";
            color_code = Color::RED;
            break;
    }

    // Console output
    if (level != LogLevel::DEBUG || s_verbose) {
        std::ostream& out = (level == LogLevel::ERR) ? std::cerr : std::cout;
        out << color_code << level_tag << Color::RESET << " " << message << "\n";
    }

    // File output (clean uncolored timestamped text)
    if (s_file_stream.is_open()) {
        s_file_stream << "[" << get_timestamp_str() << "] "
                      << level_tag << " " << message << "\n";
        s_file_stream.flush();
    }
}

void Logger::debug(const std::string& message) {
    log(LogLevel::DEBUG, message);
}

void Logger::info(const std::string& message) {
    log(LogLevel::INFO, message);
}

void Logger::success(const std::string& message) {
    log(LogLevel::SUCCESS, message);
}

void Logger::warning(const std::string& message) {
    log(LogLevel::WARNING, message);
}

void Logger::error(const std::string& message) {
    log(LogLevel::ERR, message);
}

std::string Logger::format_bytes(uintmax_t bytes) {
    const char* units[] = {"B", "KB", "MB", "GB", "TB"};
    int unit_idx = 0;
    double count = static_cast<double>(bytes);

    while (count >= 1024.0 && unit_idx < 4) {
        count /= 1024.0;
        unit_idx++;
    }

    std::ostringstream oss;
    oss << std::fixed << std::setprecision(2) << count << " " << units[unit_idx];
    return oss.str();
}

std::string Logger::format_time_ms(double ms) {
    std::ostringstream oss;
    if (ms >= 1000.0) {
        oss << std::fixed << std::setprecision(2) << (ms / 1000.0) << " s";
    } else {
        oss << std::fixed << std::setprecision(2) << ms << " ms";
    }
    return oss.str();
}

void Logger::header(const std::string& title) {
    std::lock_guard<std::mutex> lock(s_log_mutex);
    std::cout << "\n" << Color::BOLD << Color::BLUE 
              << "========================================================\n"
              << "  " << title << "\n"
              << "========================================================\n"
              << Color::RESET;

    if (s_file_stream.is_open()) {
        s_file_stream << "\n========================================================\n"
                      << "  " << title << "\n"
                      << "========================================================\n";
        s_file_stream.flush();
    }
}

} // namespace utils
} // namespace dedupfs
