#include "core/byte_verifier.hpp"
#include "core/storage_optimizer.hpp"
#include "utils/logger.hpp"

#include <fstream>
#include <filesystem>
#include <sys/stat.h>
#include <unistd.h>

namespace fs = std::filesystem;

namespace dedupfs {
namespace tests {

bool run_verifier_and_optimizer_tests() {
    utils::Logger::info("Running Verifier and Storage Optimizer Unit Tests...");

    // Create a temporary sandbox directory
    std::string test_dir = "./scratch_test_sandbox";
    fs::remove_all(test_dir);
    fs::create_directories(test_dir);

    std::string fileA = test_dir + "/fileA.bin";
    std::string fileB = test_dir + "/fileB.bin"; // Identical to A
    std::string fileC = test_dir + "/fileC.bin"; // Differs by 1 byte at EOF

    std::vector<char> data1(131072, 'X'); // 128KB of 'X'
    std::vector<char> data2 = data1;
    std::vector<char> data3 = data1;
    data3.back() = 'Y'; // 1 byte mismatch at EOF

    {
        std::ofstream ofsA(fileA, std::ios::binary);
        ofsA.write(data1.data(), data1.size());
        std::ofstream ofsB(fileB, std::ios::binary);
        ofsB.write(data2.data(), data2.size());
        std::ofstream ofsC(fileC, std::ios::binary);
        ofsC.write(data3.data(), data3.size());
    }

    // Test 1: Byte Verifier Accuracy
    if (!core::ByteVerifier::verify_identical_paths(fileA, fileB)) {
        utils::Logger::error("Verifier TC-07 failed: Identical files flagged as different!");
        fs::remove_all(test_dir);
        return false;
    }

    if (core::ByteVerifier::verify_identical_paths(fileA, fileC)) {
        utils::Logger::error("Verifier TC-07 failed: 1-byte difference at EOF was not detected!");
        fs::remove_all(test_dir);
        return false;
    }
    utils::Logger::success("TC-07 PASSED: Streaming Byte Verifier detects identical files and 1-byte EOF differences.");

    // Test 2: Storage Optimizer Dry-Run
    struct stat stA_before, stB_before;
    stat(fileA.c_str(), &stA_before);
    stat(fileB.c_str(), &stB_before);

    DuplicateGroup group;
    group.canonical_file.path = fileA;
    group.canonical_file.size = data1.size();
    group.canonical_file.inode = stA_before.st_ino;
    group.canonical_file.device = stA_before.st_dev;
    group.file_size = data1.size();

    FileInfo dupB;
    dupB.path = fileB;
    dupB.size = data2.size();
    dupB.inode = stB_before.st_ino;
    dupB.device = stB_before.st_dev;
    group.duplicates.push_back(dupB);

    DedupStats stats;
    core::StorageOptimizer dry_optimizer(core::DedupMode::DRY_RUN);
    auto dry_rep = dry_optimizer.optimize_group(group, stats);

    struct stat stB_after_dry;
    stat(fileB.c_str(), &stB_after_dry);
    if (stB_after_dry.st_ino != stB_before.st_ino || dry_rep.files_consolidated != 1) {
        utils::Logger::error("Optimizer TC-08 failed: Dry-run modified filesystem!");
        fs::remove_all(test_dir);
        return false;
    }
    utils::Logger::success("TC-08 PASSED: Dry-Run mode audits savings without altering disk files.");

    // Test 3: Storage Optimizer Live Hard-Linking
    core::StorageOptimizer live_optimizer(core::DedupMode::HARD_LINK);
    auto live_rep = live_optimizer.optimize_group(group, stats);

    struct stat stA_after, stB_after;
    stat(fileA.c_str(), &stA_after);
    stat(fileB.c_str(), &stB_after);

    if (live_rep.files_consolidated != 1 || stA_after.st_ino != stB_after.st_ino || stA_after.st_nlink != 2) {
        utils::Logger::error("Optimizer TC-09 failed: Hard-link consolidation failed or inode mismatch!");
        fs::remove_all(test_dir);
        return false;
    }
    utils::Logger::success("TC-09 PASSED: Hard-Link consolidation atomically unified inodes (st_nlink = 2).");

    // Clean up sandbox
    fs::remove_all(test_dir);
    return true;
}

} // namespace tests
} // namespace dedupfs
