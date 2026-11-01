# M.Tech Project Proposal & Comprehensive Academic Specification

## Project Title
**DedupFS: High-Performance File Deduplication and Storage Optimization Using Advanced Data Structures**

### Candidate & Course Details
- **Student Name 1:** Aryan Ravi Zodape (Roll No: 206126006)
- **Student Name 2:** Jyotiraditya Kumar (Roll No: 206126014)
- **Degree / Semester:** M.Tech, Semester 1
- **Course:** Advanced Data Structures (ADS)
- **Review Deadlines:**
  - **First Review:** October 12th, 2026 (Problem Definition, Literature Survey, Novelty, Block Diagram, Pseudo-code, Datasets)
  - **Second Review:** November 2nd, 2026 (60% Implementation, Test Cases, Evaluation Metrics)
  - **Third & Final Review:** November 23rd, 2026 (100% Implementation, Graphs, Analysis, Comparison with Existing Work)

---

# SECTION 1: REVIEW 1 REQUIREMENTS

## 1.1 Introduction: Problem Formulation & Need

### 1.1.1 The Data Redundancy Crisis
In modern computing infrastructure—ranging from personal multi-terabyte workstations and academic computing clusters to enterprise Network-Attached Storage (NAS) and cloud backup repositories—uncontrolled data redundancy is pervasive. Studies show that between **30% and 75%** of physical disk capacity is consumed by identical duplicate files, including:
- Multiple downloads of identical datasets, documents, and software packages.
- Redundant virtual machine (VM) disk images and operating system containers.
- Unpruned multi-generational file backups and replicated project workspaces.

### 1.1.2 Why Naive Duplicate Detection Fails
Naive duplicate detection algorithms rely on pairwise comparisons:
$$\text{Comparisons} = \binom{N}{2} = \frac{N(N-1)}{2} \implies O(N^2)$$
For a modest filesystem with $N = 500,000$ files, pairwise comparison requires $\approx 1.25 \times 10^{11}$ comparisons. Even if naive hashing is used (computing a SHA-256 hash for every file from byte 0 to EOF), the system becomes completely **Disk-I/O bound**, requiring sequential reading of terabytes of data just to discover that 95% of files are completely unique.

### 1.1.3 The Need for DedupFS
There is an urgent requirement for an intelligent, multi-stage deduplication engine that combines **probabilistic filtering**, **hierarchical hashing**, and **deterministic indexing**:
1. **Minimizing Disk I/O:** Rejecting 90%+ of non-duplicate files without reading beyond their first 4KB.
2. **Sub-linear Change Detection:** Tracking directory changes across snapshots in $O(\log N)$ time rather than $O(N)$ re-scans.
3. **Guaranteed Data Integrity:** Preventing false deduplication through multi-tiered verification with zero false positives.
4. **Transparent Storage Reclamation:** Reclaiming physical sectors using POSIX hard-linking without breaking filesystem path transparency.

---

## 1.2 Literature Survey

To position DedupFS within existing academic literature, we analyze three seminal papers that established the foundations of modern deduplication, detailing their key contributions and critical drawbacks.

```
+---------------------------------------------------------------------------------------------------+
|                                  LITERATURE SURVEY COMPARISON MATRIX                              |
+---------------------------------------------------------------------------------------------------+
| Paper & Authors         | Key Contributions                   | Critical Drawbacks / Limitations  |
+-------------------------+-------------------------------------+-----------------------------------+
| 1. LBFS (SOSP 2001)     | • Introduced Content-Defined        | • High CPU overhead of Rabin      |
|    Muthitacharoen et al.|   Chunking (CDC) via Rabin          |   rolling fingerprints.           |
|                         |   fingerprints.                     | • Chunk fragmentation & large     |
|                         | • Cross-file chunk deduplication    |   metadata index tables.          |
|                         |   over low-bandwidth networks.      | • Lacks whole-file fast paths     |
|                         |                                     |   and hierarchical tree diffs.    |
+-------------------------+-------------------------------------+-----------------------------------+
| 2. DDFS / Data Domain   | • Summary Vector (in-memory Bloom   | • Heavy memory footprint for      |
|    (FAST 2008)          |   filter) to avoid disk index lookups|  stream locality caches.          |
|    Zhu, Li, Patterson   | • Stream-Informed Segment Layout    | • Coupled to proprietary backup   |
|                         |   (SISL) exploiting chunk locality. |   containers; unsuited for live   |
|                         |                                     |   POSIX hierarchical filesystems. |
+-------------------------+-------------------------------------+-----------------------------------+
| 3. Extreme Binning      | • File similarity binning using one | • Chunk-sharing blindness across  |
|    (MASCOTS 2009)       |   representative chunk fingerprint. |   different bins.                 |
|    Bhagwat et al.       | • Offloads chunk index to disk,     | • Brittle if files differ in the  |
|                         |   keeping only bin IDs in RAM.      |   chosen representative chunk.    |
|                         |                                     | • Ineffective for non-clustered,  |
|                         |                                     |   heterogeneous files.            |
+-------------------------+-------------------------------------+-----------------------------------+
```

