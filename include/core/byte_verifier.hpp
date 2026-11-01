#pragma once

#include "core/types.hpp"
#include <string>
#include <cstddef>

namespace dedupfs {
namespace core {

class ByteVerifier {
public:
    static constexpr size_t VERIFY_CHUNK_SIZE = 65536; // 64KB streaming verification buffer

    // Performs byte-by-byte comparison between two candidate duplicate files.
    // Guarantees zero data loss even in the theoretical event of a SHA-256 collision.
    static bool verify_identical(const FileInfo& file1, const FileInfo& file2, DedupStats& stats);

    // Direct path comparison helper
    static bool verify_identical_paths(const std::string& path1, const std::string& path2);
};

} // namespace core
} // namespace dedupfs
