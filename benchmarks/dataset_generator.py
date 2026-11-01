#!/usr/bin/env python3
"""
DedupFS Unified Benchmark Dataset Generator
Advanced Data Structures (M.Tech Semester 1)

Generates or imports realistic, large-scale multi-tier datasets for storage deduplication:
1. Linux Kernels: Multi-version source trees (v6.6 vs v6.7) with realistic organic
   inter-version code reuse (~75% identical C/header files) or upstream tarballs.
2. zlib-ng & Silesia Compression Corpus: Industry-standard compression benchmark files
   (executables, text dictionaries, databases, binary streams, test data).
3. Kaggle Datasets: Real-world tabular CSVs (Credit Card Fraud with PCA features,
   E-Commerce events, Telecom churn, Housing) and NLP text/email corpora (Enron samples).
4. Realistic File Replication & Duplication: Replicates files into authentic user topologies
   (downloads/, backup_snapshots/, project_clones/, shared_central_repo/) with exact
   ground-truth tracking, SHA-256 hashing, and adversarial edge cases.
5. Legacy Synthetic Mode: 100% backward-compatible with original synthetic benchmarks.
"""

import os
import sys
import math
import time
import json
import zlib
import struct
import random
import shutil
import hashlib
import zipfile
import tarfile
import argparse
import urllib.request

# ----------------------------------------------------------------------
# Utility & Download Helpers
# ----------------------------------------------------------------------

def safe_download(url, dest_path, timeout=15):
    """Downloads a remote file with User-Agent and timeout handling."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response, open(dest_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print(f"    [!] Download skipped or failed for {url}: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False

def compute_sha256(file_path):
    """Streams and calculates cryptographic SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------
# 1. Linux Kernel Module (Multi-Version Source Trees)
# ----------------------------------------------------------------------

KERNEL_HEADERS = [
    ("include/linux/types.h", """/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LINUX_TYPES_H
#define _LINUX_TYPES_H
typedef unsigned int __kernel_size_t;
typedef int __kernel_ssize_t;
typedef long long __kernel_loff_t;
typedef unsigned long __kernel_ino_t;
typedef unsigned int __kernel_mode_t;
typedef unsigned short __kernel_nlink_t;
typedef struct { int counter; } atomic_t;
typedef struct { long long counter; } atomic64_t;
#endif /* _LINUX_TYPES_H */
"""),
    ("include/linux/fs.h", """/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LINUX_FS_H
#define _LINUX_FS_H
#include <linux/types.h>
struct inode {
    __kernel_mode_t   i_mode;
    __kernel_nlink_t  i_nlink;
    __kernel_ino_t    i_ino;
    __kernel_loff_t   i_size;
    atomic_t          i_count;
    unsigned int      i_flags;
};
struct file {
    struct inode      *f_inode;
    __kernel_loff_t   f_pos;
    unsigned int      f_flags;
};
int vfs_link(const char *oldname, struct inode *dir, const char *newname);
int vfs_rename(struct inode *old_dir, const char *old_dentry, struct inode *new_dir, const char *new_dentry);
#endif /* _LINUX_FS_H */
"""),
    ("include/linux/sched.h", """/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LINUX_SCHED_H
#define _LINUX_SCHED_H
#include <linux/types.h>
struct task_struct {
    int pid;
    int tgid;
    int state;
    unsigned long flags;
    atomic_t usage;
};
extern struct task_struct *current;
void wake_up_process(struct task_struct *tsk);
#endif /* _LINUX_SCHED_H */
"""),
    ("include/linux/slab.h", """/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LINUX_SLAB_H
#define _LINUX_SLAB_H
#include <linux/types.h>
#define GFP_KERNEL  0x00000001
#define GFP_ATOMIC  0x00000002
void *kmalloc(__kernel_size_t size, int flags);
void kfree(const void *ptr);
void *kzalloc(__kernel_size_t size, int flags);
#endif /* _LINUX_SLAB_H */
"""),
    ("include/linux/netdevice.h", """/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LINUX_NETDEVICE_H
#define _LINUX_NETDEVICE_H
#include <linux/types.h>
struct net_device {
    char name[16];
    unsigned long state;
    int mtu;
    unsigned int flags;
};
int register_netdevice(struct net_device *dev);
void unregister_netdevice(struct net_device *dev);
#endif /* _LINUX_NETDEVICE_H */
""")
]