### Detailed Paper Analysis:

#### Paper 1: *A Low-Bandwidth Network File System (LBFS)*
- **Authors:** Athicha Muthitacharoen, Benjie Chen, David Mazières (*ACM SOSP 2001*).
- **Core Contribution:** LBFS introduced Content-Defined Chunking (CDC) using Rabin sliding-window fingerprinting. By setting boundary markers based on content rather than fixed offsets, LBFS solved the "byte-shift problem," ensuring that an insertion at the start of a file does not invalidate all downstream chunk hashes.
- **Critical Drawbacks:**
  1. *Severe CPU Overhead:* Calculating polynomial rolling hashes byte-by-byte for every file consumes massive CPU cycles.
  2. *Chunk Index Explosion:* Storing indices for millions of 4KB–8KB chunks creates a secondary memory crisis.
  3. *Absence of Whole-File Hierarchical Filtering:* LBFS chunks everything indiscriminately, wasting resources on files that have completely unique sizes or headers.

#### Paper 2: *Avoiding the Disk Bottleneck in the Data Domain Deduplication File System (DDFS)*
- **Authors:** Benjamin Zhu, Kai Li, R. Hugo Patterson (*USENIX FAST 2008*).
- **Core Contribution:** Solved the "disk bottleneck" problem where chunk indices exceed available RAM. Introduced the **Summary Vector**—an in-memory Bloom filter array representing all stored chunk fingerprints—and **Stream-Informed Segment Layout (SISL)** to preserve spatial locality.
- **Critical Drawbacks:**
  1. *Enterprise Storage Specificity:* Tailored strictly for append-only streaming backup workloads; cannot be directly applied to interactive, hierarchical POSIX filesystems.
  2. *High Cache Complexity:* SISL requires significant RAM to cache full container descriptors, which degrades rapidly under random file access patterns.
  3. *No Structural Change Tracking:* DDFS does not support hierarchical Merkle verification for directory synchronization.

#### Paper 3: *Extreme Binning: Scalable, Parallel Deduplication for Chunk-based File Backups*
- **Authors:** Deepavali Bhagwat, Kave Eshghi, Darrell D. E. Long, Mark Lillibridge (*IEEE MASCOTS 2009*).
- **Core Contribution:** Addressed the index scalability problem for loosely clustered data by exploiting file similarity. For each file, a single "representative chunk fingerprint" (e.g., minimum hash) selects a discrete bin, and only that bin's index is paged into RAM.
- **Critical Drawbacks:**
  1. *Bin Boundary Blindness:* Extreme Binning deliberately ignores duplicate chunks shared between files assigned to different bins, reducing maximum deduplication efficiency.
  2. *Sensitivity to Representative Chunk Selection:* If two nearly identical files differ in the specific region where the representative chunk is selected, they are assigned to different bins and deduplication fails completely.
  3. *Unsuited for Uniform Datasets:* Works well only when datasets have natural clustering (e.g., daily incremental VM snapshots).

---

## 1.3 Block Diagram Highlighting Algorithmic Novelty

### 1.3.1 Algorithmic Novelty & Unique Contributions
DedupFS distinguishes itself from existing literature and standard utilities (`fdupes`, `jdupes`, `rmlint`) through four tightly integrated innovations:
1. **Cascaded Multi-Tier Filtering Pipeline:** Replaces eager cryptographic hashing with a 3-tier rejection funnel (Size Bucket $\to$ Fast 4KB Prefix Hash $\to$ Cryptographic SHA-256). Over 90% of files are discarded at Tier 1 and Tier 2 without reading full contents.
2. **In-Memory Bloom Pre-Filter with Parameterized Tuning:** Intercepts hash table lookups. A dynamic bit-vector with double-hashing rejects unseen fingerprints in $O(k)$ time, eliminating secondary index thrashing.
3. **Hierarchical Merkle Tree Directory Engine:** Organizes directory nodes into a Merkle DAG. When checking for duplicate subtrees or syncing across directories, identical trees are matched at the root in $O(1)$, and modified subtrees are isolated in $O(\log N)$ time.
4. **Max-Heap Prioritized Reclamation Engine:** In production environments, administrators cannot always deduplicate all files simultaneously due to I/O quotas. DedupFS orders duplicate equivalence classes by total wasted bytes:
   $$\text{WastedBytes}(G) = (|G| - 1) \times \text{Size}(G)$$
   allowing optimal Top-$K$ batch space reclamation.

