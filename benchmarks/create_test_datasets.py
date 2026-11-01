#!/usr/bin/env python3
"""
DedupFS Real-World Test Dataset Builder
Advanced Data Structures (M.Tech Semester 1)

Constructs comprehensive, multi-tiered test datasets from raw real-world data:
- Resumes PDF: 8,905 real PDF resume documents across 99 professional categories.
- Images COCO: 82,783 real Microsoft COCO high-resolution JPG photographs.
- Linux Kernels: Full linux-6.10 and linux-6.11 trees with intelligent subsystem
  slicing (include, fs, kernel, mm, net) capturing organic cross-version redundancy.
- Curl Releases: Consecutive releases (curl 8.4.0 vs 8.5.0) lightweight C codebase.
- Dual-Folder Architecture:
  * ground_truth/ : Pristine, untouched reference copy with independent physical inodes.
  * work/         : Working copy for DedupFS scan & optimize operations.
  * ground_truth_manifest.json : Exact hash catalog & duplicate equivalence classes.
- Fast Reset & Verification:
  * --reset <tier>  : Instantly restores work/ from ground_truth/ in seconds.
  * --verify <tier> : Byte-for-byte validation & physical inode consolidation analysis.
"""

import os
import sys
import time
import json
import random
import shutil
import hashlib
import filecmp
import argparse
import subprocess

# ----------------------------------------------------------------------
# Helper Utilities
# ----------------------------------------------------------------------