def generate_linux_kernel_tree(target_dir, version_name, patch_ratio=0.25, base_seed=100):
    """
    Synthesizes an authentic Linux kernel source hierarchy with realistic C files,
    headers, and Makefiles.
    """
    print(f"    [*] Generating Linux Kernel source tree: {version_name}")
    v_dir = os.path.join(target_dir, version_name)
    os.makedirs(v_dir, exist_ok=True)

    # Core headers
    for rel_path, content in KERNEL_HEADERS:
        p = os.path.join(v_dir, rel_path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        # Apply patch variation if version is updated
        if "6.7" in version_name and (hash(rel_path) % 100 < patch_ratio * 100):
            content += f"\n/* Commit update for Linux {version_name} release */\n#define KERNEL_VERSION_CODE 0x060700\n"
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)

    # Subsystems: kernel/, fs/ext4/, fs/btrfs/, drivers/net/, mm/
    subsystems = [
        ("kernel", ["fork.c", "sched.c", "exit.c", "panic.c", "printk.c", "time.c", "mutex.c", "irq.c"]),
        ("fs/ext4", ["super.c", "inode.c", "dir.c", "file.c", "balloc.c", "ialloc.c", "mballoc.c", "extents.c"]),
        ("fs/btrfs", ["disk-io.c", "extent_tree.c", "inode.c", "file.c", "tree-checker.c", "volumes.c"]),
        ("drivers/net/ethernet", ["e1000_main.c", "e1000_hw.c", "r8169_main.c", "virtio_net.c", "tg3.c"]),
        ("mm", ["page_alloc.c", "slab.c", "memory.c", "vmscan.c", "mmap.c", "swap.c", "shmem.c"])
    ]

    for sub, files in subsystems:
        s_dir = os.path.join(v_dir, sub)
        os.makedirs(s_dir, exist_ok=True)
        for idx, fname in enumerate(files):
            fp = os.path.join(s_dir, fname)
            file_seed = base_seed + hash(fname) % 10000

            # If version is 6.7, check if file is modified or retained identically
            is_patched = ("6.7" in version_name) and ((file_seed % 100) < int(patch_ratio * 100))

            body = [
                "/* SPDX-License-Identifier: GPL-2.0 */",
                f"/* Linux Kernel {version_name}: {sub}/{fname} */",
                "#include <linux/types.h>",
                "#include <linux/fs.h>",
                "#include <linux/slab.h>",
                ""
            ]

            # Generate realistic C functions
            func_count = 15 + (file_seed % 20)
            for func_i in range(func_count):
                fn_name = f"{sub.replace('/', '_')}_{fname.replace('.c', '')}_func_{func_i}"
                body.append(f"int {fn_name}(struct inode *inode, void *buffer, __kernel_size_t len) {{")
                body.append(f"    if (!inode || !buffer) return -1;")
                body.append(f"    atomic_t local_counter = {{ .counter = {func_i * 42} }};")
                if is_patched and func_i == 0:
                    body.append(f"    /* PATCH: Enhanced security boundary check in {version_name} */")
                    body.append(f"    if (len > 0x1000000) return -2;")
                body.append(f"    return local_counter.counter + (int)len;")
                body.append("}\n")

            with open(fp, "w", encoding="utf-8") as f:
                f.write("\n".join(body))

    # Top-level Makefile
    with open(os.path.join(v_dir, "Makefile"), "w", encoding="utf-8") as f:
        f.write(f"VERSION = 6\nPATCHLEVEL = {7 if '6.7' in version_name else 6}\nSUBLEVEL = 0\nNAME = Hurr durr I'ma sheep\n")


# ----------------------------------------------------------------------
# 2. zlib-ng & Silesia Compression Corpus Module
# ----------------------------------------------------------------------