### 1.3.2 System Architecture Block Diagram

```
+===================================================================================================+
|                                    DedupFS SYSTEM ARCHITECTURE                                    |
+===================================================================================================+

  [ Directory Input Path ]
             |
             v
+--------------------------+
|   MODULE 1: SCANNER      |  <-- Recursive POSIX traversal (`stat` / `std::filesystem`)
|  - Inode Cycle Check     |  <-- Avoids re-scanning already hard-linked files (st_ino, st_dev)
|  - Fast Size Grouping    |  <-- Files with unique sizes eliminated immediately (O(1))
+--------------------------+
             |
     [ Size Matches >= 2 ]
             |
             v
+--------------------------+
|  MODULE 2: HASH ENGINE   |
|  - Tier 1: Size Match    |
|  - Tier 2: 4KB Murmur3   |  <-- Fast prefix/footer hash (O(1) read)
|  - Tier 3: Full SHA-256  |  <-- Streamed cryptographic digest ONLY for candidate collisions
+--------------------------+
             |
     [ SHA-256 Fingerprint ]
             |
             v
+--------------------------+
| MODULE 3: BLOOM FILTER   |  *** ALGORITHMIC NOVELTY 1 ***
|  - Bit array of size m   |  - Double-hashing: g_i(x) = h1(x) + i * h2(x) (mod m)
|  - k hash evaluations    |  - Fast negative rejection (FN = 0)
+--------------------------+
       |             |
 [ Negative ]   [ Positive ]
       |             |
 (Unique File:       v
  Add to Index) +--------------------------+
                | MODULE 4: HASH TABLE     |  <-- Primary In-Memory Fingerprint Inverted Index
                |  - Inverted File Index   |  <-- Maps Digest -> std::vector<FileMetadata>
                |  - Dynamic Rehash        |  <-- Bucket collision telemetry & chain monitoring
                +--------------------------+
                             |
                     [ Duplicate Found ]
                             |
                             v
+------------------------------------------+
|        MODULE 5: BYTE VERIFIER           |  <-- Streaming byte-by-byte buffer comparison
|   - Zero-Loss Guarantee (64KB blocks)    |  <-- Eliminates cryptographic hash collision risk
+------------------------------------------+
                             |
                   [ Verified Duplicate ]
                             |
        +--------------------+--------------------+
        |                                         |
        v                                         v
+--------------------------+            +--------------------------+
| MODULE 6: STORAGE OPT    |            | MODULE 7: MERKLE TREE    | *** ALGORITHMIC NOVELTY 2 ***
|  - Atomic POSIX link(2)  |            |  - Hierarchical Hash DAG | - O(log N) change detection
|  - Safe Unlink & Swap    |            |  - Subtree-level dedup   | - Incremental directory sync
|  - Transparent Paths     |            +--------------------------+
+--------------------------+                          |
        |                                             |
        +--------------------+------------------------+
                             |
                             v
+--------------------------------------------------+
|      MODULE 8: MAX-HEAP PRIORITY RECLAMATION     | *** ALGORITHMIC NOVELTY 3 ***
|  - Key: WastedBytes = (Count - 1) * FileSize      | - Prioritized Top-K space reclamation
|  - Optimal reclamation under I/O time budgets    | - Reclaims maximum gigabytes in minimum ops
+--------------------------------------------------+
                             |
                             v
+--------------------------------------------------+
|        CLI REPORT & BENCHMARKING ENGINE          |
|  - Storage Reclaimed, Throughput, FP Telemetry   |
+--------------------------------------------------+
```

---

## 1.4 Algorithms & Detailed Pseudo-Code for All Modules