def compute_sha256(file_path):
    """Calculates cryptographic SHA-256 digest of a regular file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def copy_regular_file(src, dst):
    """Safely copies a regular file without copying broken symlinks."""
    if os.path.islink(src):
        return 0
    if not os.path.isfile(src):
        return 0
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    return os.path.getsize(dst)

# ----------------------------------------------------------------------
# Subsystem Definitions for Linux Kernels
# ----------------------------------------------------------------------

KERNEL_SUBSYSTEM_PROFILES = {
    "small": [
        "kernel",                  # Core primitives (sched, fork, panic, printk, exit)
        "fs/ext4",                 # Ext4 filesystem driver
        "mm",                      # Memory management subsystem
        "include/linux"            # Core header definitions
    ],
    "medium": [
        "include",                 # Complete kernel headers (linux, uapi, asm-generic, net, etc.)
        "fs",                      # All filesystems (ext4, btrfs, xfs, fat, nfs, vfs)
        "kernel",                  # Sched, locking, time, cgroups, bpf, irq
        "mm",                      # Page alloc, slab, swap, vmscan, mmap
        "net"                      # Core networking, ipv4, ipv6, wireless
    ],
    "large": [
        "include",                 # Complete headers
        "fs",                      # Complete filesystems
        "kernel",                  # Complete core kernel
        "mm",                      # Complete memory management
        "net",                     # Complete networking
        "arch/x86",                # x86 architecture code
        "crypto",                  # Cryptographic algorithms
        "lib",                     # Kernel utility libraries
        "drivers/net",             # Network hardware drivers
        "drivers/block"            # Block storage drivers
    ]
}

# ----------------------------------------------------------------------
# Tier Budget Configurations
# ----------------------------------------------------------------------

TIER_BUDGETS = {
    "small": {
        "name": "test_small_250MB",
        "description": "Small Smoke Test Suite (~250 MB)",
        "target_bytes": 250 * 1024 * 1024,
        "shares": {
            "resumes": 0.30,   # ~75 MB
            "images": 0.35,    # ~88 MB
            "kernel": 0.25,    # ~62 MB (split between 6.10 & 6.11)
            "curl": 0.10       # ~25 MB
        },
        "kernel_profile": "small",
        "kernel_file_limit_per_ver": 800
    },
    "medium": {
        "name": "test_medium_1GB",
        "description": "Medium Benchmark Test Suite (~1.0 GB)",
        "target_bytes": 1024 * 1024 * 1024,
        "shares": {
            "resumes": 0.30,   # ~300 MB
            "images": 0.40,    # ~400 MB
            "kernel": 0.26,    # ~260 MB (split between 6.10 & 6.11)
            "curl": 0.04       # ~37 MB
        },
        "kernel_profile": "medium",
        "kernel_file_limit_per_ver": 3000
    },
    "large": {
        "name": "test_large_3.5GB",
        "description": "Large High-Capacity Benchmark Suite (~3.5 GB)",
        "target_bytes": int(3.5 * 1024 * 1024 * 1024),
        "shares": {
            "resumes": 0.32,   # ~1.1 GB
            "images": 0.40,    # ~1.4 GB
            "kernel": 0.28,    # ~1.0 GB (split between 6.10 & 6.11)
            "curl": 0.00       # Not included to maximize kernel/images
        },
        "kernel_profile": "large",
        "kernel_file_limit_per_ver": 15000
    }
}

# ----------------------------------------------------------------------
# Core Dataset Assembly Logic (Harvesting into ground_truth/)
# ----------------------------------------------------------------------

def harvest_resumes(raw_dir, target_dir, budget_bytes, seed=42):
    """Pulls diverse PDF resumes across 99 professional categories."""
    src_resumes = os.path.join(raw_dir, "Resumes PDF")
    if not os.path.exists(src_resumes):
        print(f"    [!] Warning: {src_resumes} not found, skipping resumes.")
        return 0, []

    print(f"    [*] Sourcing PDF resumes (Budget: {budget_bytes / (1024*1024):.1f} MB)...")
    all_pdfs = []
    for root, _, files in os.walk(src_resumes):
        for f in files:
            if f.lower().endswith(".pdf"):
                p = os.path.join(root, f)
                if not os.path.islink(p):
                    all_pdfs.append(p)

    random.seed(seed)
    random.shuffle(all_pdfs)

    copied_bytes = 0
    copied_files = []
    for src in all_pdfs:
        if copied_bytes >= budget_bytes:
            break
        rel = os.path.relpath(src, src_resumes)
        dst = os.path.join(target_dir, "documents/resumes", rel)
        sz = copy_regular_file(src, dst)
        if sz > 0:
            copied_bytes += sz
            copied_files.append(dst)

    print(f"    [+] Resumes gathered: {len(copied_files)} PDFs ({copied_bytes / (1024*1024):.2f} MB)")
    return copied_bytes, copied_files


def harvest_images(raw_dir, target_dir, budget_bytes, seed=42):
    """Pulls real COCO JPG photographs across multiple media folders."""
    src_images = os.path.join(raw_dir, "Images")
    if not os.path.exists(src_images):
        print(f"    [!] Warning: {src_images} not found, skipping images.")
        return 0, []

    print(f"    [*] Sourcing COCO JPG photographs (Budget: {budget_bytes / (1024*1024):.1f} MB)...")
    all_imgs = []
    for root, _, files in os.walk(src_images):
        for f in files:
            if f.lower().endswith(".jpg"):
                p = os.path.join(root, f)
                if not os.path.islink(p):
                    all_imgs.append(p)

    random.seed(seed)
    random.shuffle(all_imgs)

    copied_bytes = 0
    copied_files = []
    media_subfolders = [
        "media/gallery_primary",
        "media/catalog_assets",
        "media/scenic_photos",
        "media/visual_archive"
    ]

    for idx, src in enumerate(all_imgs):
        if copied_bytes >= budget_bytes:
            break
        subfolder = media_subfolders[idx % len(media_subfolders)]
        fname = os.path.basename(src)
        dst = os.path.join(target_dir, subfolder, fname)
        sz = copy_regular_file(src, dst)
        if sz > 0:
            copied_bytes += sz
            copied_files.append(dst)

    print(f"    [+] Images gathered: {len(copied_files)} JPGs ({copied_bytes / (1024*1024):.2f} MB)")
    return copied_bytes, copied_files


def harvest_linux_kernel(raw_dir, target_dir, budget_bytes, profile_name, file_limit, seed=42):
    """
    Intelligently sources paired subsystems from linux-6.10 and linux-6.11,
    providing organic cross-version duplication (~75-85% identical C/header files).
    """
    k610_dir = os.path.join(raw_dir, "linux-6.10")
    k611_dir = os.path.join(raw_dir, "linux-6.11")

    if not os.path.exists(k610_dir) or not os.path.exists(k611_dir):
        print(f"    [!] Warning: Linux kernel directories not found, skipping kernel.")
        return 0, []

    subsystems = KERNEL_SUBSYSTEM_PROFILES.get(profile_name, KERNEL_SUBSYSTEM_PROFILES["small"])
    print(f"    [*] Sourcing Linux Kernels 6.10 & 6.11 (Profile: {profile_name}, Budget: {budget_bytes / (1024*1024):.1f} MB)...")

    budget_per_kernel = budget_bytes // 2
    copied_bytes = 0
    copied_files = []

    for ver_name, src_root in [("linux-6.10", k610_dir), ("linux-6.11", k611_dir)]:
        k_bytes = 0
        k_count = 0
        dst_base = os.path.join(target_dir, "source_code", ver_name)

        candidate_files = []
        for sub in subsystems:
            sub_path = os.path.join(src_root, sub)
            if not os.path.exists(sub_path):
                continue
            for root, _, files in os.walk(sub_path):
                for f in files:
                    p = os.path.join(root, f)
                    if not os.path.islink(p) and os.path.isfile(p):
                        candidate_files.append(p)

        random.seed(seed)
        random.shuffle(candidate_files)

        for src in candidate_files:
            if k_bytes >= budget_per_kernel or k_count >= file_limit:
                break
            rel = os.path.relpath(src, src_root)
            dst = os.path.join(dst_base, rel)
            sz = copy_regular_file(src, dst)
            if sz > 0:
                k_bytes += sz
                k_count += 1
                copied_bytes += sz
                copied_files.append(dst)

        print(f"        [>] Sourced {ver_name}: {k_count} files ({k_bytes / (1024*1024):.2f} MB)")

    print(f"    [+] Linux Kernels gathered: {len(copied_files)} files ({copied_bytes / (1024*1024):.2f} MB)")
    return copied_bytes, copied_files


def harvest_curl(raw_dir, target_dir, budget_bytes):
    """Pulls curl consecutive releases (curl 8.4.0 vs 8.5.0)."""
    curl_dir = os.path.join(raw_dir, "curl_releases")
    if not os.path.exists(curl_dir) or budget_bytes <= 0:
        return 0, []

    print(f"    [*] Sourcing curl releases (curl 8.4.0 vs 8.5.0)...")
    copied_bytes = 0
    copied_files = []
    dst_base = os.path.join(target_dir, "source_code/curl_releases")

    for root, _, files in os.walk(curl_dir):
        for f in files:
            if copied_bytes >= budget_bytes:
                break
            src = os.path.join(root, f)
            if not os.path.islink(src) and os.path.isfile(src):
                rel = os.path.relpath(src, curl_dir)
                dst = os.path.join(dst_base, rel)
                sz = copy_regular_file(src, dst)
                if sz > 0:
                    copied_bytes += sz
                    copied_files.append(dst)

    print(f"    [+] Curl releases gathered: {len(copied_files)} files ({copied_bytes / (1024*1024):.2f} MB)")
    return copied_bytes, copied_files


# ----------------------------------------------------------------------
# Comprehensive Replication & Multi-Folder Duplication Engine
# ----------------------------------------------------------------------

def replicate_and_nest_files(target_dir, base_files, dup_ratio=0.35, max_copies=3, seed=42):
    """
    Creates realistic duplicate files across diverse paths, different names,
    nested directories (4-6 levels deep), and multi-copy clusters.
    """
    print(f"\n    [*] Executing Comprehensive Duplication & Replication Pass...")
    print(f"        Target Duplication Ratio: {dup_ratio * 100:.1f}%")
    print(f"        Max Duplicate Copies/File: {max_copies}")

    random.seed(seed)
    random.shuffle(base_files)

    total_base_bytes = sum(os.path.getsize(p) for p in base_files if os.path.exists(p))
    target_redundant_bytes = int(total_base_bytes * dup_ratio)

    nested_destinations = [
        "downloads_inbox",
        "downloads_inbox/browser_downloads_oct2026",
        "downloads_inbox/email_attachments",
        "backup_snapshots/daily_20261031/documents",
        "backup_snapshots/daily_20261031/media",
        "backup_snapshots/weekly_vault/codebase",
        "workspace_clones/feature_branch_experimental",
        "workspace_clones/staging_env/core_assets",
        "shared_corporate_nas/hr_recruitment_pool",
        "shared_corporate_nas/creative_media_team",
        "deeply_nested_archives/dept/hr/recruitment/2026/q3/screened",
        "deeply_nested_archives/vault/media/hi_res/exports/final",
        "deeply_nested_archives/projects/kernel_audit/archived_subsystems/ext4"
    ]

    for d in nested_destinations:
        os.makedirs(os.path.join(target_dir, d), exist_ok=True)

    duplicate_clusters = {} # sha256 -> list of relative paths
    redundant_bytes_created = 0
    duplicate_copies_count = 0
    file_idx = 0

    pdf_name_templates = [
        "{base} (1).pdf", "{base} (Copy).pdf", "{base}_reviewed.pdf",
        "candidate_cv_{base}.pdf", "copy_of_{base}.pdf", "{base}_final_v2.pdf",
        "Applicant_Profile_{idx}.pdf"
    ]

    img_name_templates = [
        "{base} (1).jpg", "{base} (Copy).jpg", "{base}_compressed.jpg",
        "wallpaper_hero_{idx}.jpg", "marketing_asset_{base}.jpg", "photo_preview_{idx}.jpg"
    ]

    code_name_templates = [
        "{base}_backup.c", "{base}_old.c", "revised_{base}.c", "{base}_snapshot.c"
    ]

    while redundant_bytes_created < target_redundant_bytes and file_idx < len(base_files):
        src_path = base_files[file_idx]
        file_idx += 1
        if not os.path.exists(src_path) or os.path.islink(src_path):
            continue

        src_size = os.path.getsize(src_path)
        src_sha = compute_sha256(src_path)

        if src_sha not in duplicate_clusters:
            duplicate_clusters[src_sha] = [os.path.relpath(src_path, target_dir)]

        fname = os.path.basename(src_path)
        name_no_ext, ext = os.path.splitext(fname)
        ext_lower = ext.lower()

        num_copies = random.choices([1, 2, max_copies], weights=[65, 25, 10])[0]

        for c in range(1, num_copies + 1):
            if redundant_bytes_created >= target_redundant_bytes:
                break

            target_sub = random.choice(nested_destinations)

            if ext_lower == ".pdf":
                name_fmt = random.choice(pdf_name_templates)
            elif ext_lower == ".jpg":
                name_fmt = random.choice(img_name_templates)
            elif ext_lower in [".c", ".h"]:
                name_fmt = random.choice(code_name_templates)
            else:
                name_fmt = "{base} (Copy {idx})" + ext

            new_name = name_fmt.format(base=name_no_ext, idx=duplicate_copies_count)
            dst_path = os.path.join(target_dir, target_sub, new_name)

            if os.path.exists(dst_path):
                dst_path = os.path.join(target_dir, target_sub, f"dup_{duplicate_copies_count}_{fname}")

            shutil.copyfile(src_path, dst_path)

            duplicate_clusters[src_sha].append(os.path.relpath(dst_path, target_dir))
            redundant_bytes_created += src_size
            duplicate_copies_count += 1

    active_clusters = {h: paths for h, paths in duplicate_clusters.items() if len(paths) > 1}
    print(f"    [+] Created {duplicate_copies_count} duplicate copies ({redundant_bytes_created / (1024*1024):.2f} MB)")
    print(f"    [+] Distinct duplicate equivalence classes: {len(active_clusters)}")
    return redundant_bytes_created, duplicate_copies_count, active_clusters


# ----------------------------------------------------------------------
# Adversarial Collision Edge Cases
# ----------------------------------------------------------------------

def inject_adversarial_edge_cases(target_dir):
    """
    Creates deterministic edge-case test files:
    - Tier 1: Identical sizes, completely different content
    - Tier 2: Identical 4096-byte prefixes, differing body
    - Tier 5: 128KB files differing by only 1 byte at EOF
    """
    edge_dir = os.path.join(target_dir, "dedup_edge_cases")
    os.makedirs(os.path.join(edge_dir, "size_collision"), exist_ok=True)
    os.makedirs(os.path.join(edge_dir, "prefix_collision"), exist_ok=True)
    os.makedirs(os.path.join(edge_dir, "eof_single_byte_diff"), exist_ok=True)

    edge_cases = []

    # 1. Size Collision (1MB exact)
    pA = os.path.join(edge_dir, "size_collision", "size_match_alpha.dat")
    pB = os.path.join(edge_dir, "size_collision", "size_match_beta.dat")
    with open(pA, "wb") as f: f.write(bytes([0x33] * 1048576))
    with open(pB, "wb") as f: f.write(bytes([0x77] * 1048576))
    edge_cases.append({"type": "size_collision", "files": [pA, pB], "size": 1048576})

    # 2. Prefix Collision (4096-byte shared prefix)
    pA = os.path.join(edge_dir, "prefix_collision", "prefix_match_alpha.dat")
    pB = os.path.join(edge_dir, "prefix_collision", "prefix_match_beta.dat")
    pref = b"\xDE\xAD\xBE\xEF" * 1024
    with open(pA, "wb") as f: f.write(pref + b"\x11" * 65536)
    with open(pB, "wb") as f: f.write(pref + b"\x22" * 65536)
    edge_cases.append({"type": "prefix_collision", "files": [pA, pB], "size": 69632})

    # 3. EOF 1-byte Difference (128 KB exact)
    pA = os.path.join(edge_dir, "eof_single_byte_diff", "eof_diff_original.dat")
    pB = os.path.join(edge_dir, "eof_single_byte_diff", "eof_diff_mutated.dat")
    body = b"\x5A" * 131071
    with open(pA, "wb") as f: f.write(body + b"\x00")
    with open(pB, "wb") as f: f.write(body + b"\xFF")
    edge_cases.append({"type": "eof_single_byte_diff", "files": [pA, pB], "size": 131072})

    return edge_cases


# ----------------------------------------------------------------------
# Ground Truth Manifest Generator
# ----------------------------------------------------------------------

def write_ground_truth_manifest(target_dir, manifest_output_path, tier_info, active_clusters, redundant_bytes, dup_count, edge_cases):
    """Computes exact empirical metrics and exports ground_truth_manifest.json."""
    total_files = 0
    total_bytes = 0
    format_stats = {}
    category_stats = {}

    for root, _, files in os.walk(target_dir):
        for f in files:
            p = os.path.join(root, f)
            if not os.path.islink(p) and os.path.isfile(p):
                sz = os.path.getsize(p)
                total_files += 1
                total_bytes += sz
                ext = os.path.splitext(f)[1].lower() or ".none"
                format_stats[ext] = format_stats.get(ext, {"count": 0, "bytes": 0})
                format_stats[ext]["count"] += 1
                format_stats[ext]["bytes"] += sz

                rel = os.path.relpath(p, target_dir)
                cat = rel.split(os.sep)[0]
                category_stats[cat] = category_stats.get(cat, {"count": 0, "bytes": 0})
                category_stats[cat]["count"] += 1
                category_stats[cat]["bytes"] += sz

    unique_bytes = total_bytes - redundant_bytes
    dr = total_bytes / unique_bytes if unique_bytes > 0 else 1.0
    savings_pct = (1.0 - (1.0 / dr)) * 100.0

    manifest = {
        "metadata": {
            "dataset_name": f"DedupFS Real-World Test Dataset ({tier_info.get('name', 'Custom')})",
            "tier": tier_info.get("name", "custom"),
            "description": tier_info.get("description", "Custom real-world test suite"),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ground_truth_directory": os.path.abspath(target_dir)
        },
        "ground_truth_summary": {
            "total_files": total_files,
            "redundant_duplicate_copies": dup_count,
            "duplicate_groups_count": len(active_clusters),
            "total_logical_bytes": total_bytes,
            "unique_original_bytes": unique_bytes,
            "wasted_duplicate_bytes": redundant_bytes,
            "reclaimable_space_mb": round(redundant_bytes / (1024 * 1024), 2),
            "expected_dedup_ratio": round(dr, 4),
            "expected_space_savings_pct": round(savings_pct, 2)
        },
        "format_breakdown": {
            ext: {"count": d["count"], "total_mb": round(d["bytes"] / (1024 * 1024), 2)}
            for ext, d in sorted(format_stats.items(), key=lambda x: x[1]["bytes"], reverse=True)
        },
        "category_breakdown": {
            cat: {"count": d["count"], "total_mb": round(d["bytes"] / (1024 * 1024), 2)}
            for cat, d in sorted(category_stats.items(), key=lambda x: x[1]["bytes"], reverse=True)
        },
        "edge_cases": edge_cases,
        "duplicate_clusters": active_clusters
    }

    with open(manifest_output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return total_files, total_bytes, dr, savings_pct


# ----------------------------------------------------------------------
# Dual-Folder Tier Dataset Builder (ground_truth/ + work/)
# ----------------------------------------------------------------------

def build_test_tier(raw_dir, output_dir, tier_cfg, dup_ratio=0.35, max_copies=3, seed=42, clean=True):
    """
    Assembles a dual-folder test suite:
    - ground_truth/ : Pristine, untouched reference copy.
    - work/         : Working clone for DedupFS scan & optimize.
    """
    t0 = time.time()
    tier_name = tier_cfg["name"]
    tier_desc = tier_cfg["description"]
    target_bytes = tier_cfg["target_bytes"]
    shares = tier_cfg["shares"]
    profile = tier_cfg["kernel_profile"]
    file_limit = tier_cfg["kernel_file_limit_per_ver"]

    gt_dir = os.path.join(output_dir, "ground_truth")
    work_dir = os.path.join(output_dir, "work")
    manifest_path = os.path.join(output_dir, "ground_truth_manifest.json")

    print("\n" + "=" * 80)
    print(f"   BUILDING TEST SUITE: {tier_desc}")
    print("=" * 80)
    print(f"[*] Base Dataset Directory: {os.path.abspath(output_dir)}")
    print(f"[*] Ground Truth Directory: {os.path.abspath(gt_dir)} (Untouched Reference)")
    print(f"[*] Working Directory:      {os.path.abspath(work_dir)} (DedupFS Target)")
    print(f"[*] Target Budget:          {target_bytes / (1024*1024):.1f} MB ({target_bytes / (1024*1024*1024):.2f} GB)")
    print(f"[*] Duplication Target:     {dup_ratio * 100:.1f}%")
    print(f"[*] Random Seed:            {seed}")

    if clean and os.path.exists(output_dir):
        print(f"[*] Cleaning previous output directory...")
        shutil.rmtree(output_dir)

    os.makedirs(gt_dir, exist_ok=True)

    base_files = []

    # 1. Harvest Resumes PDF into ground_truth/
    b_resumes = int(target_bytes * shares.get("resumes", 0.30))
    _, files = harvest_resumes(raw_dir, gt_dir, b_resumes, seed=seed)
    base_files.extend(files)

    # 2. Harvest COCO Images into ground_truth/
    b_images = int(target_bytes * shares.get("images", 0.35))
    _, files = harvest_images(raw_dir, gt_dir, b_images, seed=seed)
    base_files.extend(files)

    # 3. Harvest Linux Kernels (6.10 & 6.11) into ground_truth/
    b_kernel = int(target_bytes * shares.get("kernel", 0.25))
    _, files = harvest_linux_kernel(raw_dir, gt_dir, b_kernel, profile, file_limit, seed=seed)
    base_files.extend(files)

    # 4. Harvest Curl Releases into ground_truth/
    b_curl = int(target_bytes * shares.get("curl", 0.0))
    if b_curl > 0:
        _, files = harvest_curl(raw_dir, gt_dir, b_curl)
        base_files.extend(files)

    # 5. Inject Adversarial Edge Cases into ground_truth/
    edge_cases = inject_adversarial_edge_cases(gt_dir)

    # 6. Replicate and Nest Duplicate Files in ground_truth/
    redundant_bytes, dup_count, active_clusters = replicate_and_nest_files(
        gt_dir, base_files, dup_ratio=dup_ratio, max_copies=max_copies, seed=seed
    )

    # 7. Write Ground Truth Manifest
    tot_files, tot_bytes, dr, savings = write_ground_truth_manifest(
        gt_dir, manifest_path, tier_cfg, active_clusters, redundant_bytes, dup_count, edge_cases
    )

    # 8. Clone ground_truth/ to work/ with independent physical disk inodes
    print(f"\n    [*] Cloning ground_truth/ -> work/ (creating independent physical inodes)...")
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    subprocess.run(["cp", "-r", gt_dir, work_dir], check=True)
    print(f"    [+] Clone complete! 'work/' is ready for DedupFS operations.")

    elapsed = time.time() - t0
    print("\n" + "-" * 80)
    print(f"[+] {tier_name} BUILT SUCCESSFULLY in {elapsed:.2f} seconds ({tot_bytes / (1024*1024) / elapsed:.1f} MB/s)!")
    print(f"    Total Logical Files:       {tot_files}")
    print(f"    Total Logical Footprint:   {tot_bytes / (1024*1024):.2f} MB ({tot_bytes / (1024*1024*1024):.2f} GB)")
    print(f"    Redundant Duplicate Files: {dup_count}")
    print(f"    Duplicate Groups Formed:   {len(active_clusters)}")
    print(f"    Reclaimable Space:         {redundant_bytes / (1024*1024):.2f} MB")
    print(f"    Expected Dedup Ratio:      {dr:.2f}x (Space Savings: {savings:.2f}%)")
    print(f"    Ground Truth Manifest:     {manifest_path}")
    print("-" * 80)
    print(f"1. Audit duplicates (dry-run on work/):")
    print(f"   ./bin/dedupfs scan {work_dir}")
    print(f"2. Consolidate duplicates via atomic hard links:")
    print(f"   ./bin/dedupfs optimize {work_dir}")
    print(f"3. Verify byte equivalence against untouched ground truth:")
    print(f"   ./benchmarks/create_test_datasets.py --verify {tier_name.replace('test_', '').split('_')[0]}")
    print(f"4. Revert/reset work/ to pristine state in seconds:")
    print(f"   ./benchmarks/create_test_datasets.py --reset {tier_name.replace('test_', '').split('_')[0]}\n")


# ----------------------------------------------------------------------
# Reset & Verification Utilities
# ----------------------------------------------------------------------

def reset_dataset(dataset_dir):
    """Wipes work/ and re-clones from pristine ground_truth/."""
    gt_dir = os.path.join(dataset_dir, "ground_truth")
    work_dir = os.path.join(dataset_dir, "work")

    if not os.path.exists(gt_dir):
        print(f"[!] Error: Cannot reset. {gt_dir} does not exist.")
        return False

    print(f"[*] Resetting {work_dir} from untouched {gt_dir}...")
    t0 = time.time()
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    subprocess.run(["cp", "-r", gt_dir, work_dir], check=True)
    dt = time.time() - t0
    print(f"[+] Reset complete in {dt:.2f}s! 'work/' is now in pristine pre-deduplication state.")
    return True


def verify_dataset(dataset_dir):
    """
    Performs comprehensive verification between work/ and ground_truth/:
    1. Bit-for-bit file equivalence (zero corruption check).
    2. Inode consolidation count and hard-link statistics.
    3. Reclaimed physical disk storage.
    """
    gt_dir = os.path.join(dataset_dir, "ground_truth")
    work_dir = os.path.join(dataset_dir, "work")

    if not os.path.exists(gt_dir) or not os.path.exists(work_dir):
        print(f"[!] Error: Missing ground_truth or work directory in {dataset_dir}")
        return False

    print("\n" + "=" * 80)
    print(f"   DEDUPFS INTEGRITY & OPTIMIZATION VERIFIER")
    print("=" * 80)
    print(f"[*] Dataset:       {os.path.abspath(dataset_dir)}")
    print(f"[*] Ground Truth:  {os.path.abspath(gt_dir)} (Reference)")
    print(f"[*] Work Folder:   {os.path.abspath(work_dir)} (DedupFS Target)")
    print("-" * 80)

    # 1. Gather all files
    gt_files = []
    for r, _, fs in os.walk(gt_dir):
        for f in fs:
            gt_files.append(os.path.relpath(os.path.join(r, f), gt_dir))

    work_files = []
    for r, _, fs in os.walk(work_dir):
        for f in fs:
            work_files.append(os.path.relpath(os.path.join(r, f), work_dir))

    print(f"[*] Total Files in Ground Truth: {len(gt_files):,}")
    print(f"[*] Total Files in Work Folder:  {len(work_files):,}")

    if len(gt_files) != len(work_files):
        print(f"[FAIL] File count mismatch! Ground Truth: {len(gt_files)}, Work: {len(work_files)}")
        return False

    # 2. Check bit-for-bit content preservation
    print("[*] Performing bit-for-bit content comparison...")
    mismatches = 0
    t0 = time.time()
    for rel in gt_files:
        p_gt = os.path.join(gt_dir, rel)
        p_wk = os.path.join(work_dir, rel)
        if not os.path.exists(p_wk):
            mismatches += 1
            continue
        # Compare byte size first, then contents
        if os.path.getsize(p_gt) != os.path.getsize(p_wk):
            mismatches += 1
        elif not filecmp.cmp(p_gt, p_wk, shallow=False):
            mismatches += 1

    dt = time.time() - t0
    print(f"[OK] Content verification finished in {dt:.2f}s.")
    if mismatches > 0:
        print(f"[FAIL] {mismatches} files have corrupted or mismatched contents!")
        return False
    else:
        print(f"[PASS] 100% BYTE EQUIVALENCE VERIFIED (Zero data corruption, zero false links)!")

    # 3. Inode & Storage Consolidation Analysis
    gt_inodes = {os.stat(os.path.join(gt_dir, rel)).st_ino for rel in gt_files}
    work_inodes = set()
    work_hardlinks = 0
    max_links = 1

    for rel in work_files:
        st = os.stat(os.path.join(work_dir, rel))
        work_inodes.add(st.st_ino)
        if st.st_nlink > 1:
            work_hardlinks += 1
            if st.st_nlink > max_links:
                max_links = st.st_nlink

    consolidated_inodes = len(gt_inodes) - len(work_inodes)
    print("\n--- INODE CONSOLIDATION REPORT ---")
    print(f"Ground Truth Unique Inodes:   {len(gt_inodes):,}")
    print(f"Work Folder Unique Inodes:    {len(work_inodes):,}")
    print(f"Physical Inodes Consolidated: {consolidated_inodes:,}")
    print(f"Files Sharing Hard Links:     {work_hardlinks:,} (Max Link Count: {max_links})")

    if consolidated_inodes > 0:
        print(f"\n[OK] Storage Deduplication is ACTIVE and VERIFIED on 'work/'!")
    else:
        print(f"\n[i] 'work/' is currently in un-optimized (pristine) state. Run 'dedupfs optimize' to consolidate.")
    print("=" * 80 + "\n")
    return True


# ----------------------------------------------------------------------
# Main CLI Orchestration
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="DedupFS Real-World Test Dataset Builder & Multi-Folder Harness"
    )
    parser.add_argument("--raw-dir", default="./raw_datasets", help="Path to raw_datasets directory")
    parser.add_argument("--output-base", default="./datasets", help="Base directory where test suites are stored")
    parser.add_argument("--tiers", default="small,medium,large",
                        help="Comma-separated list of tiers to build: small, medium, large, or all (default: small,medium,large)")
    parser.add_argument("--tier", default=None, choices=["small", "medium", "large"],
                        help="Build a single specific tier (small, medium, or large)")
    parser.add_argument("--target-gb", type=float, default=None,
                        help="Build a custom size dataset in Gigabytes (e.g. 2.5)")
    parser.add_argument("--output-dir", default=None,
                        help="Custom output directory (used with --target-gb or single tier)")
    parser.add_argument("--dup-ratio", type=float, default=0.35, help="Target duplication fraction (0.0 to 1.0, default: 0.35)")
    parser.add_argument("--copies", type=int, default=3, help="Max duplicate copies per group (default: 3)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--no-clean", action="store_true", help="Do not clean directory before building")

    # Fast Reset & Verify Flags
    parser.add_argument("--reset", default=None, choices=["small", "medium", "large", "all"],
                        help="Quickly reset work/ from ground_truth/ for a specific tier")
    parser.add_argument("--verify", default=None, choices=["small", "medium", "large", "all"],
                        help="Verify bit-for-bit equivalence & inode consolidation between work/ and ground_truth/")

    args = parser.parse_args()

    clean = not args.no_clean

    # Handle Reset Command
    if args.reset:
        tiers_to_reset = ["small", "medium", "large"] if args.reset == "all" else [args.reset]
        for t in tiers_to_reset:
            tier_dir = os.path.join(args.output_base, TIER_BUDGETS[t]["name"])
            reset_dataset(tier_dir)
        return

    # Handle Verify Command
    if args.verify:
        tiers_to_verify = ["small", "medium", "large"] if args.verify == "all" else [args.verify]
        for t in tiers_to_verify:
            tier_dir = os.path.join(args.output_base, TIER_BUDGETS[t]["name"])
            verify_dataset(tier_dir)
        return

    if not os.path.exists(args.raw_dir):
        print(f"[!] Error: raw_datasets directory not found at: {os.path.abspath(args.raw_dir)}")
        sys.exit(1)

    # 1. Custom Target GB Mode
    if args.target_gb is not None:
        target_bytes = int(args.target_gb * 1024 * 1024 * 1024)
        out_dir = args.output_dir or os.path.join(args.output_base, f"test_custom_{args.target_gb:.1f}GB")
        prof = "large" if args.target_gb >= 2.0 else ("medium" if args.target_gb >= 0.7 else "small")
        flimit = 15000 if args.target_gb >= 2.0 else 4000
        custom_cfg = {
            "name": os.path.basename(out_dir),
            "description": f"Custom Test Suite ({args.target_gb:.2f} GB)",
            "target_bytes": target_bytes,
            "shares": {"resumes": 0.32, "images": 0.40, "kernel": 0.28},
            "kernel_profile": prof,
            "kernel_file_limit_per_ver": flimit
        }
        build_test_tier(args.raw_dir, out_dir, custom_cfg, dup_ratio=args.dup_ratio, max_copies=args.copies, seed=args.seed, clean=clean)
        return

    # 2. Single Tier Mode
    if args.tier:
        tier_cfg = TIER_BUDGETS[args.tier]
        out_dir = args.output_dir or os.path.join(args.output_base, tier_cfg["name"])
        build_test_tier(args.raw_dir, out_dir, tier_cfg, dup_ratio=args.dup_ratio, max_copies=args.copies, seed=args.seed, clean=clean)
        return

    # 3. Multi-Tier Batch Mode
    selected_tiers = [t.strip().lower() for t in args.tiers.split(",")]
    if "all" in selected_tiers:
        selected_tiers = ["small", "medium", "large"]

    for t in selected_tiers:
        if t in TIER_BUDGETS:
            tier_cfg = TIER_BUDGETS[t]
            out_dir = os.path.join(args.output_base, tier_cfg["name"])
            build_test_tier(args.raw_dir, out_dir, tier_cfg, dup_ratio=args.dup_ratio, max_copies=args.copies, seed=args.seed, clean=clean)
        else:
            print(f"[!] Warning: Unknown tier '{t}', skipping. Available: small, medium, large")


if __name__ == "__main__":
    main()
