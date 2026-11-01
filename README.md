# DedupFS: High-Performance Storage Deduplication Engine

**Course:** Advanced Data Structures (M.Tech Semester 1)  
**Authors:** Aryan Ravi Zodape (206126006) & Jyotiraditya Kumar (206126014)

---

## 1. Overview
**DedupFS** is a modular C++ storage deduplication and optimization system designed to eliminate data redundancy while minimizing disk I/O. By orchestrating probabilistic data structures (**Bloom Filter**), deterministic inverted indexes (**Custom Hash Table**), and multi-tier hashing, DedupFS achieves fast duplicate identification with mathematical zero false negatives and zero data loss risk.

### Key Milestones
- **Phase 1 (60% - Review 2, Nov 2, 2026):** Multi-tier pipeline, Custom Bloom Filter, Custom Hash Table with telemetry, streaming Byte Verifier, and POSIX atomic Hard-Link Storage Optimizer.
- **Phase 2 (40% - Review 3, Nov 23, 2026):** Hierarchical Merkle Tree for $O(\log N)$ change detection, Max-Heap Priority Queue for Top-$K$ space reclamation, and compression-aware inspection.

---

## 2. Phase 1 Architecture & Data Structures

```
[ Target Directory ]
         |
         v
+--------------------------+
|  MODULE 1: FILE SCANNER  |  <-- Recursive POSIX traversal (`stat` / `std::filesystem`)
|  - Inode cycle detection |  <-- Skips already hard-linked files (st_dev, st_ino)
|  - O(1) Size Bucketing   |  <-- Files with unique sizes discarded immediately (Tier 1)
+--------------------------+
         | (Candidate size matches >= 2)
         v
+--------------------------+
|  MODULE 2: HASH ENGINE   |
|  - Tier 2: 4KB Murmur3   |  <-- Fast 128-bit prefix hash (O(1) read)
|  - Tier 3: SHA-256 Full  |  <-- Streamed cryptographic digest (candidates only)
+--------------------------+
         | (Fingerprint)
         v
+--------------------------+
| MODULE 3: BLOOM FILTER   |  <-- Dynamic bitset m = -n*ln(p)/(ln 2)^2, optimal k
|  - Double-hashing        |  <-- g_i(x) = h1(x) + i * h2(x) (mod m)
|  - O(k) membership query |  <-- Rejects ~99% of unique files without index lookup
+--------------------------+
         | (Potential duplicate)
         v
+--------------------------+
|  MODULE 4: HASH TABLE    |  <-- Primary in-memory inverted index (Fingerprint -> Files)
|  - Dynamic rehashing     |  <-- Automatically doubles buckets at load factor > 0.75
|  - Bucket telemetry      |  <-- Max chain, collisions, variance tracking
+--------------------------+
         | (Candidate duplicate found)
         v
+--------------------------+
| MODULE 5: BYTE VERIFIER  |  <-- 64KB streaming buffer comparison (memcmp)
|  - Zero Collision Risk   |  <-- Guarantees 100% data preservation
+--------------------------+
         | (Verified match)
         v
+--------------------------+
| MODULE 6: STORAGE OPT    |  <-- POSIX atomic hard-linking: link(2) + rename(2)
|  - Dry-Run / Optimize    |  <-- Transparent file paths; frees duplicate disk blocks
+--------------------------+
```

---

## 3. Directory Layout