### 1.4.1 Module 1: File Scanner & Size Bucket Aggregator
```python
algorithm FileScanner(target_directory):
    input: target_directory path
    output: Map<FileSize, List<FilePath>> candidate_buckets

    visited_inodes = Set<InodeID>()
    size_map = Map<FileSize, List<FilePath>>()

    for entry in recursive_walk(target_directory):
        if is_regular_file(entry) and not is_symlink(entry):
            inode = get_inode(entry)
            if inode in visited_inodes:
                continue  # Already linked or scanned
            visited_inodes.insert(inode)

            file_size = get_file_size(entry)
            if file_size > 0:  # Ignore 0-byte empty files
                size_map[file_size].append(entry.path)

    # Filter out files with unique sizes (cannot be duplicates)
    candidate_buckets = Filter(size_map, lambda (size, files): len(files) >= 2)
    return candidate_buckets
```

### 1.4.2 Module 2: Multi-Tier Hashing Engine
```python
algorithm MultiTierHash(file_path):
    input: file_path
    output: FastHash prefix_hash, FullHash sha256_hash

    # Tier 2: Fast Prefix Hash (Read first 4096 bytes)
    fd = open(file_path, READ_ONLY)
    buffer = read(fd, 4096)
    prefix_hash = MurmurHash3_x64_128(buffer)
    close(fd)

    # Tier 3: Cryptographic Full SHA-256 (Invoked ONLY if prefix collides)
    sha256_context = SHA256_Init()
    fd = open(file_path, READ_ONLY)
    while (chunk = read(fd, 65536)) > 0:
        SHA256_Update(sha256_context, chunk)
    sha256_hash = SHA256_Final(sha256_context)
    close(fd)

    return (prefix_hash, sha256_hash)
```

### 1.4.3 Module 3: Bloom Filter (Probabilistic Pre-Filter)
```python
algorithm BloomFilter:
    parameters: m (bit array length), k (hash count)
    state: bit_array[0 .. m-1] initialized to 0

    procedure Insert(fingerprint):
        (h1, h2) = Decompose128Bit(fingerprint)
        for i from 0 to k - 1:
            index = (h1 + i * h2) mod m
            bit_array[index] = 1

    procedure MightContain(fingerprint) -> Boolean:
        (h1, h2) = Decompose128Bit(fingerprint)
        for i from 0 to k - 1:
            index = (h1 + i * h2) mod m
            if bit_array[index] == 0:
                return False  # Guaranteed: element has NEVER been seen
        return True           # Element probably exists (subject to false-positive rate p)
```

### 1.4.4 Module 4: Custom In-Memory Hash Table with Collision Handling
```python
algorithm FingerprintHashTable:
    state: Table of Buckets[0 .. Capacity-1], size, max_load_factor = 0.75

    procedure InsertOrLookup(fingerprint, file_record):
        bucket_idx = Hash(fingerprint) mod Capacity
        bucket = Buckets[bucket_idx]

        for item in bucket:
            if item.fingerprint == fingerprint:
                # Potential duplicate found!
                return (FOUND, item.file_list)

        # Unique fingerprint: Insert into bucket
        bucket.append(Record(fingerprint, [file_record]))
        size = size + 1
        if (size / Capacity) > max_load_factor:
            Rehash(Capacity * 2)
        return (NEW_INSERT, bucket.last().file_list)
```

### 1.4.5 Module 5: Byte-by-Byte Collision Verifier
```python
algorithm ByteVerifier(fileA, fileB):
    input: fileA, fileB paths
    output: Boolean (True if 100% identical)

    if fileA.size != fileB.size:
        return False
    if fileA.inode == fileB.inode:
        return True  # Already identical physical storage

    fdA = open(fileA, READ_ONLY)
    fdB = open(fileB, READ_ONLY)
    bufferA = AllocateBuffer(65536)
    bufferB = AllocateBuffer(65536)

    try:
        while not EOF(fdA):
            bytesReadA = read(fdA, bufferA)
            bytesReadB = read(fdB, bufferB)
            if bytesReadA != bytesReadB or memcmp(bufferA, bufferB, bytesReadA) != 0:
                return False
        return True
    finally:
        close(fdA)
        close(fdB)
```

### 1.4.6 Module 6: Storage Optimizer (Atomic Link Consolidation)
```python
algorithm StorageOptimizer(original_file, duplicate_file, dry_run):
    input: original_file, duplicate_file, dry_run flag
    output: Status (RECLAIMED / SKIPPED)

    if dry_run:
        Print("[DRY-RUN] Would hard-link:", duplicate_file, "->", original_file)
        return RECLAIMED

    temp_link_path = duplicate_file + ".tmp_dedup"
    # Step 1: Create hard link to original file
    if link(original_file, temp_link_path) != 0:
        return ERROR_LINK_FAILED

    # Step 2: Atomically rename over duplicate file
    if rename(temp_link_path, duplicate_file) != 0:
        unlink(temp_link_path)
        return ERROR_RENAME_FAILED

    # Disk blocks freed immediately by OS; paths remain intact
    return RECLAIMED
```

