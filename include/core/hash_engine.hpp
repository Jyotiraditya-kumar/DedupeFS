#pragma once

#include "core/types.hpp"
#include <string>
#include <cstddef>

namespace dedupfs {
namespace core {

class HashEngine {
public:
    static constexpr size_t PREFIX_SAMPLE_BYTES = 4096; // 4KB prefix sample
    static constexpr size_t BUFFER_CHUNK_BYTES = 65536; // 64KB streaming buffer

    // Tier 2: Computes fast 128-bit hash of first 4KB
    static bool compute_prefix_hash(FileInfo& file);

    // Tier 3: Computes full 256-bit cryptographic SHA-256
    static bool compute_full_sha256(FileInfo& file);

    // Direct helper for strings or raw memory
    static Hash256 sha256_buffer(const uint8_t* data, size_t size);
};

} // namespace core
} // namespace dedupfs