```
DedupFS/
├── include/
│   ├── core/
│   │   ├── types.hpp              # Core structs (Hash128, Hash256, FileInfo, Stats)
│   │   ├── file_scanner.hpp       # Recursive scanner and size bucketing
│   │   ├── hash_engine.hpp        # MurmurHash3 prefix + OpenSSL SHA-256
│   │   ├── byte_verifier.hpp      # Streaming 64KB byte comparator
│   │   ├── storage_optimizer.hpp  # Atomic hard-link optimizer
│   │   └── pipeline.hpp           # End-to-end pipeline orchestrator
│   ├── ds/
│   │   ├── murmur3.hpp            # 128-bit MurmurHash3 implementation
│   │   ├── bloom_filter.hpp       # Dynamically sized bitset with double-hashing
│   │   └── hash_table.hpp         # Chained hash table with statistical diagnostics
│   └── utils/
│       ├── logger.hpp             # ANSI colored logging and formatting
│       └── metrics.hpp            # High-resolution timer and Linux RSS memory profiler
├── src/
│   ├── core/                      # Core module implementations
│   ├── ds/                        # Data structure implementations
│   ├── utils/                     # Utility implementations
│   └── main.cpp                   # CLI executable entrypoint
├── tests/
│   ├── test_bloom_filter.cpp      # Unit tests: FN=0 invariant, empirical FPR bound
│   ├── test_hash_table.cpp        # Unit tests: Rehashing, collision chains, grouping
│   ├── test_verifier_optimizer.cpp# Unit tests: 1-byte EOF mismatch, dry-run, hard links
│   ├── test_pipeline.cpp          # Integration test: End-to-end deduplication
│   └── test_runner.cpp            # Test suite runner
├── benchmarks/
│   └── dataset_generator.py       # Configurable synthetic dataset generator
├── docs/
│   └── project_proposal.md        # Comprehensive academic project proposal
├── Makefile                       # High-speed compilation & test automation
└── CMakeLists.txt                 # Modern CMake build configuration
```

---

## 4. Build & Compilation Instructions

### Quick Start (Copy-Paste Ready)
```bash
# 1. Install prerequisites (Ubuntu / Debian)
sudo apt update && sudo apt install -y build-essential libssl-dev cmake python3

# 2. Build binaries (dedupfs CLI and test_runner)
make all

# 3. Execute automated test suite
make test

# 4. Run DedupFS audit (dry-run) on a test dataset
./bin/dedupfs scan ./datasets/test_small_250MB/work

# 5. Consolidate duplicates via atomic POSIX hard links
./bin/dedupfs optimize ./datasets/test_small_250MB/work
```

---

### Prerequisites & Dependencies
DedupFS is built natively for Linux environments supporting POSIX filesystem APIs and C++17.
* **Operating System:** Linux (Ubuntu 20.04/22.04/24.04, Debian 11/12, Fedora, Arch Linux)
* **Compiler:** `g++` (version 11 or higher with full `-std=c++17` support) or `clang++` (version 12+)
* **Build Tools:** `make` (GNU Make 4.0+) or `cmake` (3.16+)
* **Libraries:** `libssl-dev` (OpenSSL cryptographic engine for hardware-accelerated SHA-256)
* **Scripting:** `python3` (for test suite generation and benchmark harnesses)

#### Installing Dependencies:
```bash
# Ubuntu / Debian / Linux Mint
sudo apt update && sudo apt install -y build-essential g++ make cmake libssl-dev python3

# Fedora / RHEL / CentOS Stream
sudo dnf install -y gcc-c++ make cmake openssl-devel python3

# Arch Linux / Manjaro
sudo pacman -S base-devel cmake openssl python
```

---