### 1.4.7 Module 7: Hierarchical Merkle Tree & Subtree Diffing
```python
algorithm BuildMerkleTree(directory_node):
    input: directory_node
    output: MerkleNode root

    if directory_node.is_file():
        leaf_hash = MultiTierHash(directory_node.path).sha256_hash
        return MerkleNode(type=FILE, path=directory_node.path, hash=leaf_hash)

    child_hashes = []
    children_nodes = []
    for child in directory_node.list_children_sorted():
        child_merkle = BuildMerkleTree(child)
        children_nodes.append(child_merkle)
        child_hashes.append(child_merkle.hash)

    # Merkle parent hash: SHA256(child_hash_1 || child_hash_2 || ...)
    parent_hash = SHA256(Concatenate(child_hashes))
    return MerkleNode(type=DIRECTORY, path=directory_node.path, hash=parent_hash, children=children_nodes)

algorithm DiffMerkleTrees(treeA, treeB):
    input: MerkleNode treeA, MerkleNode treeB
    output: List<DiffEvent> changes

    if treeA.hash == treeB.hash:
        return []  # ENTIRE SUBTREE IS IDENTICAL! O(1) early-exit

    if treeA.is_file and treeB.is_file:
        return [DiffEvent(MODIFIED, treeA.path, treeB.path)]

    # Recurse only into non-matching children: O(log N) average traversal
    for (childA, childB) in ZipChildren(treeA, treeB):
        if childA.hash != childB.hash:
            changes.append_all(DiffMerkleTrees(childA, childB))
    return changes
```

### 1.4.8 Module 8: Max-Heap Priority Queue for Targeted Storage Reclamation
```python
algorithm PrioritizedReclamation(duplicate_groups, top_K):
    input: duplicate_groups (List of duplicate file lists), top_K integer
    output: PriorityQueue top_savings_heap

    max_heap = MaxHeap(comparator=lambda g: (len(g.files) - 1) * g.file_size)

    for group in duplicate_groups:
        wasted_bytes = (len(group.files) - 1) * group.file_size
        max_heap.insert(PriorityNode(wasted_bytes, group))

    top_savings = []
    for i from 1 to top_K:
        if max_heap.is_empty():
            break
        top_savings.append(max_heap.extract_max())

    return top_savings
```

---

## 1.5 Datasets for Empirical Evaluation

To ensure reproducible academic evaluation, DedupFS will be evaluated across both **standard real-world public datasets** and a **controlled synthetic dataset generator**.

### 1.5.1 Real-World Public Datasets
1. **Linux Kernel Git Repository (Source Code Benchmark)**
   - **Download URL:** `https://github.com/torvalds/linux/archive/refs/tags/v6.6.tar.gz`
   - **Characteristics:** ~85,000 files, ~1.4 GB raw size.
   - **Contents:** Deeply nested C source files, header files, and build scripts. Ideal for testing directory scanning speed, Merkle tree construction, and small-file hash table performance.
2. **Ubuntu Cloud Server Base Images (Multi-Version OS Benchmark)**
   - **Download URL:** `https://cloud-images.ubuntu.com/releases/24.04/release/`
   - **Characteristics:** 2.5 GB to 10 GB across successive cloud image builds (`rootfs.tar.xz`, ISOs).
   - **Contents:** Repetitive system binaries, shared libraries, and configuration files with known 40%–60% cross-version redundancy.
3. **The Enron Email Dataset (Document / Text Benchmark)**
   - **Download URL:** `https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz`
   - **Characteristics:** ~500,000 text files across 150 users (~1.8 GB).
   - **Contents:** High duplicate ratio (chain emails, identical attachment forwards, meeting invites). Perfect for Bloom filter false-positive rate evaluation.

### 1.5.2 Synthetic Controlled Dataset Generator
A Python test harness (`benchmarks/dataset_generator.py`) will synthesize datasets under controlled parameters:
- **Duplicate Ratios:** 0%, 25%, 50%, 75%, 100%.
- **Size Distributions:** Small (<64 KB), Medium (1 MB – 10 MB), Large (>100 MB).
- **Cluster Topologies:** Dense clusters (1 file repeated 50 times) vs Sparse clusters (50 distinct pairs).

