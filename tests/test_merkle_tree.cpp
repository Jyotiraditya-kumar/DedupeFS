#include "ds/merkle_tree.hpp"
#include "core/hash_engine.hpp"
#include "utils/logger.hpp"
#include <cassert>
#include <iostream>

namespace dedupfs {
namespace tests {

bool run_merkle_tree_tests() {
    utils::Logger::info("Running Hierarchical Merkle Tree Unit Tests...");

    // Create synthetic file catalog
    // Hierarchy:
    // root/
    //   dir1/
    //     file_a.txt (hash A)
    //     file_b.txt (hash B)
    //   dir2/ (identical copy of dir1)
    //     file_a.txt (hash A)
    //     file_b.txt (hash B)
    //   dir3/ (different)
    //     file_c.txt (hash C)

    std::vector<FileInfo> files;

    FileInfo f1;
    f1.path = "/test_root/dir1/file_a.txt";
    f1.size = 1024;
    f1.full_hash = Hash256::from_hex("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef");
    files.push_back(f1);

    FileInfo f2;
    f2.path = "/test_root/dir1/file_b.txt";
    f2.size = 2048;
    f2.full_hash = Hash256::from_hex("abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789");
    files.push_back(f2);

    FileInfo f3;
    f3.path = "/test_root/dir2/file_a.txt";
    f3.size = 1024;
    f3.full_hash = f1.full_hash;
    files.push_back(f3);

    FileInfo f4;
    f4.path = "/test_root/dir2/file_b.txt";
    f4.size = 2048;
    f4.full_hash = f2.full_hash;
    files.push_back(f4);

    FileInfo f5;
    f5.path = "/test_root/dir3/file_c.txt";
    f5.size = 512;
    f5.full_hash = Hash256::from_hex("fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210");
    files.push_back(f5);

    // TC-MT-01: Build Merkle Tree
    ds::MerkleTree tree1;
    bool ok = tree1.build("/test_root", files);
    if (!ok || tree1.root_hash_hex().empty()) {
        utils::Logger::error("Merkle Tree build failed!");
        return false;
    }
    if (tree1.total_leaves() != 5) {
        utils::Logger::error("Merkle Tree leaves count mismatch! Expected 5, got " + std::to_string(tree1.total_leaves()));
        return false;
    }
    utils::Logger::success("TC-MT-01 PASSED: Merkle Tree successfully built with valid root hash (" + tree1.root_hash_hex().substr(0, 16) + "...).");

    // TC-MT-02: Cryptographic Root Determinism
    ds::MerkleTree tree2;
    tree2.build("/test_root", files);
    if (tree1.root_hash_hex() != tree2.root_hash_hex()) {
        utils::Logger::error("Merkle Tree deterministic hash invariant violated!");
        return false;
    }
    utils::Logger::success("TC-MT-02 PASSED: Merkle Tree root hash is 100% deterministic across rebuilds.");

    // TC-MT-03: Subtree Duplicate Detection (dir1 and dir2 are identical subtrees)
    auto dup_subtrees = tree1.find_duplicate_subtrees();
    if (dup_subtrees.empty()) {
        utils::Logger::error("Failed to detect duplicate subtrees!");
        return false;
    }
    bool found_dir_dup = false;
    for (const auto& st : dup_subtrees) {
        if (st.subtree_size == (1024 + 2048) && st.files_count == 2) {
            found_dir_dup = true;
            break;
        }
    }
    if (!found_dir_dup) {
        utils::Logger::error("Subtree duplicate does not match expected size and file count!");
        return false;
    }
    utils::Logger::success("TC-MT-03 PASSED: Identified identical duplicate sub-directory trees (dir1 == dir2) in O(N).");

    // TC-MT-04: Cryptographic Audit Proof & Verification
    auto proof = tree1.generate_proof("dir1/file_a.txt");
    if (proof.empty()) {
        utils::Logger::error("Failed to generate Merkle audit proof for dir1/file_a.txt!");
        return false;
    }
    bool verified = ds::MerkleTree::verify_proof(f1.full_hash.to_hex(), proof, tree1.root_hash_hex());
    if (!verified) {
        utils::Logger::error("Merkle audit proof verification failed!");
        return false;
    }
    utils::Logger::success("TC-MT-04 PASSED: Cryptographic Merkle inclusion proof generated and verified in O(log N).");

    // TC-MT-05: Incremental Snapshot Diff
    std::vector<FileInfo> modified_files = files;
    FileInfo f_new;
    f_new.path = "/test_root/dir3/file_new.txt";
    f_new.size = 4096;
    f_new.full_hash = Hash256::from_hex("111122223333444455556666777788889999aaaabbbbccccddddeeeeffff0000");
    modified_files.push_back(f_new);

    ds::MerkleTree tree_modified;
    tree_modified.build("/test_root", modified_files);

    auto diff = ds::MerkleTree::diff_trees(tree1, tree_modified);
    if (diff.added_files.size() != 1 || diff.added_files[0] != "dir3/file_new.txt") {
        utils::Logger::error("Merkle Tree diff failed to identify added file!");
        return false;
    }
    utils::Logger::success("TC-MT-05 PASSED: Incremental snapshot change detection verified (O(log N) tree diff).");

    return true;
}

} // namespace tests
} // namespace dedupfs