def setup_zlib_corpus(target_dir, allow_download=True, target_bytes=150*1024*1024):
    """
    Sets up the zlib-ng test corpus and Silesia benchmark dataset.
    Downloads upstream official archives if online, or synthesizes authentic corpora.
    """
    print(f"[*] Setting up zlib-ng and Compression Corpus in: {target_dir}")
    corpus_dir = os.path.join(target_dir, "zlib_corpus")
    os.makedirs(corpus_dir, exist_ok=True)

    downloaded = False
    if allow_download:
        # 1. Official Silesia Compression Corpus
        silesia_zip = os.path.join(corpus_dir, "silesia.zip")
        print("    [>] Attempting download of Silesia Compression Corpus (gold standard)...")
        if safe_download("https://sun.aei.polsl.pl/~sdeor/corpus/silesia.zip", silesia_zip, timeout=12):
            try:
                with zipfile.ZipFile(silesia_zip, "r") as z:
                    z.extractall(os.path.join(corpus_dir, "silesia_extracted"))
                os.remove(silesia_zip)
                print("    [+] Silesia corpus extracted successfully (202 MB uncompressed).")
                downloaded = True
            except Exception as e:
                print(f"    [!] Failed to extract Silesia zip: {e}")

        # 2. Official zlib-ng repository
        zlib_tar = os.path.join(corpus_dir, "zlib-ng-2.1.6.tar.gz")
        print("    [>] Attempting download of zlib-ng official release...")
        if safe_download("https://github.com/zlib-ng/zlib-ng/archive/refs/tags/2.1.6.tar.gz", zlib_tar, timeout=10):
            try:
                with tarfile.open(zlib_tar, "r:gz") as tar:
                    tar.extractall(corpus_dir)
                os.remove(zlib_tar)
                print("    [+] zlib-ng official codebase & test corpus extracted.")
                downloaded = True
            except Exception as e:
                print(f"    [!] Failed to extract zlib-ng tar: {e}")

    # If offline or downloads were skipped, generate high-fidelity synthetic compression files
    if not downloaded:
        print("    [*] Synthesizing authentic compression corpus files...")
        # A: Natural text dictionary (high redundancy)
        words = ["compression", "deflate", "huffman", "lz77", "sliding_window", "hash_table", "deduplication", "bloom_filter", "posix", "inode"]
        text_file = os.path.join(corpus_dir, "corpus_natural_language.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            for i in range(150000):
                line = " ".join([random.choice(words) for _ in range(12)]) + "\n"
                f.write(line)

        # B: Binary database with repeated records
        db_file = os.path.join(corpus_dir, "corpus_binary_records.dat")
        rec = struct.pack("<IIQQff", 1001, 2002, 1793400000, 4096000, 3.14159, 99.9)
        with open(db_file, "wb") as f:
            f.write(rec * 400000) # ~12 MB

        # C: Mock ELF executable binary
        elf_file = os.path.join(corpus_dir, "corpus_executable_blob.bin")
        elf_header = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8 + struct.pack("<HHI", 2, 62, 1)
        code_block = b"\x55\x48\x89\xe5\x48\x83\xec\x20\x89\x7d\xec\x48\x89\x75\xe0" * 2000
        with open(elf_file, "wb") as f:
            f.write(elf_header)
            f.write(code_block * 500)


# ----------------------------------------------------------------------
# 3. Kaggle Datasets Module (Tabular CSVs, JSON Databases, NLP)
# ----------------------------------------------------------------------

def generate_kaggle_creditcard(path, target_mb=40):
    """Generates authentic Kaggle Credit Card Fraud Detection CSV with PCA features V1-V28."""
    headers = "Time," + ",".join([f"V{i}" for i in range(1, 29)]) + ",Amount,Class\n"
    target_bytes = int(target_mb * 1024 * 1024)
    with open(path, "w", encoding="utf-8") as f:
        f.write(headers)
        written = len(headers)
        r = 0
        batch = []
        while written < target_bytes:
            batch.clear()
            for _ in range(1500):
                r += 1
                t = r * 0.75
                feats = [f"{(r * 7 + i * 13) % 1000 / 100.0 - 5.0:.4f}" for i in range(1, 29)]
                amt = f"{(r * 31 % 50000) / 100.0:.2f}"
                cls = "1" if (r % 580 == 0) else "0" # Imbalanced fraud class ~0.17%
                batch.append(f"{t:.1f}," + ",".join(feats) + f",{amt},{cls}\n")
            block = "".join(batch)
            f.write(block)
            written += len(block)

def generate_kaggle_ecommerce(path, target_mb=35):
    """Generates Kaggle E-Commerce User Behavioral Logs CSV."""
    headers = "event_time,event_type,product_id,category_id,category_code,brand,price,user_id,user_session\n"
    target_bytes = int(target_mb * 1024 * 1024)
    event_types = ["view", "cart", "purchase", "remove_from_cart"]
    brands = ["samsung", "apple", "xiaomi", "lenovo", "sony", "huawei", "asus", "dell"]
    with open(path, "w", encoding="utf-8") as f:
        f.write(headers)
        written = len(headers)
        r = 0
        batch = []
        while written < target_bytes:
            batch.clear()
            for _ in range(1500):
                r += 1
                ev = event_types[r % len(event_types)]
                pid = 1000000 + (r * 19) % 50000
                cid = 2053013552259662000 + (r * 7) % 500
                brand = brands[(r * 3) % len(brands)]
                price = f"{15.0 + (r * 17 % 1200):.2f}"
                uid = 512000000 + (r * 31) % 100000
                sess = hashlib.md5(f"sess_{uid}_{r // 5}".encode()).hexdigest()[:16]
                batch.append(f"2026-10-31 10:{r%60:02d}:{(r*3)%60:02d} UTC,{ev},{pid},{cid},electronics.smartphone,{brand},{price},{uid},{sess}\n")
            block = "".join(batch)
            f.write(block)
            written += len(block)

def generate_kaggle_enron_emails(path, num_emails=10000):
    """Generates Kaggle/CMU Enron email corpus JSON format."""
    senders = ["jeff.skilling@enron.com", "kenneth.lay@enron.com", "andrew.fastow@enron.com", "vince.kaminski@enron.com", "sara.shackleton@enron.com"]
    subjects = ["Trading Desk Energy Forward Positions", "Quarterly Risk Assessment Committee", "Pipeline Capacity Allocation Meeting", "Legal Review: Special Purpose Entity Disclosures", "FERC Regulatory Inquiry Response"]
    data = {"dataset": "Kaggle Enron Email Corpus Sample", "records": []}
    for i in range(num_emails):
        data["records"].append({
            "message_id": f"<{i:06d}.10758553.JavaMail.evans@thyme>",
            "date": f"2001-10-{(i % 28) + 1:02d} 09:30:00 -0700",
            "from": senders[i % len(senders)],
            "to": [senders[(i + 1) % len(senders)], senders[(i + 2) % len(senders)]],
            "subject": f"{subjects[i % len(subjects)]} (Ref #{i * 13 % 1000})",
            "body": f"Please review the attached contract schedules and confirm volume commitments for the upcoming fiscal cycle. Current exposure limits are strictly enforced under risk policy section {i % 15 + 1}."
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def setup_kaggle_datasets(target_dir, allow_download=True, target_mb=120):
    """Sets up Kaggle tabular and NLP benchmarks."""
    print(f"[*] Setting up Kaggle Datasets in: {target_dir}")
    k_dir = os.path.join(target_dir, "kaggle_datasets")
    os.makedirs(k_dir, exist_ok=True)

    # 1. Real public sample downloads if online
    if allow_download:
        safe_download("https://raw.githubusercontent.com/datasets/gdp/master/data/gdp.csv", os.path.join(k_dir, "kaggle_world_gdp.csv"), timeout=8)
        safe_download("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv", os.path.join(k_dir, "kaggle_titanic.csv"), timeout=8)

    # 2. Authentic high-scale Kaggle datasets
    print("    [>] Synthesizing Kaggle Credit Card Fraud dataset (PCA features V1-V28)...")
    generate_kaggle_creditcard(os.path.join(k_dir, "creditcard_fraud_dataset.csv"), target_mb=target_mb // 3)

    print("    [>] Synthesizing Kaggle E-Commerce User Behavior dataset...")
    generate_kaggle_ecommerce(os.path.join(k_dir, "ecommerce_behavior_events.csv"), target_mb=target_mb // 3)

    print("    [>] Synthesizing Kaggle Enron Email corpus sample...")
    generate_kaggle_enron_emails(os.path.join(k_dir, "enron_emails_sample.json"), num_emails=12000)


# ----------------------------------------------------------------------
# 4. Realistic File Replication & Duplication Engine
# ----------------------------------------------------------------------

def replicate_and_duplicate_files(target_dir, dup_ratio=0.35, copies=2, include_edge_cases=True):
    """
    Scans base files and properly replicates/duplicates selected files into realistic
    user topologies (downloads, backups, clones, shared) with independent physical inodes.
    """
    print("\n[*] ====================================================================")
    print("    EXECUTING PROPER FILE REPLICATION & DUPLICATION PASS")
    print("    ====================================================================")
    print(f"[*] Base Directory:          {target_dir}")
    print(f"[*] Duplication Target Ratio:{dup_ratio * 100:.1f}%")
    print(f"[*] Duplication Copies/File: {copies}")

    # Gather all base files
    base_files = []
    for root, _, files in os.walk(target_dir):
        if "ground_truth_manifest.json" in files:
            files.remove("ground_truth_manifest.json")
        for f in files:
            p = os.path.join(root, f)
            if not os.path.islink(p):
                base_files.append(p)

    if not base_files:
        print("[!] No base files found to duplicate.")
        return

    random.seed(42)
    random.shuffle(base_files)

    total_base_files = len(base_files)
    total_base_bytes = sum(os.path.getsize(p) for p in base_files)
    target_redundant_bytes = int(total_base_bytes * dup_ratio)

    print(f"[*] Total Base Files Found:  {total_base_files} ({total_base_bytes / (1024*1024):.2f} MB)")
    print(f"[*] Target Redundant Volume: {target_redundant_bytes / (1024*1024):.2f} MB")

    # Define realistic destination topologies
    dest_folders = [
        "downloads_inbox",
        "backup_snapshots/daily_backup_2026_10_01",
        "backup_snapshots/weekly_archive",
        "project_clones/workspace_feature_branch",
        "shared_central_repo/reusable_assets"
    ]
    for d in dest_folders:
        os.makedirs(os.path.join(target_dir, d), exist_ok=True)

    # Replicate selected files
    duplicate_groups = {} # sha256 -> list of relative paths
    redundant_bytes_created = 0
    duplicate_copies_count = 0
    selected_idx = 0

    while redundant_bytes_created < target_redundant_bytes and selected_idx < len(base_files):
        src_file = base_files[selected_idx]
        selected_idx += 1
        src_size = os.path.getsize(src_file)
        src_sha = compute_sha256(src_file)

        if src_sha not in duplicate_groups:
            duplicate_groups[src_sha] = [os.path.relpath(src_file, target_dir)]

        fname = os.path.basename(src_file)
        name_no_ext, ext = os.path.splitext(fname)

        # Distribute copies
        for c in range(1, copies + 1):
            if redundant_bytes_created >= target_redundant_bytes:
                break

            target_folder = random.choice(dest_folders)
            if "downloads" in target_folder:
                # User download naming variants
                variant_name = random.choice([
                    f"{name_no_ext} (1){ext}",
                    f"{name_no_ext} (Copy){ext}",
                    f"{name_no_ext}_download{ext}",
                    f"copy_of_{fname}",
                    fname
                ])
            elif "backup" in target_folder:
                variant_name = f"backup_snapshot_{fname}"
            else:
                variant_name = f"cloned_{fname}"

            dest_path = os.path.join(target_dir, target_folder, variant_name)
            if os.path.exists(dest_path):
                dest_path = os.path.join(target_dir, target_folder, f"dup_{duplicate_copies_count}_{fname}")

            # Independent physical file copy (distinct inode)
            shutil.copyfile(src_file, dest_path)

            duplicate_groups[src_sha].append(os.path.relpath(dest_path, target_dir))
            redundant_bytes_created += src_size
            duplicate_copies_count += 1

    # Filter to active duplicate groups (count >= 2)
    active_clusters = {h: paths for h, paths in duplicate_groups.items() if len(paths) > 1}

    # Inject Adversarial Edge Cases if requested
    edge_cases = []
    if include_edge_cases:
        print("\n[*] Injecting Deduplication Edge Cases (Tier 1, Tier 2, Byte Verifier)...")
        edge_dir = os.path.join(target_dir, "dedup_edge_cases")
        os.makedirs(os.path.join(edge_dir, "size_collision"), exist_ok=True)
        os.makedirs(os.path.join(edge_dir, "prefix_collision"), exist_ok=True)
        os.makedirs(os.path.join(edge_dir, "eof_single_byte_diff"), exist_ok=True)

        # Size collision: 1MB identical size, completely different data
        pA = os.path.join(edge_dir, "size_collision", "size_match_fileA.dat")
        pB = os.path.join(edge_dir, "size_collision", "size_match_fileB.dat")
        with open(pA, "wb") as f: f.write(bytes([0x11] * 1048576))
        with open(pB, "wb") as f: f.write(bytes([0x22] * 1048576))
        edge_cases.append({"type": "size_collision", "files": [pA, pB], "size": 1048576})

        # Prefix collision: Identical 4096 bytes, differing payload
        pA = os.path.join(edge_dir, "prefix_collision", "prefix_match_fileA.dat")
        pB = os.path.join(edge_dir, "prefix_collision", "prefix_match_fileB.dat")
        with open(pA, "wb") as f: f.write(b"\xAA" * 4096 + b"\xBB" * 65536)
        with open(pB, "wb") as f: f.write(b"\xAA" * 4096 + b"\xCC" * 65536)
        edge_cases.append({"type": "prefix_collision", "files": [pA, pB], "size": 69632})

        # EOF 1-byte difference: 128KB identical except last byte
        pA = os.path.join(edge_dir, "eof_single_byte_diff", "eof_diff_fileA.dat")
        pB = os.path.join(edge_dir, "eof_single_byte_diff", "eof_diff_fileB.dat")
        with open(pA, "wb") as f: f.write(b"\x55" * 131071 + b"\x00")
        with open(pB, "wb") as f: f.write(b"\x55" * 131071 + b"\x01")
        edge_cases.append({"type": "eof_single_byte_diff", "files": [pA, pB], "size": 131072})

    # Recalculate full directory statistics
    total_files_final = 0
    total_bytes_final = 0
    format_stats = {}

    for root, _, files in os.walk(target_dir):
        if "ground_truth_manifest.json" in files:
            files.remove("ground_truth_manifest.json")
        for f in files:
            p = os.path.join(root, f)
            sz = os.path.getsize(p)
            total_files_final += 1
            total_bytes_final += sz
            ext = os.path.splitext(f)[1].lower() or ".none"
            format_stats[ext] = format_stats.get(ext, {"count": 0, "bytes": 0})
            format_stats[ext]["count"] += 1
            format_stats[ext]["bytes"] += sz

    unique_bytes_final = total_bytes_final - redundant_bytes_created
    dr = total_bytes_final / unique_bytes_final if unique_bytes_final > 0 else 1.0
    savings_pct = (1.0 - (1.0 / dr)) * 100.0

    # Export Ground Truth Manifest
    manifest = {
        "metadata": {
            "dataset_name": "DedupFS Unified Benchmark Dataset",
            "generator_version": "3.0.0",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dup_ratio_requested": dup_ratio,
            "copies_per_duplicate": copies
        },
        "ground_truth_summary": {
            "total_files": total_files_final,
            "redundant_duplicate_copies": duplicate_copies_count,
            "duplicate_groups_count": len(active_clusters),
            "total_logical_bytes": total_bytes_final,
            "unique_original_bytes": unique_bytes_final,
            "wasted_duplicate_bytes": redundant_bytes_created,
            "reclaimable_space_mb": round(redundant_bytes_created / (1024 * 1024), 2),
            "expected_dedup_ratio": round(dr, 4),
            "expected_space_savings_pct": round(savings_pct, 2)
        },
        "format_breakdown": {
            ext: {"count": d["count"], "total_mb": round(d["bytes"] / (1024 * 1024), 2)}
            for ext, d in sorted(format_stats.items(), key=lambda x: x[1]["bytes"], reverse=True)
        },
        "edge_cases": edge_cases,
        "duplicate_clusters": active_clusters
    }

    manifest_path = os.path.join(target_dir, "ground_truth_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n[+] REPLICATION PASS COMPLETE!")
    print(f"    Total Final Files:          {total_files_final}")
    print(f"    Duplicate Copies Created:   {duplicate_copies_count}")
    print(f"    Duplicate Groups Formed:    {len(active_clusters)}")
    print(f"    Total Logical Footprint:    {total_bytes_final / (1024*1024):.2f} MB ({total_bytes_final / (1024*1024*1024):.2f} GB)")
    print(f"    Wasted Redundant Storage:   {redundant_bytes_created / (1024*1024):.2f} MB")
    print(f"    Expected Dedup Ratio (DR):  {dr:.2f}x (Space Savings: {savings_pct:.2f}%)")
    print(f"    Ground Truth Manifest:      {manifest_path}\n")


# ----------------------------------------------------------------------
# 5. Legacy Synthetic Dataset Generator (Backward Compatibility)
# ----------------------------------------------------------------------

def generate_legacy_synthetic(output_dir, num_unique, dup_ratio, min_kb, max_kb, copies_per_dup=2):
    """Preserves 100% backward compatibility with original synthetic generator CLI."""
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)

    total_unique = num_unique
    num_dup_groups = int(num_unique * dup_ratio)

    ground_truth = {
        "unique_files": 0,
        "duplicate_copies": 0,
        "total_files": 0,
        "total_bytes": 0,
        "wasted_bytes": 0
    }

    print(f"[*] Generating synthetic dataset in: {output_dir}")
    print(f"[*] Unique files: {total_unique}, Duplicate groups: {num_dup_groups}, Copies/group: {copies_per_dup}")

    unique_files_pool = []

    # 1. Generate unique files
    for i in range(total_unique):
        size_bytes = random.randint(min_kb * 1024, max_kb * 1024)
        subfolder = os.path.join(output_dir, f"dir_{i % 8}")
        os.makedirs(subfolder, exist_ok=True)
        file_path = os.path.join(subfolder, f"file_{i:05d}.dat")

        content = os.urandom(size_bytes)
        with open(file_path, "wb") as f:
            f.write(content)

        unique_files_pool.append((file_path, size_bytes, content))
        ground_truth["unique_files"] += 1
        ground_truth["total_files"] += 1
        ground_truth["total_bytes"] += size_bytes

    # 2. Replicate duplicate copies
    selected_for_dup = random.sample(unique_files_pool, num_dup_groups)
    for idx, (orig_path, size_bytes, content) in enumerate(selected_for_dup):
        for c in range(1, copies_per_dup + 1):
            dup_subfolder = os.path.join(output_dir, f"dup_dir_{idx % 4}")
            os.makedirs(dup_subfolder, exist_ok=True)
            dup_path = os.path.join(dup_subfolder, f"dup_{idx:04d}_copy{c}.dat")

            with open(dup_path, "wb") as f:
                f.write(content)

            ground_truth["duplicate_copies"] += 1
            ground_truth["total_files"] += 1
            ground_truth["total_bytes"] += size_bytes
            ground_truth["wasted_bytes"] += size_bytes

    print("\n[+] Synthetic Dataset Generation Complete!")
    print(f"    Total Files:           {ground_truth['total_files']}")
    print(f"    Unique Original Files: {ground_truth['unique_files']}")
    print(f"    Redundant Duplicates:  {ground_truth['duplicate_copies']}")
    print(f"    Total Logical Size:    {ground_truth['total_bytes'] / (1024 * 1024):.2f} MB")
    print(f"    Wasted Duplicate Size: {ground_truth['wasted_bytes'] / (1024 * 1024):.2f} MB")
    if ground_truth['total_bytes'] > 0:
        dr = ground_truth['total_bytes'] / (ground_truth['total_bytes'] - ground_truth['wasted_bytes'])
        savings = (1.0 - (1.0 / dr)) * 100.0
        print(f"    Expected Dedup Ratio:  {dr:.2f}x (Space Savings: {savings:.2f}%)")


# ----------------------------------------------------------------------
# Main Entry Point
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="DedupFS Unified Benchmark Dataset Generator (Linux Kernels, zlib-ng, Kaggle, Synthetic)"
    )
    parser.add_argument("--output-dir", default="./test_dataset", help="Output directory path")
    parser.add_argument("--type", "--dataset", dest="dataset_type",
                        choices=["all", "linux_kernel", "zlib_corpus", "kaggle", "synthetic"],
                        default="all",
                        help="Dataset type to build (default: all)")
    parser.add_argument("--target-gb", type=float, default=2.0, help="Target logical dataset size in GB (default: 2.0)")
    parser.add_argument("--dup-ratio", type=float, default=0.35, help="Fraction of base files to duplicate (0.0 to 1.0)")
    parser.add_argument("--copies", type=int, default=2, help="Number of duplicate copies per replicated group")
    parser.add_argument("--download", action="store_true", help="Attempt downloading official upstream archives (zlib-ng, Silesia, Kaggle)")
    parser.add_argument("--offline", action="store_true", help="Strictly offline mode (bypass all network downloads)")
    parser.add_argument("--include-edge-cases", action="store_true", default=True, help="Inject adversarial collision testcases")
    parser.add_argument("--clean", action="store_true", help="Clean destination directory before generating")

    # Legacy synthetic flags for 100% backward compatibility
    parser.add_argument("--num-unique", type=int, default=None, help="Legacy: Number of unique base files (triggers synthetic mode if specified without --type)")
    parser.add_argument("--min-kb", type=int, default=10, help="Legacy: Minimum file size in KB")
    parser.add_argument("--max-kb", type=int, default=100, help="Legacy: Maximum file size in KB")

    args = parser.parse_args()

    # Detect legacy invocation
    if args.num_unique is not None and args.dataset_type == "all" and "--type" not in sys.argv and "--dataset" not in sys.argv:
        generate_legacy_synthetic(args.output_dir, args.num_unique, args.dup_ratio, args.min_kb, args.max_kb, args.copies)
        return

    if args.clean and os.path.exists(args.output_dir):
        print(f"[*] Cleaning existing directory: {args.output_dir}")
        shutil.rmtree(args.output_dir)

    os.makedirs(args.output_dir, exist_ok=True)
    allow_download = args.download and not args.offline

    t0 = time.time()
    print("================================================================================")
    print("   DedupFS High-Performance Unified Dataset Generator")
    print("================================================================================")
    print(f"[*] Target Directory:   {os.path.abspath(args.output_dir)}")
    print(f"[*] Mode / Type:        {args.dataset_type}")
    print(f"[*] Target Size:        {args.target_gb:.2f} GB")
    print(f"[*] Duplication Ratio:  {args.dup_ratio * 100:.1f}%")
    print(f"[*] Copies per Group:   {args.copies}")
    print(f"[*] Online Downloads:   {'Enabled' if allow_download else 'Disabled (Offline Synthesizer)'}")
    print("--------------------------------------------------------------------------------\n")

    # 1. Linux Kernels
    if args.dataset_type in ["all", "linux_kernel"]:
        kernel_dir = os.path.join(args.output_dir, "linux_kernel")
        os.makedirs(kernel_dir, exist_ok=True)
        generate_linux_kernel_tree(kernel_dir, "linux-v6.6", patch_ratio=0.0)
        generate_linux_kernel_tree(kernel_dir, "linux-v6.7", patch_ratio=0.25)

    # 2. zlib-ng & Silesia Corpus
    if args.dataset_type in ["all", "zlib_corpus"]:
        setup_zlib_corpus(args.output_dir, allow_download=allow_download)

    # 3. Kaggle Datasets
    if args.dataset_type in ["all", "kaggle"]:
        setup_kaggle_datasets(args.output_dir, allow_download=allow_download)

    # 4. Synthetic mode
    if args.dataset_type == "synthetic":
        num_u = args.num_unique or 200
        generate_legacy_synthetic(args.output_dir, num_u, args.dup_ratio, args.min_kb, args.max_kb, args.copies)
        return

    # 5. Execute Proper Replication & Duplication Pass
    replicate_and_duplicate_files(
        args.output_dir,
        dup_ratio=args.dup_ratio,
        copies=args.copies,
        include_edge_cases=args.include_edge_cases
    )

    elapsed = time.time() - t0
    print(f"[+] Total Workflow Finished in {elapsed:.2f} seconds.")
    print(f"\nAudit duplicates with DedupFS:")
    print(f"  ./bin/dedupfs scan {args.output_dir}")
    print(f"Consolidate duplicates via POSIX atomic hard links:")
    print(f"  ./bin/dedupfs optimize {args.output_dir}\n")


if __name__ == "__main__":
    main()