---

# SECTION 2: SPECIALIZED ANALYSIS — LIMITATIONS & COMPRESSED FILES

## 2.1 The Critical Limitation: Compressed & Encrypted Files

### 2.1.1 Problem Statement
> *Will standard file-level deduplication work when one file is an uncompressed file (`data.csv`) and another is its compressed counterpart (`data.csv.gz`), or between two differently compressed versions (`archive.tar.gz` vs `archive.tar.bz2`)?*

**Definitive Answer:**
**No.** Naive whole-file deduplication (and even standard fixed-block deduplication) **fails completely** on compressed files.

### 2.1.2 Fundamental Theoretical Causes
1. **The Avalanche Effect of Compression Algorithms:**
   Compression algorithms like DEFLATE (used in `.gz`, `.zip`, `.docx`), LZMA (used in `.xz`, `.7z`), and Zstandard utilize sliding-window Lempel-Ziv dictionary substitutions followed by entropy coding (Huffman or Range Coding). A 1-byte difference in the raw data or a slightly different compression level (e.g. `gzip -1` vs `gzip -9`) alters bit alignments completely, causing the resulting compressed bitstream to look like uncorrelated pseudo-random noise.
2. **Metadata & Timestamp Headers:**
   Standard `.tar.gz` or `.zip` archives embed modification timestamps and filesystem permissions inside container headers. Two archives generated from identical directories 5 seconds apart will produce completely different cryptographic hashes.
3. **Size Discrepancy:**
   Tier 1 of our multi-tier engine relies on file sizes. Because a 100MB file and its 30MB compressed archive have disparate sizes, they are immediately placed in different size buckets.

---

## 2.2 How Compression-Aware Deduplication Can Be Implemented

To bridge this limitation, we formulate three architectural solutions that extend DedupFS:

```
+-----------------------------------------------------------------------------------+
|              PROPOSED DECOMPRESS-ON-INSPECT NORMALIZATION PIPELINE                |
+-----------------------------------------------------------------------------------+

   [ File Ingest: data.csv.gz ]
                |
                v
  +---------------------------+
  | Container Format Detector |  <-- Magic byte inspection:
  |  (Gzip, Zip, Tar, Zstd)   |      0x1F 0x8B -> Gzip, 0x50 0x4B 0x03 0x04 -> Zip
  +---------------------------+
                |
        [ Compressed? ]
        /             \
   (Yes)               (No)
     |                   |
     v                   v
+----------------+   +----------------+
| Streaming      |   | Raw Stream     |
| Decompressor   |   | (Direct Feed)  |
| (zlib/libdefl) |   +----------------+
+----------------+           |
     |                       |
     +-----------+-----------+
                 |
                 v
+---------------------------------+
| Canonical Content Fingerprint   |  <-- SHA-256 computed on UNCOMPRESSED stream!
|  (Raw Inverted Hash Table)      |  <-- Matches identical uncompressed files
+---------------------------------+
```

### Approach 1: Normalized Decompress-on-Inspect (Canonical Fingerprinting)
1. **Magic-Byte Sniffing:** The scanner reads the first 4 bytes of each file to detect known compression signatures (`1F 8B` for Gzip, `42 5A 68` for Bzip2, `FD 37 7A 58 5A 00` for XZ, `50 4B 03 04` for Zip/DOCX).
2. **Streaming Decompression:** Rather than decompressing to disk, DedupFS pipes the file through a lightweight in-memory streaming decompressor (e.g., `libdeflate` or `zlib`).
3. **Canonical Hash Generation:** The SHA-256 fingerprint is calculated over the **decompressed stream**. 
4. **Result:** An uncompressed file (`data.csv`) and its compressed version (`data.csv.gz`) yield identical canonical hashes, allowing the system to recognize them as semantic duplicates.

### Approach 2: Deduplicate-Before-Compress Architecture
In enterprise backup systems (e.g., BorgBackup, ZFS, restic):
- Ingested files are split into blocks and deduplicated *first*.
- Compression is applied *only to unique blocks* immediately before committing them to disk.
- This guarantees 100% deduplication efficiency without compression interference.

### Approach 3: Content-Defined Chunking (CDC) with Sub-Stream Delta Compression
For archive files that share 90% common data but have differing headers:
- Files are chunked using **FastCDC** (variable chunk boundaries based on content patterns).
- Common interior chunks match identical files, while divergent header blocks are stored as lightweight delta patches.

---

