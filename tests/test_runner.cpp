#include "utils/logger.hpp"
#include <iostream>

namespace dedupfs {
namespace tests {
    bool run_bloom_filter_tests();
    bool run_hash_table_tests();
    bool run_priority_queue_tests();
    bool run_merkle_tree_tests();
    bool run_verifier_and_optimizer_tests();
    bool run_pipeline_e2e_tests();
}
}

int main() {
    using namespace dedupfs;
    utils::Logger::header("DEDUPFS ADVANCED DATA STRUCTURES AUTOMATED TEST SUITE");

    int passed = 0;
    int total = 6;

    if (tests::run_bloom_filter_tests()) passed++;
    if (tests::run_hash_table_tests()) passed++;
    if (tests::run_priority_queue_tests()) passed++;
    if (tests::run_merkle_tree_tests()) passed++;
    if (tests::run_verifier_and_optimizer_tests()) passed++;
    if (tests::run_pipeline_e2e_tests()) passed++;

    utils::Logger::header("TEST SUMMARY");
    std::cout << "Suites Executed: " << total << "\n";
    std::cout << "Suites Passed:   " << passed << "\n";
    std::cout << "Suites Failed:   " << (total - passed) << "\n";

    if (passed == total) {
        utils::Logger::success("ALL 6 DEDUPFS TEST SUITES PASSED SUCCESSFULLY (100% PASS RATE)!");
        return 0;
    } else {
        utils::Logger::error("SOME TEST CASES FAILED.");
        return 1;
    }
}
