#include "core/byte_verifier.hpp"
#include "utils/logger.hpp"

#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <vector>

namespace dedupfs {
namespace core {

bool ByteVerifier::verify_identical(const FileInfo& file1, const FileInfo& file2, DedupStats& stats) {
    stats.byte_verifications_performed++;

    if (file1.size != file2.size) {
        stats.byte_verifications_failed++;
        return false;
    }

    // Fast-path: if they have the exact same inode on the same device, they are already identical
    if (file1.device == file2.device && file1.inode == file2.inode) {
        stats.byte_verifications_matched++;
        return true;
    }

    bool matched = verify_identical_paths(file1.path, file2.path);
    if (matched) {
        stats.byte_verifications_matched++;
    } else {
        stats.byte_verifications_failed++;
        utils::Logger::warning("Byte mismatch detected between candidate files: " + file1.path + " and " + file2.path);
    }
    return matched;
}

bool ByteVerifier::verify_identical_paths(const std::string& path1, const std::string& path2) {
    int fd1 = open(path1.c_str(), O_RDONLY);
    if (fd1 < 0) return false;

    int fd2 = open(path2.c_str(), O_RDONLY);
    if (fd2 < 0) {
        close(fd1);
        return false;
    }

    std::vector<uint8_t> buf1(VERIFY_CHUNK_SIZE);
    std::vector<uint8_t> buf2(VERIFY_CHUNK_SIZE);

    bool identical = true;
    while (true) {
        ssize_t n1 = read(fd1, buf1.data(), VERIFY_CHUNK_SIZE);
        ssize_t n2 = read(fd2, buf2.data(), VERIFY_CHUNK_SIZE);

        if (n1 != n2) {
            identical = false;
            break;
        }

        if (n1 <= 0) {
            break; // EOF or error
        }

        if (std::memcmp(buf1.data(), buf2.data(), static_cast<size_t>(n1)) != 0) {
            identical = false;
            break;
        }
    }

    close(fd1);
    close(fd2);
    return identical;
}

} // namespace core
} // namespace dedupfs