# SECTION 3: REVIEW 2 REQUIREMENTS (DUE NOV 2, 2026 — 60% MILESTONE)

## 3.1 60% Implementation Deliverables
By November 2nd, 2026, the core engine and primary data structures will be fully operational:

1. **Scaffold & Build System:** Modern C++17 modular repository with `Makefile` and `CMakeLists.txt` configured with `-Wall -Wextra -O3`.
2. **Module 1 (File Scanner):** Recursive POSIX directory traversal with inode caching to avoid re-hashing hard-linked files, and size-bucket pre-filtering.
3. **Module 2 (Multi-Tier Hash Engine):**
   - Tier 1: Size grouping.
   - Tier 2: 4KB MurmurHash3 header/footer fast hashing.
   - Tier 3: Cryptographic SHA-256 hashing.
4. **Module 3 (Custom Bloom Filter):**
   - Dynamic bit-vector with mathematical sizing ($m = -\frac{n \ln p}{(\ln 2)^2}$).
   - Kirsch-Mitzenmacher double-hashing ($g_i(x) = h_1(x) + i \cdot h_2(x) \pmod m$).
   - Telemetry module tracking true rejects and false positives.
5. **Module 4 (Custom Hash Table Index):**
   - In-memory fingerprint table with dynamic load-factor management ($< 0.75$).
   - Bucket distribution and collision diagnostic metrics.
6. **Module 5 & 6 (Byte Verifier & Storage Optimizer):**
   - Streaming 64KB byte-level verification to prevent hash collision data loss.
   - Atomic POSIX hard-link consolidation (`link(2)` and `rename(2)`).
7. **Phase 1 CLI Tool:** Full command line interface supporting:
   ```bash
   ./dedupfs scan --path /target/dir --dry-run
   ./dedupfs optimize --path /target/dir
   ```

---

## 3.2 Formal Test Cases for Phase 1 Validation

| Test ID | Category | Test Description | Expected Behavior |
| :--- | :--- | :--- | :--- |
| **TC-01** | Unit: Bloom Filter | Insert $10^5$ random fingerprints; query $10^5$ known items. | **Zero False Negatives ($FN = 0$):** All inserted items must return `True`. |
| **TC-02** | Unit: Bloom Filter | Query $10^5$ unseen keys at $p = 0.01$ theoretical design. | Empirical false-positive rate must satisfy $FPR \le 0.015$. |
| **TC-03** | Unit: Hash Table | Insert $10^5$ entries causing load factor $> 0.75$. | Table automatically rehashes, doubling capacity; lookup remains $O(1)$. |
| **TC-04** | Unit: Verifier | Compare two 500MB files identical except for 1 byte at EOF. | Verifier detects mismatch; rejects duplicate claim; zero data corruption. |
| **TC-05** | Integration | Run `--dry-run` on directory with known duplicate clusters. | Correctly identifies duplicate files, reports exact wasted bytes, leaves disk unchanged. |
| **TC-06** | Integration | Run `--optimize` on test directory. | Redundant files replaced with hard links (`st_nlink > 1`, identical `st_ino`), physical space reclaimed. |
| **TC-07** | Boundary | Directory with empty (0-byte) files, circular symlinks, and permission restrictions. | Graceful error handling without crashes, infinite loops, or false deduplication. |

---

## 3.3 Evaluation Metrics for Phase 1

1. **Deduplication Ratio ($DR$):**
   $$DR = \frac{\text{Total Logical Size of Scanned Files}}{\text{Total Physical Size After Deduplication}}$$
2. **Space Savings Percentage ($S$):**
   $$S = \left( 1 - \frac{1}{DR} \right) \times 100\%$$
3. **Throughput ($\text{MB/s}$):**
   $$\text{Throughput} = \frac{\text{Total Megabytes Scanned}}{\text{Total Elapsed Execution Time (seconds)}}$$
4. **Bloom Filter Rejection Efficiency ($\eta$):**
   $$\eta = \frac{\text{Lookups Avoided by Bloom Filter}}{\text{Total Unique Files}} \times 100\%$$
5. **Empirical False Positive Rate ($FPR_{emp}$):**
   $$FPR_{emp} = \frac{\text{False Positives Observed}}{\text{Total True Negative Queries}}$$
   Compared against theoretical bound: $FPR_{theo} \approx (1 - e^{-kn/m})^k$.

---

# SECTION 4: REVIEW 3 REQUIREMENTS (DUE NOV 23, 2026 — 100% FINAL MILESTONE)

