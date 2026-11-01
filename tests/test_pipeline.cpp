#include "core/pipeline.hpp"
#include "utils/logger.hpp"

#include <filesystem>
#include <fstream>
#include <vector>

namespace fs = std::filesystem;

namespace dedupfs {
namespace tests {

bool run_pipeline_e2e_tests() {
    utils::Logger::info("Running Full End-to-End Pipeline Integration Test...");

    std::string test_dir = "./scratch_e2e_sandbox";
    fs::remove_all(test_dir);
    fs::create_directories(test_dir + "/sub1");
    fs::create_directories(test_dir + "/sub2");

    // File 1: Unique size (1000 bytes) -> Should be skipped at Tier 1
    {
        std::ofstream ofs(test_dir + "/unique_1.bin");
        std::string content(1000, 'U');
        ofs.write(content.data(), content.size());
    }

    // File 2 & 3: Identical (2048 bytes) -> Should be detected as duplicates
    std::string dup_content(2048, 'D');
    {
        std::ofstream ofs(test_dir + "/dup_orig.bin");
        ofs.write(dup_content.data(), dup_content.size());
    }
    {
        std::ofstream ofs(test_dir + "/sub1/dup_copy1.bin");
        ofs.write(dup_content.data(), dup_content.size());
    }

    // File 4: Same size (2048 bytes) but different content -> Should be discarded at Tier 2 or 3
    {
        std::ofstream ofs(test_dir + "/sub2/diff_content.bin");
        std::string diff_content(2048, 'Z');
        ofs.write(diff_content.data(), diff_content.size());
    }

    // Run dry-run scan
    core::PipelineConfig config;
    config.root_path = test_dir;
    config.mode = core::DedupMode::DRY_RUN;
    config.verbose = false;

    core::DedupPipeline pipeline(config);
    DedupStats stats = pipeline.run();

    if (stats.total_files_scanned != 4) {
        utils::Logger::error("E2E Test failed: Expected 4 files scanned, got " + std::to_string(stats.total_files_scanned));
        fs::remove_all(test_dir);
        return false;
    }

    if (stats.unique_size_files_skipped != 1) {
        utils::Logger::error("E2E Test failed: Expected 1 file skipped at Tier 1, got " + std::to_string(stats.unique_size_files_skipped));
        fs::remove_all(test_dir);
        return false;
    }

    if (stats.duplicate_groups_count != 1 || stats.duplicate_files_count != 1) {
        utils::Logger::error("E2E Test failed: Expected 1 duplicate group with 1 redundant file!");
        fs::remove_all(test_dir);
        return false;
    }

    if (stats.potential_reclaimed_bytes != 2048) {
        utils::Logger::error("E2E Test failed: Expected 2048 bytes potential savings, got " + std::to_string(stats.potential_reclaimed_bytes));
        fs::remove_all(test_dir);
        return false;
    }

    utils::Logger::success("TC-10 PASSED: End-to-End Pipeline successfully identified exact duplicates and calculated correct space savings.");

    // Clean up
    fs::remove_all(test_dir);
    return true;
}

} // namespace tests
} // namespace dedupfs
