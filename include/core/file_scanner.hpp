#pragma once

#include "core/types.hpp"
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <cstdint>

namespace dedupfs {
namespace core {

struct ScannerOptions {
    bool follow_symlinks{false};
    uintmax_t min_file_size{1}; // Skip 0-byte files by default
    uintmax_t max_file_size{UINTMAX_MAX};
    std::vector<std::string> exclude_dirs{};
};

// Map from FileSize to Candidate File Records
using SizeBucketMap = std::unordered_map<uintmax_t, std::vector<FileInfo>>;

class FileScanner {
public:
    explicit FileScanner(ScannerOptions options = {});

    // Scans directory recursively and groups files having identical sizes (candidate duplicates)
    SizeBucketMap scan_directory(const std::string& root_path, DedupStats& stats);

private:
    bool is_excluded(const std::string& path) const;
    uint64_t make_inode_key(dev_t dev, ino_t ino) const;

    ScannerOptions options_;
    std::unordered_set<uint64_t> visited_inodes_;
};

} // namespace core
} // namespace dedupfs