## 4.1 100% Implementation Deliverables
By November 23rd, 2026, the complete system with advanced hierarchical data structures and analytical optimization will be delivered:

1. **Module 7 (Hierarchical Merkle Tree Engine):**
   - Recursive Merkle DAG builder over directory structures.
   - Incremental $O(\log N)$ tree diffing engine for snapshot synchronization.
   - Whole-subtree matching (instantaneous identical directory recognition).
2. **Module 8 (Max-Heap Priority Reclamation Engine):**
   - Max-Heap ordering duplicate clusters by total recoverable bytes: $(Count - 1) \times Size$.
   - CLI Top-$K$ command:
     ```bash
     ./dedupfs topk --path /target/dir --k 10 --reclaim
     ```
3. **Format-Aware Inspection Extension:**
   - Sniffer module for `.gz` / `.zip` formats with transparent decompressed stream hashing.
4. **Comprehensive Benchmarking & Profiling Suite:**
   - Automated scripts executing scaling runs from 100MB to 10GB.
   - Cache-miss and memory footprint profiling using `valgrind --tool=massif` and `perf`.

---

## 4.2 Performance Graphs & Experimental Visualizations

The final thesis documentation will feature five publication-grade comparative graphs:

1. **Graph 1: Throughput vs Dataset Size (Linear Scaling):**
   - Compares naive pairwise comparison ($O(N^2)$), full SHA-256 scanning, and DedupFS multi-tier pipeline.
   - Expected result: DedupFS maintains near-constant processing throughput ($> 150 \text{ MB/s}$), whereas naive approaches collapse exponentially.
2. **Graph 2: Bloom Filter FPR vs Bits-per-Element ($m/n$):**
   - Plots empirical FPR against theoretical curve across $m/n \in [4, 16]$.
   - Validates that $m/n = 10$ yields $p \approx 0.008$ (under 1% false positives).
3. **Graph 3: Execution Time Breakdown by Module:**
   - Stacked bar chart showing time spent in: File Traversal vs Tier 2 Fast Hashing vs Tier 3 Cryptographic Hashing vs Bloom Filter vs Disk Linking.
4. **Graph 4: Merkle Tree Differential Synchronization Latency:**
   - Plots time taken to detect single-file modifications in a 100,000-file directory:
   - Full Recursive Re-scan ($O(N)$) vs Merkle Tree Diffing ($O(\log N)$).
5. **Graph 5: Top-$K$ Priority Reclamation Efficiency:**
   - Cumulative space reclaimed vs number of equivalence classes processed.
   - Demonstrates that reclaiming the top 10% of duplicate clusters yields over 70% of total possible storage recovery.

---

## 4.3 Analysis of Results & Theoretical Rationale

The final report will provide comprehensive analysis explaining why the data structures performed as observed:
- **I/O Reduction Analysis:** Quantification of disk block reads avoided due to the 4KB prefix hash and Bloom filter.
- **Cache Locality:** Analysis of memory layout optimizations in the custom hash table that minimized CPU L2/L3 cache misses.
- **Merkle Tree Proofs:** Formal time complexity derivation for Merkle tree construction ($O(N)$) and path verification ($O(d) = O(\log N)$).

---

## 4.4 Systematic Comparison with Existing Work

| Feature / Metric | GNU `fdupes` | `jdupes` | `rmlint` | BorgBackup | **DedupFS (Our Work)** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Language** | C | C | C | Python / C | **Modern C++17** |
| **Pre-Filter DS** | None (pairwise size) | Size buckets only | Non-cryptographic hash | In-memory hashtable | **Bloom Filter ($O(k)$ rejection)** |
| **Primary Index** | Red-Black Tree | Chained Hash Table | Custom Hash Map | Chunk index | **Custom Hash Table with telemetry** |
| **Hierarchical Diff**| None | None | None | None | **Merkle Tree ($O(\log N)$ diffing)** |
| **Prioritized Space Reclamation** | None (FIFO) | None (FIFO) | None | None | **Max-Heap (Top-$K$ Wasted Bytes)** |
| **Safety Verification** | Byte-by-byte | Byte-by-byte | Byte-by-byte / Optional | SHA-256 trust only | **Multi-tier + Streaming Byte-by-Byte** |
| **Atomic POSIX Links**| Manual prompt | Supported | Generates shell script | Proprietary repository | **Built-in Atomic Hard-Linking** |
| **Compressed File Awareness** | No | No | No | Yes (Chunk-level) | **Decompress-on-inspect architecture** |
