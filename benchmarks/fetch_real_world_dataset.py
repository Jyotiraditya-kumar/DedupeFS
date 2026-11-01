#!/usr/bin/env python3
"""
DedupFS Real-World Dataset Fetcher & Benchmark Preparer

Fetches and prepares representative real-world workloads:
1. Real-world multi-version software releases (e.g. Redis / SQLite / curl consecutive releases)
   -> Real-world code duplication between release snapshots (40%-80% duplicate files).
2. Document/text corpora (e.g. Enron Email sample / RFC documents).
3. Linux kernel headers / source subtree.
"""

import os
import sys
import shutil
import urllib.request
import tarfile
import zipfile
import subprocess
import argparse

REAL_DATASETS = {
    "software_releases": {
        "description": "Multi-release code trees with organic inter-version redundancy (e.g., Redis v7.0.0 vs v7.0.5 vs v7.2.0)",
        "sources": [
            ("redis-7.0.0", "https://github.com/redis/redis/archive/refs/tags/7.0.0.tar.gz"),
            ("redis-7.0.5", "https://github.com/redis/redis/archive/refs/tags/7.0.5.tar.gz"),
        ]
    },
    "curl_releases": {
        "description": "Curl consecutive releases (lightweight C codebase with real-world file evolution)",
        "sources": [
            ("curl-8.4.0", "https://github.com/curl/curl/archive/refs/tags/curl-8_4_0.tar.gz"),
            ("curl-8.5.0", "https://github.com/curl/curl/archive/refs/tags/curl-8_5_0.tar.gz"),
        ]
    },
    "rfc_documents": {
        "description": "IETF RFC technical documents collection (high text redundancy & repeated headers)",
        "sources": [
            ("rfc_samples", "https://www.ietf.org/rfc/tar/rfc-1000-1099.tar.gz")
        ]
    }
}

def download_file(url, target_path):
    print(f"[*] Downloading {url} -> {target_path}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print(f"[+] Download complete: {os.path.getsize(target_path) / (1024*1024):.2f} MB")

def extract_archive(archive_path, extract_dir):
    print(f"[*] Extracting {archive_path} -> {extract_dir}")
    os.makedirs(extract_dir, exist_ok=True)
    if archive_path.endswith(".tar.gz") or archive_path.endswith(".tgz"):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(extract_dir)
    elif archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    print("[+] Extraction finished.")

def setup_dataset(dataset_key, base_dir):
    if dataset_key not in REAL_DATASETS:
        print(f"[!] Unknown dataset: {dataset_key}. Choose from: {list(REAL_DATASETS.keys())}")
        sys.exit(1)

    info = REAL_DATASETS[dataset_key]
    out_dir = os.path.join(base_dir, dataset_key)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n========================================================")
    print(f"  Preparing Real-World Dataset: {dataset_key}")
    print(f"  Description: {info['description']}")
    print(f"  Target Directory: {out_dir}")
    print(f"========================================================\n")

    for name, url in info["sources"]:
        tar_name = f"{name}.tar.gz"
        tar_path = os.path.join(base_dir, tar_name)
        target_subfolder = os.path.join(out_dir, name)

        if os.path.exists(target_subfolder) and len(os.listdir(target_subfolder)) > 0:
            print(f"[i] Already extracted: {target_subfolder}")
            continue

        if not os.path.exists(tar_path):
            download_file(url, tar_path)

        extract_archive(tar_path, out_dir)

        # Cleanup tarball after extraction to save disk space
        if os.path.exists(tar_path):
            os.remove(tar_path)

    # Calculate statistics
    total_files = 0
    total_size = 0
    for root, _, files in os.walk(out_dir):
        for f in files:
            p = os.path.join(root, f)
            if not os.path.islink(p):
                total_files += 1
                total_size += os.path.getsize(p)

    print(f"\n[+] Real-World Dataset Ready in: {out_dir}")
    print(f"    Total Extracted Files: {total_files}")
    print(f"    Total Logical Footprint: {total_size / (1024*1024):.2f} MB")
    print(f"\nYou can now benchmark with:")
    print(f"    ./bin/dedupfs scan {out_dir}")
    print(f"    ./bin/dedupfs optimize {out_dir}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and prepare real-world datasets for DedupFS")
    parser.add_argument("--dataset", choices=list(REAL_DATASETS.keys()), default="curl_releases",
                        help="Dataset key to download")
    parser.add_argument("--output-dir", default="./datasets", help="Base directory to store datasets")
    args = parser.parse_args()

    setup_dataset(args.dataset, args.output_dir)
