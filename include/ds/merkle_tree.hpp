#pragma once

#include "core/types.hpp"
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>

namespace dedupfs {
namespace ds {

struct MerkleNode {
    std::string name;
    std::string relative_path;
    bool is_directory{false};
    uintmax_t size{0};
    size_t file_count{0};
    Hash256 hash{};

    std::vector<std::shared_ptr<MerkleNode>> children;

    // Helper to get hex string representation of node hash
    std::string hash_hex() const {
        return hash.to_hex();
    }
};

struct DuplicateSubtree {
    std::string hash_hex;
    std::string canonical_path;
    std::vector<std::string> replica_paths;
    uintmax_t subtree_size{0};
    size_t files_count{0};

    uintmax_t wasted_bytes() const {
        return replica_paths.size() * subtree_size;
    }
};

struct MerkleDiff {
    std::vector<std::string> added_files;
    std::vector<std::string> modified_files;
    std::vector<std::string> deleted_files;
    size_t unchanged_nodes_count{0};
    double change_ratio{0.0};
};

struct MerkleProofStep {
    std::string sibling_name;
    std::string sibling_hash_hex;
    bool is_left_sibling{false};
};

struct MerkleTreeDiagnostics {
    std::string root_hash_hex;
    size_t total_nodes{0};
    size_t leaf_files_count{0};
    size_t directory_nodes_count{0};
    size_t max_depth{0};
    size_t duplicate_subtrees_count{0};
    uintmax_t duplicate_subtree_wasted_bytes{0};
};

/**
 * Advanced Data Structure: Hierarchical Merkle Hash Tree
 * Represents filesystem hierarchy as a cryptographic hash tree.
 * Enables O(1) subtree duplicate detection, O(log N) incremental change detection
 * between storage snapshots, and tamper-proof verification proofs.
 */
class MerkleTree {
public:
    MerkleTree() = default;

    // Constructs the Merkle Tree from the scanned file catalog
    bool build(const std::string& root_path, const std::vector<FileInfo>& files);

    // Subtree duplicate detection: locates identical nested directories in O(N)
    std::vector<DuplicateSubtree> find_duplicate_subtrees() const;

    // Incremental Change Detection: diffs two snapshots in O(log N)
    static MerkleDiff diff_trees(const MerkleTree& old_tree, const MerkleTree& new_tree);

    // Cryptographic audit proof generation for a given file path
    std::vector<MerkleProofStep> generate_proof(const std::string& relative_path) const;

    // Verify proof
    static bool verify_proof(const std::string& file_hash_hex, 
                             const std::vector<MerkleProofStep>& proof, 
                             const std::string& expected_root_hex);

    // Diagnostics & Accessors
    MerkleTreeDiagnostics get_diagnostics() const;
    std::shared_ptr<MerkleNode> root() const { return root_; }
    std::string root_hash_hex() const { return root_ ? root_->hash_hex() : ""; }
    size_t total_nodes() const { return total_nodes_; }
    size_t total_leaves() const { return total_leaves_; }

    void clear();

private:
    std::shared_ptr<MerkleNode> root_{nullptr};
    std::string root_path_{""};
    size_t total_nodes_{0};
    size_t total_leaves_{0};
    size_t max_depth_{0};

    // Internal recursive builders
    void compute_hashes_recursive(const std::shared_ptr<MerkleNode>& node, size_t current_depth);
    void collect_duplicate_subtrees_recursive(
        const std::shared_ptr<MerkleNode>& node,
        std::unordered_map<std::string, std::vector<std::shared_ptr<MerkleNode>>>& hash_map) const;
};

} // namespace ds
} // namespace dedupfs
