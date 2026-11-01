#include "core/pipeline.hpp"
#include "utils/logger.hpp"

#include <iostream>
#include <string>
#include <vector>

void print_banner() {
    std::cout << "\033[1m\033[36m"
              << "  ____           _             _____ ____  \n"
              << " |  _ \\  ___  __| |_   _ _ __ |  ___/ ___| \n"
              << " | | | |/ _ \\/ _` | | | | '_ \\| |_  \\___ \\ \n"
              << " | |_| |  __/ (_| | |_| | |_) |  _|  ___) |\n"
              << " |____/ \\___|\\__,_|\\__,_| .__/|_|   |____/ \n"
              << "                        |_|                \n"
              << " High-Performance Storage Deduplication Engine\n"
              << " Advanced Data Structures (M.Tech Sem 1)\n"
              << "\033[0m\n";
}

void print_usage(const char* prog) {
    std::cout << "Usage:\n"
              << "  " << prog << " scan <directory> [options]      Scan and audit duplicates (Dry-run by default)\n"
              << "  " << prog << " optimize <directory> [options]  Consolidate duplicate files via POSIX hard links\n"
              << "  " << prog << " help                           Display this help message\n\n"
              << "Options:\n"
              << "  --dry-run             Audit only, do not modify files (default for 'scan')\n"
              << "  --verbose, -v         Enable detailed debug output\n"
              << "  --min-size <bytes>    Minimum file size to consider (default: 1 byte)\n"
              << "  --fpr <float>         Target Bloom filter false-positive rate (default: 0.01 = 1%)\n"
              << "  --report-dir <path>   Directory to save execution & duplicate reports (default: ./reports)\n"
              << "  --log-file <path>     Custom path for persistent session log (default: ./logs/dedupfs_<ts>.log)\n"
              << "  --no-reports          Disable automatic report generation\n"
              << "  --no-log-file         Disable persistent file logging\n"
              << "  --help, -h            Show help\n\n"
              << "Examples:\n"
              << "  " << prog << " scan /home/user/data --verbose\n"
              << "  " << prog << " optimize /home/user/data\n"
              << "  " << prog << " scan /home/user/data --report-dir ./my_reports --log-file ./my_log.log\n";
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_banner();
        print_usage(argv[0]);
        return 1;
    }

    std::string command = argv[1];
    if (command == "help" || command == "--help" || command == "-h") {
        print_banner();
        print_usage(argv[0]);
        return 0;
    }

    if (command != "scan" && command != "optimize") {
        std::cerr << "Unknown command: " << command << "\n";
        print_usage(argv[0]);
        return 1;
    }

    if (argc < 3) {
        std::cerr << "Error: Directory path required for command '" << command << "'\n";
        print_usage(argv[0]);
        return 1;
    }

    std::string root_dir = argv[2];
    dedupfs::core::PipelineConfig config;
    config.root_path = root_dir;
    config.mode = (command == "optimize") ? dedupfs::core::DedupMode::HARD_LINK : dedupfs::core::DedupMode::DRY_RUN;

    std::string custom_log_file = "";
    bool enable_file_logging = true;

    // Parse options
    for (int i = 3; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--dry-run") {
            config.mode = dedupfs::core::DedupMode::DRY_RUN;
        } else if (arg == "--verbose" || arg == "-v") {
            config.verbose = true;
        } else if (arg == "--min-size" && i + 1 < argc) {
            config.min_file_size = std::stoull(argv[++i]);
        } else if (arg == "--fpr" && i + 1 < argc) {
            config.bloom_target_fpr = std::stod(argv[++i]);
        } else if (arg == "--report-dir" && i + 1 < argc) {
            config.reports_dir = argv[++i];
        } else if (arg == "--log-file" && i + 1 < argc) {
            custom_log_file = argv[++i];
        } else if (arg == "--no-reports") {
            config.enable_reports = false;
        } else if (arg == "--no-log-file") {
            enable_file_logging = false;
        }
    }

    if (enable_file_logging) {
        dedupfs::utils::Logger::init(custom_log_file, config.verbose);
    } else {
        dedupfs::utils::Logger::set_verbose(config.verbose);
    }

    print_banner();

    try {
        dedupfs::core::DedupPipeline pipeline(config);
        pipeline.run();
        pipeline.print_report();
    } catch (const std::exception& ex) {
        dedupfs::utils::Logger::error(std::string("Fatal exception during execution: ") + ex.what());
        dedupfs::utils::Logger::close();
        return 1;
    }

    dedupfs::utils::Logger::close();
    return 0;
}
