#include "ds/hash_table.hpp"
#include "ds/murmur3.hpp"
#include "utils/logger.hpp"

#include <iostream>
#include <string>

namespace dedupfs {
namespace tests {

bool run_hash_table_tests() {
    utils::Logger::info("Running Fingerprint Hash Table Unit Tests...");

    // Start with small bucket count to trigger rehashing
    ds::FingerprintHashTable table(16, 0.75);

    // Test 1: Insertions and Automatic Rehashing
    const size_t num_unique = 100;
    for (size_t i = 0; i < num_unique; ++i) {
        Hash256 h{};
        h.bytes[0] = static_cast<uint8_t>(i & 0xFF);
        h.bytes[1] = static_cast<uint8_t>((i >> 8) & 0xFF);

        FileInfo info;
        info.path = "/test/file_" + std::to_string(i) + ".dat";
        info.size = 1024 * (i + 1);

        bool is_dup = false;
        table.insert(h, info, is_dup);

        if (is_dup) {
            utils::Logger::error("Hash Table TC-04 failed: Incorrectly flagged unique key as duplicate!");
            return false;
        }
    }

    if (table.size() != num_unique) {
        utils::Logger::error("Hash Table TC-04 failed: Size mismatch after insertions.");
        return false;
    }

    auto diag = table.get_diagnostics();
    if (diag.rehash_count == 0) {
        utils::Logger::error("Hash Table TC-05 failed: Rehashing was not triggered!");
        return false;
    }
    utils::Logger::success("TC-04 & TC-05 PASSED: Insertions and automatic dynamic rehashing verified (" +
                          std::to_string(diag.rehash_count) + " rehashes occurred).");

    // Test 2: Duplicate Grouping
    Hash256 dup_key{};
    dup_key.bytes[0] = 0xAA;
    dup_key.bytes[1] = 0xBB;

    FileInfo orig;
    orig.path = "/data/master.bin";
    orig.size = 4096;

    FileInfo copy1;
    copy1.path = "/data/backup/copy1.bin";
    copy1.size = 4096;

    FileInfo copy2;
    copy2.path = "/data/backup/copy2.bin";
    copy2.size = 4096;

    bool dup_flag = false;
    table.insert(dup_key, orig, dup_flag);
    table.insert(dup_key, copy1, dup_flag);
    if (!dup_flag) {
        utils::Logger::error("Hash Table TC-06 failed: Duplicate not detected on second insert!");
        return false;
    }

    table.insert(dup_key, copy2, dup_flag);
    if (!dup_flag) {
        utils::Logger::error("Hash Table TC-06 failed: Duplicate not detected on third insert!");
        return false;
    }

    auto groups = table.get_duplicate_groups();
    bool found_target_group = false;
    for (const auto& g : groups) {
        if (g.canonical_file.path == "/data/master.bin") {
            if (g.duplicates.size() == 2 && g.total_wasted_bytes() == 8192) {
                found_target_group = true;
                break;
            }
        }
    }

    if (!found_target_group) {
        utils::Logger::error("Hash Table TC-06 failed: Duplicate group structure incorrect.");
        return false;
    }

    utils::Logger::success("TC-06 PASSED: Duplicate group detection and wasted byte calculation verified.");
    return true;
}

} // namespace tests
} // namespace dedupfs