### Building with GNU Make (Recommended)
The included [`Makefile`](file:///home/jyotiraditya/CodingProjects/DedupFS/Makefile) provides high-speed parallel compilation with aggressive compiler optimizations (`-O3 -std=c++17 -Wall -Wextra`).

```bash
# Build both dedupfs CLI and test_runner binaries
make all

# Launch the decoupled Web Management UI Dashboard (http://127.0.0.1:5000)
make ui

# Parallel build across all CPU cores
make -j$(nproc)

# Display available Makefile targets
make help

# Clean all compiled object files and binaries
make clean
```
* **Output CLI Binary:** `bin/dedupfs`
* **Output Test Binary:** `bin/test_runner`

---

### Building with Modern CMake
Alternatively, DedupFS supports standard CMake builds:

```bash
# Configure release build
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release

# Compile all targets
cmake --build build -j$(nproc)
```

---

## 5. Running the Automated Test Suite (Review 2 Requirement)

Run the automated test runner verifying all data structure invariants, empirical error bounds, and storage optimizer atomicity:
```bash
# Run test suite via Makefile
make test

# Or execute test binary directly
./bin/test_runner
```

### Test Coverage Matrix (100% Pass Rate):
| Test ID | Module | Invariant / Property Tested | Status |
| :--- | :--- | :--- | :--- |
| **TC-01** | Bloom Filter | Zero False Negatives ($FN = 0$) verified across $5 \times 10^3$ keys | **PASSED** |
| **TC-02** | Bloom Filter | Empirical FPR matches theoretical design bound ($p \le 0.015$) | **PASSED** |
| **TC-03** | Bloom Filter | Dynamic bitset fill ratio calculation and `clear()` reset | **PASSED** |
| **TC-04** | Hash Table | Insertion, unique key isolation, and retrieval | **PASSED** |
| **TC-05** | Hash Table | Dynamic rehashing when load factor $\lambda > 0.75$ | **PASSED** |
| **TC-06** | Hash Table | Equivalence class grouping and wasted byte calculation | **PASSED** |
| **TC-07** | Byte Verifier | Identical file confirmation & detection of 1-byte EOF mismatch | **PASSED** |
| **TC-08** | Storage Optimizer | Dry-Run audit leaves filesystem 100% untouched | **PASSED** |
| **TC-09** | Storage Optimizer | Live hard-link consolidation unifies inodes (`st_nlink = 2`) | **PASSED** |
| **TC-10** | End-to-End | Directory scanning, multi-tier filtering, and byte savings | **PASSED** |

---

## 6. Program Execution & CLI Command Reference

### Command Syntax
```bash
./bin/dedupfs <command> <target_directory> [options]
```

### Core Subcommands
| Command | Mode | Disk Mutation | Description |
| :--- | :---: | :---: | :--- |
| `scan <dir>` | Dry-Run Audit | **None (Read-Only)** | Traverses `<dir>`, evaluates Tier 1 size bucketing, Tier 2 4KB Murmur3 prefix hashing, Tier 3 SHA-256 digests, queries the Bloom filter, indexes candidates into the Hash Table, performs 64KB streaming byte verification, and outputs potential storage reclamation telemetry. |
| `optimize <dir>` | Live Deduplication | **Consolidates Inodes** | Performs full scanning and byte verification, then atomically consolidates duplicate files via POSIX hard links (`link(2)` + `rename(2)`). Duplicate physical disk blocks are freed while preserving file paths and permissions. |
| `help` | Information | **None** | Displays CLI usage syntax, available commands, and option flags. |

---

### CLI Options & Flags
| Option Flag | Argument Type | Default Value | Description |
| :--- | :---: | :---: | :--- |
| `--dry-run` | Flag | `true` for `scan` | Enforces read-only audit mode. Scans, verifies, and reports savings without modifying any filesystem files. |
| `--verbose`, `-v` | Flag | `false` | Enables granular logging for every size bucket, prefix hash, SHA-256 computation, and Bloom filter query. |
| `--min-size <bytes>` | Integer | `1 byte` | Sets minimum file size in bytes to evaluate for deduplication. Files smaller than this threshold are skipped. |
| `--fpr <float>` | Float | `0.01` (1%) | Configures target theoretical false-positive probability ($p$) for dynamic Bloom filter bitset sizing. |
| `--help`, `-h` | Flag | - | Prints the help dialog and CLI option overview. |

---

### Step-by-Step Execution Walkthrough

#### Step 1: Performing a Safe Audit / Dry-Run
Scans a target directory and reports duplicate groups, wasted storage, and pipeline metrics without touching any files:
```bash
./bin/dedupfs scan ./datasets/test_small_250MB/work
```

#### Step 2: Verbose Diagnostic Inspection
Enables per-file debug logs tracing candidate bucketing and multi-tier hash decisions:
```bash
./bin/dedupfs scan ./datasets/test_small_250MB/work --verbose
```

#### Step 3: Filtering Small Files
To ignore tiny files (e.g. smaller than 4 KB) and focus deduplication on larger documents/media:
```bash
./bin/dedupfs scan ./datasets/test_small_250MB/work --min-size 4096
```

#### Step 4: Fine-Tuning the Bloom Filter False-Positive Rate
DedupFS dynamically computes optimal bitset size $m$ and hash functions $k$ based on `--fpr`:
```bash
# Higher precision Bloom filter with 0.1% target false-positive rate
./bin/dedupfs scan ./datasets/test_small_250MB/work --fpr 0.001
```

#### Step 5: Live Storage Optimization (Hard-Link Consolidation)
Consolidates verified duplicates into atomic POSIX hard links, freeing redundant disk space:
```bash
./bin/dedupfs optimize ./datasets/test_small_250MB/work
```

#### Step 6: Verifying Optimization & Bit-Level Integrity
Use the dataset verification harness to confirm 100% byte equivalence against the untouched `ground_truth/` copy and inspect consolidated inodes:
```bash
./benchmarks/create_test_datasets.py --verify small
```

#### Step 7: Reverting / Resetting the Workspace
Instantly reset the working directory back to its pristine, un-optimized state from `ground_truth/` in seconds:
```bash
./benchmarks/create_test_datasets.py --reset small
```

---

## 5.5 Decoupled Web Management UI & Telemetry Dashboard

DedupFS includes a modern, responsive web dashboard built with Python Flask and Tailwind CSS + Chart.js, completely decoupled from the core C++ engine.

### Launching the Web UI:
```bash
# Using Makefile
make ui

# Or using the launcher script
./run_ui.sh 5000

# Access in your browser:
# http://127.0.0.1:5000
```

### Dashboard Features:
1. **Interactive Path Selector & Presets:** Enter any custom directory path or click presets for standard benchmark tiers (Small ~280MB, Medium ~1.09GB, Large ~3.99GB).
2. **Dual Execution Options:** Trigger safe dry-run audits (**Scan**) or live atomic POSIX hard-link consolidation (**Optimize**) with live terminal output streaming.
3. **Space Usage & Savings Visualizations:**
   - **Donut Chart:** Storage distribution across file extensions (`.pdf`, `.jpg`, `.c`, `.h`, `.csv`).
   - **Bar Chart:** Physical storage reclaimed per file extension.
   - **Horizontal Bar Chart:** Space usage and savings across nested subdirectories.
4. **Algorithmic Telemetry Cards:** Real-time gauges for Bloom filter bit saturation, queries, true rejections ($FN=0$ guarantee), and Hash table load factor $\lambda$ ($\le 0.75$).
5. **Interactive Duplicate Clusters Explorer:** Searchable table of duplicate equivalence classes detailing canonical originals vs. replicas with inode numbers and link counts.

---

## 5.6 Academic Presentation Deck for the Professor

DedupFS provides a comprehensive, 13-slide academic presentation specifically designed for M.Tech course evaluations:

1. **PowerPoint Presentation File (`.pptx`):**
   - Location: [`presentation/DedupFS_MTech_Presentation.pptx`](file:///home/jyotiraditya/CodingProjects/DedupFS/presentation/DedupFS_MTech_Presentation.pptx)
   - Professional 16:9 widescreen format with dark academic palette, metric cards, mathematical formulations, and comparison tables.
   - Can be generated anytime via `python3 presentation/generate_ppt.py`.
2. **Interactive HTML5 Web Slide Deck:**
   - Location: [`presentation/index.html`](file:///home/jyotiraditya/CodingProjects/DedupFS/presentation/index.html)
   - Accessible via the Web UI at `http://127.0.0.1:5000/presentation`.
   - Full keyboard navigation (Left/Right arrows, Space, PageUp/PageDown).


---

### Understanding the Execution Telemetry Report

DedupFS outputs an execution report structured into five analytical sections:

```
========================================================
  DEDUPFS EXECUTION REPORT & TELEMETRY
========================================================

--- SCANNING & I/O SAVINGS ---
Total Files Scanned:                  9516          # Total regular files traversed
Total Raw Data Scanned:               279.63 MB     # Cumulative logical dataset volume
Unique Size Files Discarded (Tier 1): 2346 (24.7%)  # Eliminated in O(1) via size bucketing
4KB Prefix Hashes Evaluated (Tier 2): 7164          # Murmur3 128-bit prefix hashes computed
Prefix Mismatches Discarded:          2060          # Eliminated after reading only 4KB
Full SHA-256 Hashes Computed (Tier 3):5104          # Cryptographic digests computed

--- PROBABILISTIC BLOOM FILTER TELEMETRY ---
Bloom Filter Total Bits (m):          958506        # Optimal dynamic bitset size
Hash Functions Count (k):             7             # Optimal double-hashing count
Bloom Filter Fill Ratio (1-bits):     1.46%         # Bitset saturation percentage
Total Membership Queries:             5104          # Total membership checks
True Negative Rejections (O(k)):      2012          # Unique files rejected in O(k)
Reported Positives (Lookups):         3092          # Potential duplicates queried in hash table
Observed False Positives:             0             # Empirical false positives observed
Empirical False Positive Rate:        0.00e+00      # Zero false positives confirmed

--- PRIMARY HASH TABLE DIAGNOSTICS ---
Primary Index Elements:               2012          # Distinct fingerprints stored
Allocated Buckets:                    4096          # Power-of-two table capacity
Current Load Factor:                  0.491         # Load factor (rehashes at > 0.75)
Rehash Expansions:                    0             # Table growth events
Collisions in Buckets:                410           # Collisions resolved via chaining
Max Bucket Chain Length:              4             # Maximum collision chain depth
Avg Non-Empty Chain Length:           1.26          # Average chain length across occupied buckets

--- VERIFICATION & DEDUPLICATION RESULTS ---
Byte Verifications Performed:         3092          # Streaming 64KB buffer comparisons
Byte-by-Byte Confirmed Matches:       3092          # 100% verified duplicate files
Duplicate Equivalence Classes:        1999          # Unique file content groups
Redundant Duplicate Files:            3092          # Number of redundant files
Storage Savings Potential:            76.03 MB      # Space reclaimable
Actually Reclaimed Physical Storage:  76.03 MB      # Physical disk blocks freed (optimize mode)
Deduplication Ratio (DR):             1.37x         # Logical size / Physical size
Space Savings Percentage:             27.19%        # Percentage of disk capacity reclaimed

--- EXECUTION TIMING & THROUGHPUT ---
Scan Time:                            26.27 ms      # Recursive stat traversal duration
Hash & Index Time:                    169.98 ms     # Prefix, SHA-256, Bloom & Indexing duration
Optimization Time:                    179.63 ms     # Atomic hard-link creation duration
Total Runtime:                        377.38 ms     # End-to-end execution duration
Overall Throughput:                   740.96 MB/s   # Processing throughput
Peak Process Memory (RSS):            309.01 MB     # Maximum resident memory usage
```

---

## 7. Benchmark Datasets & Generation Harnesses

### 7.1 Unified Benchmark Dataset Generator (`dataset_generator.py`)
Generates and replicates realistic multi-tier benchmark workloads across:
- **Linux Kernels:** Multi-version source trees (`linux-v6.6` vs `linux-v6.7`) with organic inter-version redundancy (~75% identical C/header files).
- **zlib-ng & Silesia Compression Corpus:** Industry standard compression benchmark corpus (executables, dictionaries, database binaries, text, test data).
- **Kaggle Datasets:** Realistic tabular datasets (Credit Card Fraud with PCA features $V_1 \dots V_{28}$, E-Commerce user behavior, Telecom churn) and Enron email NLP corpora.
- **Proper Replication & Duplication:** Replicates files across realistic user topologies (`downloads/`, `backup_snapshots/`, `project_clones/`, `shared_central_repo/`) with controlled duplication ratios, multi-copy clusters, adversarial collision edge cases, and exact ground-truth manifest generation.

```bash
# Generate all workloads (Linux Kernels, zlib-ng corpus, Kaggle datasets) with 35% duplication
./benchmarks/dataset_generator.py --output-dir ./datasets/unified_benchmark --type all --dup-ratio 0.35 --copies 2

# Generate specific workload only (e.g. linux_kernel, zlib_corpus, kaggle, or synthetic)
./benchmarks/dataset_generator.py --output-dir ./datasets/kaggle_test --type kaggle --dup-ratio 0.40

# Download official upstream archives (zlib-ng release & Silesia corpus)
./benchmarks/dataset_generator.py --output-dir ./datasets/compression_test --type zlib_corpus --download

# Legacy synthetic mode (100% backward compatible)
./benchmarks/dataset_generator.py --output-dir ./test_dir --num-unique 100 --dup-ratio 0.5 --copies 2
```

### 7.2 Real-World GitHub Software Release Benchmarks (`fetch_real_world_dataset.py`)
Fetch and prepare real-world software releases with organic inter-version code redundancy:
```bash
# Download consecutive GitHub releases of curl (curl-8.4.0 vs curl-8.5.0)
./benchmarks/fetch_real_world_dataset.py --dataset curl_releases --output-dir ./datasets

# Audit duplicates on real-world codebase (7,683 files)
./bin/dedupfs scan ./datasets/curl_releases

# Consolidate duplicate files via POSIX hard links
./bin/dedupfs optimize ./datasets/curl_releases
```

#### Real-World Benchmark Results on `curl` GitHub Releases:
* **Total Files Scanned:** 7,683 files (34.68 MB)
* **Tier 1 (Size Filter):** 958 unique files discarded in $O(1)$
* **Tier 2 (4KB Prefix Hash):** 646 files eliminated without full read
* **Bloom Filter Telemetry:** 6,067 queries, 3,006 true negative rejections ($O(k)$ rejection, 0 secondary lookups), 0 false positives
* **Duplicate Equivalence Classes Found:** 2,994
* **Redundant Files Identified:** 3,061 files (9.60 MB storage saved, 27.70% deduplication ratio)
* **Total Execution Runtime:** 153.83 ms (225.43 MB/s overall throughput)

### 7.3 Large Mixed Documents & Images Benchmark (`generate_mixed_dataset.py`)
Generates and benchmarks a massive 2.5 GB realistic dataset featuring authentic documents (PDF, Markdown, CSV, JSON, HTML, TXT) and high-resolution images (BMP, PNG, PPM, SVG), organized in realistic enterprise directories (`documents/`, `media_images/`, `downloads_inbox/`, `backups_and_snapshots/`, `shared_team_assets/`, `dedup_edge_cases/`):
```bash
# Generate ~2.5 GB realistic mixed dataset (or custom size via --target-gb)
./benchmarks/generate_mixed_dataset.py --target-gb 2.5 --dup-ratio 0.35 --output-dir ./datasets/mixed_docs_images

# Audit duplicates (dry-run)
./bin/dedupfs scan ./datasets/mixed_docs_images

# Consolidate duplicate files via POSIX atomic hard links
./bin/dedupfs optimize ./datasets/mixed_docs_images
```

#### Empirical Benchmark Results on 2.51 GB Mixed Dataset:
* **Total Files Scanned:** 1,151 files (2.51 GB raw data)
* **Format Breakdown:** BMP (1.44 GB), CSV (358 MB), PDF (351 MB), PPM (285 MB), JSON (95 MB), HTML (12 MB), PNG (10 MB), DAT (8 MB), Markdown (5.8 MB), SVG (1.9 MB), TXT/Log (1.8 MB)
* **Tier 1 (Size Filter):** 176 unique size files discarded in 5.49 ms (15.3%)
* **Tier 2 (4KB Prefix Hash):** 975 evaluated, 271 prefix mismatches discarded without full read
* **Tier 3 (SHA-256 Digest):** 704 computed
* **Probabilistic Bloom Filter:** 704 queries, 294 true negative rejections, 0 observed false positives
* **Primary Hash Table:** 294 index entries, load factor 0.072, max chain length 2
* **Byte Verifier:** 410 byte-by-byte comparisons with 100% data preservation
* **Reclaimed Redundant Storage:** 945.92 MB (1.58x deduplication ratio, 36.78% space savings)
* **Total Execution Runtime:** 3.16 seconds (**813.37 MB/s overall throughput**)

### 7.4 Real-World Multi-Tier Test Suites from `raw_datasets` (`create_test_datasets.py`)
Constructs and benchmarks comprehensive test suites directly from authentic raw data (8,905 real PDF Resumes, 82,783 real COCO JPG Photos, paired Linux Kernels 6.10 & 6.11, and Curl releases), incorporating multi-folder duplication, realistic naming variants, deep directory nesting (4-6 levels), and collision edge cases.

#### Dual-Folder Architecture (`ground_truth/` & `work/`):
Each generated test dataset incorporates two independent, synchronized directory trees:
- **`ground_truth/`**: **Untouched reference copy**. Contains the original duplicate structure with independent physical disk inodes. Never modified by DedupFS.
- **`work/`**: **Active working workspace**. DedupFS scans and optimizes this directory, creating POSIX hard links and reclaiming physical disk blocks.
- **`ground_truth_manifest.json`**: Mathematical catalog of all SHA-256 fingerprints and duplicate equivalence clusters.

```bash
# Build all standard test tiers (Small ~250MB, Medium ~1.0GB, Large ~3.5GB)
./benchmarks/create_test_datasets.py --tiers small,medium,large

# Audit / scan DedupFS on the active working copy (leaves ground_truth untouched)
./bin/dedupfs scan ./datasets/test_small_250MB/work
./bin/dedupfs scan ./datasets/test_medium_1GB/work
./bin/dedupfs scan ./datasets/test_large_3.5GB/work

# Consolidate duplicates into atomic POSIX hard links
./bin/dedupfs optimize ./datasets/test_small_250MB/work

# Verify bit-for-bit data equivalence & inode consolidation against untouched ground_truth
./benchmarks/create_test_datasets.py --verify small
./benchmarks/create_test_datasets.py --verify medium
./benchmarks/create_test_datasets.py --verify large

# Instantly reset work/ to pristine pre-deduplication state from ground_truth in seconds
./benchmarks/create_test_datasets.py --reset small
./benchmarks/create_test_datasets.py --reset all
```

#### Multi-Tier Empirical Benchmark Matrix:
| Test Tier | Files Scanned | Logical Size | Unique Discarded (Tier 1) | Rehash Buckets | Duplicates Found | Reclaimed Storage | Runtime | Overall Throughput |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Small (`test_small_250MB/work`)** | 9,516 files | 279.63 MB | 2,346 (24.7%) | 4,096 | 3,092 files | 76.03 MB | 218.48 ms | **1,279.88 MB/s** |
| **Medium (`test_medium_1GB/work`)** | 23,380 files | 1.09 GB | 5,403 (23.1%) | 8,192 (1 rehash) | 9,620 files | 303.31 MB | 2.12 s | **526.79 MB/s** |
| **Large (`test_large_3.5GB/work`)** | 58,629 files | 3.99 GB | 14,133 (24.1%) | 32,768 (3 rehashes) | 24,431 files | 1.13 GB | 8.58 s | **476.62 MB/s** |




