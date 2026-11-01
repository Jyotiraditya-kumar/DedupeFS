#include "core/hash_engine.hpp"
#include "ds/murmur3.hpp"
#include "utils/logger.hpp"

#include <openssl/evp.h>
#include <fcntl.h>
#include <unistd.h>
#include <vector>
#include <memory>

namespace dedupfs {
namespace core {

bool HashEngine::compute_prefix_hash(FileInfo& file) {
    int fd = open(file.path.c_str(), O_RDONLY);
    if (fd < 0) {
        utils::Logger::debug("Failed to open file for prefix hash: " + file.path);
        return false;
    }

    std::vector<uint8_t> buffer(PREFIX_SAMPLE_BYTES);
    ssize_t bytes_read = read(fd, buffer.data(), PREFIX_SAMPLE_BYTES);
    close(fd);

    if (bytes_read < 0) {
        return false;
    }

    file.prefix_hash = ds::MurmurHash3::hash_buffer(buffer.data(), static_cast<size_t>(bytes_read));
    file.has_prefix_hash = true;
    return true;
}

bool HashEngine::compute_full_sha256(FileInfo& file) {
    int fd = open(file.path.c_str(), O_RDONLY);
    if (fd < 0) {
        utils::Logger::debug("Failed to open file for full SHA-256: " + file.path);
        return false;
    }

    std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)> ctx(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    if (!ctx) {
        close(fd);
        return false;
    }

    if (EVP_DigestInit_ex(ctx.get(), EVP_sha256(), nullptr) != 1) {
        close(fd);
        return false;
    }

    std::vector<uint8_t> buffer(BUFFER_CHUNK_BYTES);
    ssize_t bytes_read = 0;

    while ((bytes_read = read(fd, buffer.data(), BUFFER_CHUNK_BYTES)) > 0) {
        if (EVP_DigestUpdate(ctx.get(), buffer.data(), static_cast<size_t>(bytes_read)) != 1) {
            close(fd);
            return false;
        }
    }
    close(fd);

    if (bytes_read < 0) {
        return false; // I/O read error
    }

    unsigned int digest_len = 0;
    Hash256 result;
    if (EVP_DigestFinal_ex(ctx.get(), result.bytes.data(), &digest_len) != 1 || digest_len != 32) {
        return false;
    }

    file.full_hash = result;
    file.has_full_hash = true;
    return true;
}

Hash256 HashEngine::sha256_buffer(const uint8_t* data, size_t size) {
    std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)> ctx(EVP_MD_CTX_new(), EVP_MD_CTX_free);
    Hash256 result;
    if (!ctx) return result;

    if (EVP_DigestInit_ex(ctx.get(), EVP_sha256(), nullptr) == 1) {
        EVP_DigestUpdate(ctx.get(), data, size);
        unsigned int len = 0;
        EVP_DigestFinal_ex(ctx.get(), result.bytes.data(), &len);
    }
    return result;
}

} // namespace core
} // namespace dedupfs
