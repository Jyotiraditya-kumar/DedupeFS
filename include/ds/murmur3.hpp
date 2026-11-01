#pragma once

#include "core/types.hpp"
#include <cstddef>
#include <cstdint>

namespace dedupfs {
namespace ds {

class MurmurHash3 {
public:
    // Computes 128-bit MurmurHash3 for x64 architecture
    static Hash128 hash128(const void* key, size_t len, uint32_t seed = 42);

    // Convenience helper for byte vectors or buffers
    static Hash128 hash_buffer(const uint8_t* buffer, size_t size, uint32_t seed = 42);
};

} // namespace ds
} // namespace dedupfs
