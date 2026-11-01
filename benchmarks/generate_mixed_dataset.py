#!/usr/bin/env python3
"""
DedupFS Realistic Mixed Documents & Images Dataset Generator
Advanced Data Structures (M.Tech Semester 1)

Generates a large (~2-3 GB), realistic mixed dataset consisting of authentic:
- Documents: PDF reports, Markdown specs, CSV spreadsheets, JSON data lakes,
             HTML dashboards, and system log memos.
- Images: High-resolution uncompressed BMP photos/scans, PNG graphics,
          Netpbm PPM rasters, and SVG vector diagrams.
- Real-world directory hierarchy: documents/, media_images/, downloads_inbox/,
  backups_and_snapshots/, shared_team_assets/, and dedup_edge_cases/.
- Edge cases: Size collisions (Tier 1), 4KB Prefix collisions (Tier 2),
  and 1-byte EOF mismatches (Byte Verifier).
- Ground truth manifest (JSON) recording exact duplicate clusters and byte statistics.
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
import argparse

# ----------------------------------------------------------------------
# Procedural Content Generators for Realistic Documents & Images
# ----------------------------------------------------------------------

REPORT_TITLES = [
    "Storage Deduplication Performance in High-Throughput Cluster Environments",
    "Empirical Analysis of Inverted Index Collision Rates and Load Factors",
    "Probabilistic Set Membership and Bloom Filter Scaling Limits",
    "Transactional Inode Relinking and Space Reclamation in POSIX Filesystems",
    "Zero-Collision Byte Verification Protocols for Critical Storage Arrays",
    "Quarterly Global Operations and Infrastructure Auditing Report",
    "Distributed Cache Consistency and Replication Telemetry Analysis",
    "Cryptographic SHA-256 Stream Pipeline Acceleration on Modern Silicon",
    "Hierarchical Merkle Trees for Incremental Snapshot Synchronization",
    "Longitudinal Study of Redundant Block Accumulation in Cloud Buckets"
]

AUTHORS = [
    "Aryan Ravi Zodape & Jyotiraditya Kumar",
    "Dr. Systems Engineering Research Group",
    "Infrastructure Storage Architecture Working Group",
    "Advanced Data Structures & Algorithms Lab",
    "High-Performance Computing Research Consortium"
]

MD_SECTIONS = [
    ("Executive Summary", "This technical evaluation investigates high-capacity storage deduplication architectures. Modern file systems frequently store extensive redundant data streams originating from repeated attachments, parallel build trees, and uncoordinated backup jobs. By combining dynamic bitset Bloom filters with linear probing hash tables, secondary storage overhead is substantially reduced."),
    ("Algorithmic Methodology", "The indexing pipeline utilizes a multi-tier screening hierarchy. In Tier 1, file sizes are cataloged via stat(2) calls to reject unique lengths in O(1) time. In Tier 2, candidate pairs evaluate a 128-bit Murmur3 prefix digest over the initial 4096 bytes. In Tier 3, a full SHA-256 cryptographic digest confirms candidate equivalence."),
    ("Experimental Setup", "All tests were conducted on an Ubuntu Linux 64-bit environment with high-throughput NVMe storage. High-resolution POSIX monotonic clocks measured system latency across scanning, hashing, and link-swapping stages."),
    ("Memory Footprint & Telemetry", "Peak resident set size (RSS) was captured using /proc/self/statm inspections. The empirical false-positive rate of the Bloom filter adhered strictly to the theoretical bounds derived from the dynamic bitset formula m = -n*ln(p)/(ln 2)^2.")
]

def make_valid_pdf(path, title, author, extra_bytes=50000):
    """Generates a syntactically valid PDF-1.4 file with text and binary payload streams."""
    stream_text = (
        f"BT\n"
        f"/F1 16 Tf\n"
        f"50 740 Td\n({title[:60]}) Tj\n"
        f"/F1 11 Tf\n"
        f"0 -25 Td\n(Author: {author}) Tj\n"
        f"0 -20 Td\n(Publication Date: October 2026 | Technical Report Series) Tj\n"
        f"0 -25 Td\n(Abstract: High-performance storage deduplication benchmarks and metrics.) Tj\n"
        f"ET\n"
    ).encode("latin-1")

    # Repeatable structural pseudo-binary payload to simulate embedded image / chart stream
    stream_payload = bytearray(stream_text)
    stream_payload.extend(b"\nq\n% EMBEDDED_DIAGRAM_RASTER_DATA\n")
    pattern_block = b"DEDUPFS_RAW_METRIC_BUFFER_VECTOR_POINT_XYZ_DATA_STREAM_CHUNK\n"
    needed = max(0, extra_bytes - len(stream_payload) - 50)
    repeats = (needed // len(pattern_block)) + 1
    stream_payload.extend((pattern_block * repeats)[:needed])
    stream_payload.extend(b"\nQ\n")

    body = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []

    def add_obj(data):
        offsets.append(len(body))
        body.extend(f"{len(offsets)} 0 obj\n".encode("latin-1"))
        body.extend(data)
        body.extend(b"\nendobj\n")

    # Obj 1: Catalog
    add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    # Obj 2: Pages
    add_obj(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    # Obj 3: Page
    add_obj(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>")
    # Obj 4: Contents Stream
    add_obj(f"<< /Length {len(stream_payload)} >>\nstream\n".encode("latin-1") + stream_payload + b"\nendstream")
    # Obj 5: Font
    add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

    xref_pos = len(body)
    body.extend(f"xref\n0 {len(offsets)+1}\n0000000000 65535 f \n".encode("latin-1"))
    for off in offsets:
        body.extend(f"{off:010d} 00000 n \n".encode("latin-1"))
    body.extend(f"trailer\n<< /Size {len(offsets)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1"))

    with open(path, "wb") as f:
        f.write(body)

def make_valid_bmp(path, width, height, seed=1):
    """Generates a syntactically valid Windows 3.x 24-bit RGB uncompressed BMP image."""
    row_bytes = (width * 3 + 3) & ~3
    image_bytes = row_bytes * height
    file_bytes = 54 + image_bytes
    hdr = struct.pack("<2sIHHI", b"BM", file_bytes, 0, 0, 54)
    dib = struct.pack("<IIIHHIIIIII", 40, width, height, 1, 24, 0, image_bytes, 2835, 2835, 0, 0)

    # Generate a procedural patterned raster (gradients + stripes)
    row_data = bytearray(row_bytes)
    for x in range(width):
        r = (x * 7 + seed * 19) & 0xFF
        g = ((width - x) * 5 + seed * 11) & 0xFF
        b = ((x ^ seed) * 13) & 0xFF
        row_data[x * 3] = b
        row_data[x * 3 + 1] = g
        row_data[x * 3 + 2] = r

    # Write in blocks
    block_rows = 64
    block = bytes(row_data) * block_rows

    with open(path, "wb") as f:
        f.write(hdr)
        f.write(dib)
        rem = height
        while rem > 0:
            count = min(block_rows, rem)
            f.write(block[:count * row_bytes])
            rem -= count

def make_valid_png(path, width, height, seed=1):
    """Generates a valid PNG truecolor RGB image with zlib compression."""
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data))

    # Procedural scanline pattern
    line = bytearray([0]) # filter none
    for x in range(width):
        r = (x * 3 + seed * 7) & 0xFF
        g = (x * 11 + seed * 13) & 0xFF
        b = ((x + seed) * 17) & 0xFF
        line.extend([r, g, b])

    raw_data = bytes(line) * height
    compressed = zlib.compress(raw_data, level=1)

    idat = struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", zlib.crc32(b"IDAT" + compressed))
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND"))

    with open(path, "wb") as f:
        f.write(sig + ihdr + idat + iend)

def make_valid_ppm(path, width, height, seed=1):
    """Generates a valid Netpbm P6 24-bit binary color pixmap."""
    hdr = f"P6\n{width} {height}\n255\n".encode("ascii")
    row = bytearray(width * 3)
    for x in range(width):
        row[x * 3] = (x * 9 + seed * 23) & 0xFF
        row[x * 3 + 1] = (x * 5 + seed * 37) & 0xFF
        row[x * 3 + 2] = (x * 13 + seed * 41) & 0xFF
    row_bytes = bytes(row)

    block_rows = 64
    block = row_bytes * block_rows

    with open(path, "wb") as f:
        f.write(hdr)
        rem = height
        while rem > 0:
            count = min(block_rows, rem)
            f.write(block[:count * len(row_bytes)])
            rem -= count

def make_valid_svg(path, title, seed=1, target_bytes=50000):
    """Generates a valid scalable vector graphics XML file."""
    shapes = []
    num_shapes = max(20, target_bytes // 250)
    for i in range(num_shapes):
        cx = (i * 37 + seed * 19) % 1800 + 100
        cy = (i * 29 + seed * 31) % 900 + 100
        r = (i * 13 + seed) % 70 + 15
        color = f"#{(i * 9999 + seed * 12345) % 0xFFFFFF:06x}"
        shapes.append(f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="0.75" stroke="#1e293b" stroke-width="2"/>')
        if i % 3 == 0:
            x1 = cx - r
            y1 = cy - r
            shapes.append(f'  <rect x="{x1}" y="{y1}" width="{r*2}" height="{r*1.5:.1f}" fill="none" stroke="{color}" stroke-dasharray="4,4"/>')

    svg_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 1200" width="100%" height="100%">\n'
        f'  <title>{title}</title>\n'
        '  <defs>\n'
        '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">\n'
        '      <stop offset="0%" stop-color="#0f172a"/>\n'
        '      <stop offset="100%" stop-color="#1e1b4b"/>\n'
        '    </linearGradient>\n'
        '  </defs>\n'
        '  <rect width="2000" height="1200" fill="url(#bgGrad)"/>\n'
        f'  <text x="80" y="100" font-family="monospace" font-size="32" fill="#38bdf8" font-weight="bold">{title}</text>\n'
        f'  <text x="80" y="140" font-family="sans-serif" font-size="18" fill="#94a3b8">Seed: {seed} | Vector Nodes: {num_shapes} | DedupFS Dataset</text>\n'
        + "\n".join(shapes) + "\n"
        '</svg>\n'
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg_content)

def make_valid_csv(path, title, seed=1, target_bytes=500000):
    """Generates a realistic structured CSV dataset of financial/sensor metrics."""
    headers = "record_id,timestamp_epoch,server_node_id,request_uri,http_status,latency_us,bytes_transferred,cache_hit,client_ip,payload_sha256\n"
    header_bytes = headers.encode("utf-8")

    row_template = "{:08d},{:d},cluster_node_{:03d},/api/v2/storage/chunks/{:08x},{:d},{:d},{:d},{:s},192.168.{:d}.{:d},{:s}\n"

    with open(path, "wb") as f:
        f.write(header_bytes)
        written = len(header_bytes)
        rec_id = 1
        base_time = 1793400000 + seed * 1000

        # Buffer writes in ~64KB batches
        batch = bytearray()
        while written < target_bytes:
            batch.clear()
            for _ in range(500):
                rec_id += 1
                node = (rec_id * 7 + seed) % 64
                status = 200 if (rec_id % 17 != 0) else 503
                latency = 120 + ((rec_id * 13) % 4500)
                b_tx = 4096 + ((rec_id * 31) % 1048576)
                hit = "TRUE" if (rec_id % 3 == 0) else "FALSE"
                ip1 = (rec_id * 3) % 254 + 1
                ip2 = (rec_id * 11) % 254 + 1
                h = hashlib.sha256(f"{rec_id}_{seed}".encode()).hexdigest()

                line = row_template.format(rec_id, base_time + rec_id, node, rec_id * 97, status, latency, b_tx, hit, ip1, ip2, h)
                batch.extend(line.encode("utf-8"))

            f.write(batch)
            written += len(batch)

def make_valid_json(path, title, seed=1, target_bytes=400000):
    """Generates a structured JSON database file with nested records."""
    prefix = f'{{\n  "dataset_title": "{title}",\n  "schema_version": "3.1.0",\n  "benchmark_seed": {seed},\n  "records": [\n'
    suffix = '\n  ]\n}\n'

    with open(path, "wb") as f:
        f.write(prefix.encode("utf-8"))
        written = len(prefix) + len(suffix)
        idx = 0
        batch = bytearray()

        while written < target_bytes:
            batch.clear()
            for _ in range(300):
                idx += 1
                comma = "," if idx > 1 else ""
                record = (
                    f'{comma}\n    {{\n'
                    f'      "id": {idx},\n'
                    f'      "uuid": "{hashlib.md5(f"{idx}_{seed}".encode()).hexdigest()}",\n'
                    f'      "device_type": "storage_controller_nvme",\n'
                    f'      "metrics": {{\n'
                    f'        "read_iops": {150000 + (idx * 17) % 50000},\n'
                    f'        "write_iops": {95000 + (idx * 13) % 30000},\n'
                    f'        "queue_depth": {(idx % 32) + 1},\n'
                    f'        "temperature_celsius": {38.5 + (idx % 15) * 0.5:.1f}\n'
                    f'      }},\n'
                    f'      "active": {"true" if idx % 2 == 0 else "false"}\n'
                    f'    }}'
                )
                batch.extend(record.encode("utf-8"))

            f.write(batch)
            written += len(batch)

        f.write(suffix.encode("utf-8"))

def make_valid_markdown(path, title, seed=1, target_bytes=100000):
    """Generates a multi-page Markdown technical guide and reference document."""
    header = (
        f"# {title}\n\n"
        f"**Author:** Advanced Systems Research Group (Seed: {seed})  \n"
        f"**Status:** Approved Technical Document  \n"
        f"**Date:** October 2026  \n\n"
        f"---\n\n"
        f"## Table of Contents\n"
        f"1. [System Architecture](#system-architecture)\n"
        f"2. [Dynamic Data Structure Sizing](#dynamic-data-structure-sizing)\n"
        f"3. [Empirical Evaluation Metrics](#empirical-evaluation-metrics)\n"
        f"4. [Detailed Telemetry Log](#detailed-telemetry-log)\n\n"
    )

    body = [header]
    for sec_title, sec_desc in MD_SECTIONS:
        body.append(f"## {sec_title}\n\n{sec_desc}\n\n")

    body.append("### Pipeline Performance Comparison Table\n\n")
    body.append("| Scan Iteration | Files Analyzed | Logical Size (MB) | Redundant Size (MB) | Dedup Ratio | Throughput (MB/s) |\n")
    body.append("|:--------------:|:--------------:|:-----------------:|:-------------------:|:-----------:|:-----------------:|\n")
    for r in range(1, 25):
        logical = r * 115.4
        wasted = logical * 0.38
        dr = logical / (logical - wasted)
        tp = 650.0 + (r * 13.5) % 250
        body.append(f"| Run #{r:02d} | {r * 120} | {logical:.1f} MB | {wasted:.1f} MB | {dr:.2f}x | {tp:.1f} MB/s |\n")

    body.append("\n```cpp\n")
    body.append("// DedupFS Core Inode Relinker Sample Code\n")
    body.append("int link_and_swap(const std::string& original, const std::string& duplicate) {\n")
    body.append("    std::string temp_link = duplicate + \".dedup_tmp\";\n")
    body.append("    if (::link(original.c_str(), temp_link.c_str()) != 0) return -1;\n")
    body.append("    if (::rename(temp_link.c_str(), duplicate.c_str()) != 0) return -2;\n")
    body.append("    return 0; // Success\n")
    body.append("}\n```\n\n")

    full_text = "".join(body)
    with open(path, "wb") as f:
        f.write(full_text.encode("utf-8"))
        written = len(full_text.encode("utf-8"))
        # Pad with technical notes to reach target_bytes if needed
        padding_block = (
            "### Extended System Telemetry Note\n"
            "Each candidate duplicate block undergoes rigorous 64KB streaming memory comparison.\n"
            "By ensuring memcmp(bufferA, bufferB, bytesRead) == 0 across the entire file range,\n"
            "cryptographic SHA-256 hash collision vulnerabilities are completely nullified.\n\n"
        ).encode("utf-8")
        while written < target_bytes:
            w = min(len(padding_block), target_bytes - written)
            f.write(padding_block[:w])
            written += w

def make_valid_html(path, title, seed=1, target_bytes=150000):
    """Generates an HTML5 executive report with embedded CSS styling and data tables."""
    html_head = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        f"  <title>{title}</title>\n"
        "  <style>\n"
        "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 2rem; }\n"
        "    .container { max-width: 1200px; margin: 0 auto; }\n"
        "    .card { background: #1e293b; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #334155; }\n"
        "    h1 { color: #38bdf8; }\n"
        "    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }\n"
        "    th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }\n"
        "    th { background: #0f172a; color: #94a3b8; }\n"
        "    .badge { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }\n"
        "    .badge-ok { background: #065f46; color: #34d399; }\n"
        "  </style>\n"
        "</head>\n<body>\n"
        f"  <div class=\"container\">\n"
        f"    <h1>{title}</h1>\n"
        f"    <p class=\"lead\">Automated Data Storage Analysis &amp; Deduplication Telemetry (Seed: {seed})</p>\n"
        "    <div class=\"card\">\n"
        "      <h2>Executive Summary</h2>\n"
        "      <p>Continuous monitoring confirms the multi-tier deduplication engine preserves 100% data fidelity while reclaiming excessive duplicate capacity.</p>\n"
        "    </div>\n"
        "    <div class=\"card\">\n"
        "      <h2>Audit Records</h2>\n"
        "      <table>\n"
        "        <thead>\n"
        "          <tr><th>ID</th><th>Cluster</th><th>Files Scanned</th><th>Redundant Bytes</th><th>Status</th></tr>\n"
        "        </thead>\n"
        "        <tbody>\n"
    )

    with open(path, "wb") as f:
        f.write(html_head.encode("utf-8"))
        written = len(html_head.encode("utf-8"))
        row_id = 0
        batch = bytearray()
        footer = "        </tbody>\n      </table>\n    </div>\n  </div>\n</body>\n</html>\n".encode("utf-8")

        while written + len(footer) < target_bytes:
            batch.clear()
            for _ in range(50):
                row_id += 1
                files = 50 + (row_id * 17) % 300
                wasted = files * 1024 * 1024 * 0.42
                row = (
                    f"          <tr>"
                    f"<td>REC-{row_id:05d}</td>"
                    f"<td>US-WEST-{row_id % 8}</td>"
                    f"<td>{files}</td>"
                    f"<td>{wasted / (1024*1024):.2f} MB</td>"
                    f"<td><span class=\"badge badge-ok\">OPTIMIZED</span></td>"
                    f"</tr>\n"
                )
                batch.extend(row.encode("utf-8"))

            f.write(batch)
            written += len(batch)

        f.write(footer)

def make_valid_txt(path, title, seed=1, target_bytes=50000):
    """Generates server log files or internal engineering memos."""
    header = f"=== SYSTEM AUDIT LOG: {title} (Seed {seed}) ===\n"
    with open(path, "wb") as f:
        f.write(header.encode("utf-8"))
        written = len(header.encode("utf-8"))
        log_id = 1
        batch = bytearray()

        while written < target_bytes:
            batch.clear()
            for _ in range(100):
                log_id += 1
                level = "[INFO]" if log_id % 10 != 0 else ("[WARN]" if log_id % 30 != 0 else "[ERROR]")
                line = f"2026-10-31 10:14:{log_id % 60:02d}.{log_id % 1000:03d} {level} [WorkerThread-{log_id % 16:02d}] Deduplication index bucket #{log_id * 13 % 4096} scanned {log_id * 512} candidate bytes.\n"
                batch.extend(line.encode("utf-8"))
            f.write(batch)
            written += len(batch)


# ----------------------------------------------------------------------
# Ground Truth Hashing Helper
# ----------------------------------------------------------------------

def compute_sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------
# Main Dataset Generation Orchestrator
# ----------------------------------------------------------------------

def generate_mixed_dataset(output_dir, target_gb=2.5, dup_ratio=0.35, seed=42, clean=False):
    t_start = time.time()
    random.seed(seed)

    if clean and os.path.exists(output_dir):
        print(f"[*] Cleaning previous dataset directory: {output_dir}")
        shutil.rmtree(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    target_total_bytes = int(target_gb * 1024 * 1024 * 1024)
    target_redundant_bytes = int(target_total_bytes * dup_ratio)
    target_unique_bytes = target_total_bytes - target_redundant_bytes

    print("================================================================================")
    print("   DedupFS High-Performance Realistic Dataset Generator")
    print("================================================================================")
    print(f"[*] Target Directory:            {os.path.abspath(output_dir)}")
    print(f"[*] Target Total Size:           {target_gb:.2f} GB ({target_total_bytes / (1024*1024):.1f} MB)")
    print(f"[*] Desired Duplication Ratio:   {dup_ratio * 100:.1f}% duplicates")
    print(f"[*] Target Base Unique Data:     {target_unique_bytes / (1024*1024):.1f} MB")
    print(f"[*] Target Redundant Duplicates: {target_redundant_bytes / (1024*1024):.1f} MB")
    print(f"[*] Deterministic Random Seed:   {seed}")
    print("--------------------------------------------------------------------------------\n")

    # Define directory layout
    doc_subdirs = [
        "documents/corporate_reports",
        "documents/financial_records",
        "documents/legal_contracts",
        "documents/research_papers",
        "documents/technical_specs"
    ]

    media_subdirs = [
        "media_images/camera_dcim",
        "media_images/scanned_documents",
        "media_images/wallpapers_and_art",
        "media_images/diagrams_and_vectors"
    ]

    dest_subdirs = [
        "downloads_inbox",
        "backups_and_snapshots/quarterly_archive_docs",
        "backups_and_snapshots/photo_vault_backup",
        "shared_team_assets"
    ]

    edge_case_subdirs = [
        "dedup_edge_cases/size_collision",
        "dedup_edge_cases/prefix_collision",
        "dedup_edge_cases/eof_single_byte_diff"
    ]

    all_dirs = doc_subdirs + media_subdirs + dest_subdirs + edge_case_subdirs
    for d in all_dirs:
        os.makedirs(os.path.join(output_dir, d), exist_ok=True)

    # ------------------------------------------------------------------
    # Step 1: Generate Base Unique Files (~50% Documents, ~50% Images)
    # ------------------------------------------------------------------
    print("[*] STEP 1: Synthesizing Base Unique Documents & Images...")
    unique_files = [] # list of dicts: {path, size, category, format, sha256}
    current_unique_bytes = 0
    file_counter = 0

    # Image resolution pools for realistic file sizes
    bmp_resolutions = [
        (1024, 768),    # ~2.3 MB
        (1280, 720),    # ~2.6 MB
        (1280, 1024),   # ~3.8 MB
        (1600, 1200),   # ~5.5 MB
        (1920, 1080),   # ~5.9 MB
        (2048, 1536),   # ~9.0 MB
        (2560, 1440),   # ~10.5 MB
    ]

    ppm_resolutions = [
        (800, 600),     # ~1.4 MB
        (1024, 768),    # ~2.3 MB
        (1280, 720),    # ~2.6 MB
        (1600, 900),    # ~4.1 MB
    ]

    png_resolutions = [
        (800, 600),     # ~100KB - 800KB
        (1024, 768),
        (1280, 720),
        (1920, 1080),
    ]

    last_print = time.time()

    while current_unique_bytes < target_unique_bytes:
        file_counter += 1
        # Alternate roughly 50% documents and 50% images
        is_image = (file_counter % 2 == 0)

        if is_image:
            # Pick image format
            img_type = random.choices(["bmp", "png", "ppm", "svg"], weights=[45, 30, 20, 5])[0]
            if img_type == "bmp":
                subdir = random.choice(["media_images/camera_dcim", "media_images/scanned_documents", "media_images/wallpapers_and_art"])
                fname = f"IMG_RAW_{file_counter:05d}.bmp"
                w, h = random.choice(bmp_resolutions)
                fpath = os.path.join(output_dir, subdir, fname)
                make_valid_bmp(fpath, w, h, seed=file_counter)
                category = "Images"
                fmt = "BMP"
            elif img_type == "png":
                subdir = random.choice(["media_images/camera_dcim", "media_images/scanned_documents", "media_images/wallpapers_and_art"])
                fname = f"PHOTO_EXPORT_{file_counter:05d}.png"
                w, h = random.choice(png_resolutions)
                fpath = os.path.join(output_dir, subdir, fname)
                make_valid_png(fpath, w, h, seed=file_counter)
                category = "Images"
                fmt = "PNG"
            elif img_type == "ppm":
                subdir = "media_images/wallpapers_and_art"
                fname = f"RASTER_SPECTRUM_{file_counter:05d}.ppm"
                w, h = random.choice(ppm_resolutions)
                fpath = os.path.join(output_dir, subdir, fname)
                make_valid_ppm(fpath, w, h, seed=file_counter)
                category = "Images"
                fmt = "PPM"
            else: # SVG
                subdir = "media_images/diagrams_and_vectors"
                fname = f"VECTOR_DIAGRAM_{file_counter:05d}.svg"
                target_sz = random.randint(30_000, 120_000)
                fpath = os.path.join(output_dir, subdir, fname)
                title = f"DedupFS Vector Topology #{file_counter}"
                make_valid_svg(fpath, title, seed=file_counter, target_bytes=target_sz)
                category = "Images"
                fmt = "SVG"
        else:
            # Pick document format
            doc_type = random.choices(["pdf", "csv", "json", "markdown", "html", "txt"], weights=[35, 25, 15, 10, 10, 5])[0]
            if doc_type == "pdf":
                subdir = random.choice(["documents/corporate_reports", "documents/legal_contracts", "documents/research_papers"])
                fname = f"REPORT_DOC_{file_counter:05d}.pdf"
                title = random.choice(REPORT_TITLES)
                author = random.choice(AUTHORS)
                extra = random.randint(100_000, 3_500_000)
                fpath = os.path.join(output_dir, subdir, fname)
                make_valid_pdf(fpath, title, author, extra_bytes=extra)
                category = "Documents"
                fmt = "PDF"
            elif doc_type == "csv":
                subdir = "documents/financial_records"
                fname = f"FINANCIAL_LEDGER_{file_counter:05d}.csv"
                target_sz = random.randint(300_000, 4_500_000)
                fpath = os.path.join(output_dir, subdir, fname)
                make_valid_csv(fpath, f"Ledger #{file_counter}", seed=file_counter, target_bytes=target_sz)
                category = "Documents"
                fmt = "CSV"
            elif doc_type == "json":
                subdir = "documents/financial_records"
                fname = f"TELEMETRY_DATASET_{file_counter:05d}.json"
                target_sz = random.randint(200_000, 2_000_000)
                fpath = os.path.join(output_dir, subdir, fname)
                make_valid_json(fpath, f"Telemetry #{file_counter}", seed=file_counter, target_bytes=target_sz)
                category = "Documents"
                fmt = "JSON"
            elif doc_type == "markdown":
                subdir = "documents/research_papers"
                fname = f"ARCHITECTURE_SPEC_{file_counter:05d}.md"
                target_sz = random.randint(30_000, 250_000)
                fpath = os.path.join(output_dir, subdir, fname)
                make_valid_markdown(fpath, f"Deduplication Architecture Spec #{file_counter}", seed=file_counter, target_bytes=target_sz)
                category = "Documents"
                fmt = "Markdown"
            elif doc_type == "html":
                subdir = "documents/corporate_reports"
                fname = f"EXECUTIVE_DASHBOARD_{file_counter:05d}.html"
                target_sz = random.randint(50_000, 350_000)
                fpath = os.path.join(output_dir, subdir, fname)
                make_valid_html(fpath, f"Executive Audit Dashboard #{file_counter}", seed=file_counter, target_bytes=target_sz)
                category = "Documents"
                fmt = "HTML"
            else: # txt
                subdir = "documents/technical_specs"
                fname = f"SYSTEM_DEBUG_{file_counter:05d}.log"
                target_sz = random.randint(20_000, 150_000)
                fpath = os.path.join(output_dir, subdir, fname)
                make_valid_txt(fpath, f"Diagnostic Trace #{file_counter}", seed=file_counter, target_bytes=target_sz)
                category = "Documents"
                fmt = "Text"

        fsize = os.path.getsize(fpath)
        current_unique_bytes += fsize
        unique_files.append({
            "path": fpath,
            "rel_path": os.path.relpath(fpath, output_dir),
            "size": fsize,
            "category": category,
            "format": fmt
        })

        if time.time() - last_print > 1.5:
            last_print = time.time()
            progress_pct = (current_unique_bytes / target_unique_bytes) * 100.0
            print(f"  [>] Synthesized {len(unique_files)} unique files ({current_unique_bytes / (1024*1024):.1f} MB / {target_unique_bytes / (1024*1024):.1f} MB - {progress_pct:.1f}%)")

    print(f"[+] Unique Base Files Complete: {len(unique_files)} files ({current_unique_bytes / (1024*1024):.2f} MB)")

    # ------------------------------------------------------------------
    # Step 2: Inject Deduplication Edge Cases (Size collision, Prefix, EOF)
    # ------------------------------------------------------------------
    print("\n[*] STEP 2: Injecting Special Deduplication Edge Cases...")
    edge_cases = []

    # Edge Case A: Size Collisions (Exact same byte size, completely different data)
    size_col_dir = os.path.join(output_dir, "dedup_edge_cases/size_collision")
    col_size = 1048576 # 1 MB exact
    for i in range(1, 4):
        pA = os.path.join(size_col_dir, f"size_match_pair_{i:02d}_fileA.dat")
        pB = os.path.join(size_col_dir, f"size_match_pair_{i:02d}_fileB.dat")
        # Generate independent pseudo-random blocks
        with open(pA, "wb") as f:
            f.write(bytes([i * 17 % 256]) * col_size)
        with open(pB, "wb") as f:
            f.write(bytes([i * 31 % 256]) * col_size)
        current_unique_bytes += (col_size * 2)
        unique_files.append({"path": pA, "rel_path": os.path.relpath(pA, output_dir), "size": col_size, "category": "EdgeCase", "format": "DAT"})
        unique_files.append({"path": pB, "rel_path": os.path.relpath(pB, output_dir), "size": col_size, "category": "EdgeCase", "format": "DAT"})
        edge_cases.append({"type": "size_collision", "files": [pA, pB], "size": col_size})

    # Edge Case B: Prefix Collisions (Same 4096-byte prefix, different body)
    pref_col_dir = os.path.join(output_dir, "dedup_edge_cases/prefix_collision")
    pref_size = 262144 # 256 KB
    common_prefix = bytes([0xAA] * 4096)
    for i in range(1, 4):
        pA = os.path.join(pref_col_dir, f"prefix_shared_pair_{i:02d}_alpha.dat")
        pB = os.path.join(pref_col_dir, f"prefix_shared_pair_{i:02d}_beta.dat")
        with open(pA, "wb") as f:
            f.write(common_prefix)
            f.write(bytes([i * 7 % 256]) * (pref_size - 4096))
        with open(pB, "wb") as f:
            f.write(common_prefix)
            f.write(bytes([i * 23 % 256]) * (pref_size - 4096))
        current_unique_bytes += (pref_size * 2)
        unique_files.append({"path": pA, "rel_path": os.path.relpath(pA, output_dir), "size": pref_size, "category": "EdgeCase", "format": "DAT"})
        unique_files.append({"path": pB, "rel_path": os.path.relpath(pB, output_dir), "size": pref_size, "category": "EdgeCase", "format": "DAT"})
        edge_cases.append({"type": "prefix_collision", "files": [pA, pB], "size": pref_size})

    # Edge Case C: Single-byte EOF difference (Identical for 128KB except last byte)
    eof_dir = os.path.join(output_dir, "dedup_edge_cases/eof_single_byte_diff")
    eof_size = 131072 # 128 KB
    base_block = bytes([0x55] * (eof_size - 1))
    for i in range(1, 3):
        pA = os.path.join(eof_dir, f"eof_diff_pair_{i:02d}_orig.dat")
        pB = os.path.join(eof_dir, f"eof_diff_pair_{i:02d}_mutated.dat")
        with open(pA, "wb") as f:
            f.write(base_block)
            f.write(b"\x00")
        with open(pB, "wb") as f:
            f.write(base_block)
            f.write(b"\x01")
        current_unique_bytes += (eof_size * 2)
        unique_files.append({"path": pA, "rel_path": os.path.relpath(pA, output_dir), "size": eof_size, "category": "EdgeCase", "format": "DAT"})
        unique_files.append({"path": pB, "rel_path": os.path.relpath(pB, output_dir), "size": eof_size, "category": "EdgeCase", "format": "DAT"})
        edge_cases.append({"type": "eof_single_byte_diff", "files": [pA, pB], "size": eof_size})

    print(f"[+] Edge Cases Injected: {len(edge_cases)} adversarial test pairs.")

    # ------------------------------------------------------------------
    # Step 3: Compute Exact SHA-256 Hashes for Unique Files
    # ------------------------------------------------------------------
    print("\n[*] STEP 3: Indexing Base File Fingerprints (OpenSSL SHA-256)...")
    for idx, item in enumerate(unique_files):
        item["sha256"] = compute_sha256(item["path"])
        if idx % 150 == 0 and idx > 0:
            print(f"  [>] Fingerprinted {idx}/{len(unique_files)} files...")

    # ------------------------------------------------------------------
    # Step 4: Replicate Duplicate Copies into Realistic Folders
    # ------------------------------------------------------------------
    print("\n[*] STEP 4: Creating Duplicate Replicas across realistic user directories...")
    print(f"    (Target Redundant Size: {target_redundant_bytes / (1024*1024):.2f} MB)")

    # Exclude edge cases from duplicate replication so they remain pure negative testcases
    replicable_pool = [f for f in unique_files if f["category"] != "EdgeCase"]
    random.shuffle(replicable_pool)

    # We will track duplicate clusters: sha256 -> list of all file paths
    duplicate_clusters = {}
    for item in unique_files:
        duplicate_clusters[item["sha256"]] = [item["rel_path"]]

    redundant_bytes_created = 0
    duplicate_copies_count = 0
    rep_idx = 0

    while redundant_bytes_created < target_redundant_bytes and rep_idx < len(replicable_pool):
        orig = replicable_pool[rep_idx]
        rep_idx += 1
        orig_name = os.path.basename(orig["path"])
        name_no_ext, ext = os.path.splitext(orig_name)

        # Decide how many duplicates to make: 1 copy (70%), 2 copies (20%), 3 copies (10%)
        num_copies = random.choices([1, 2, 3], weights=[70, 20, 10])[0]

        for c in range(1, num_copies + 1):
            if redundant_bytes_created >= target_redundant_bytes:
                break

            # Pick target directory realistically
            dest_choice = random.choices(
                ["downloads", "backup_docs", "backup_photos", "shared_team"],
                weights=[40, 25, 20, 15]
            )[0]

            if dest_choice == "downloads":
                target_sub = "downloads_inbox"
                # realistic user download naming variations
                name_variant = random.choice([
                    f"{name_no_ext} (1){ext}",
                    f"{name_no_ext} (Copy){ext}",
                    f"{name_no_ext}_download{ext}",
                    f"copy_of_{orig_name}",
                    orig_name # identical name in downloads!
                ])
            elif dest_choice == "backup_docs":
                target_sub = "backups_and_snapshots/quarterly_archive_docs"
                name_variant = f"archive_q3_{orig_name}"
            elif dest_choice == "backup_photos":
                target_sub = "backups_and_snapshots/photo_vault_backup"
                name_variant = f"backup_snapshot_{orig_name}"
            else:
                target_sub = "shared_team_assets"
                name_variant = f"shared_template_{orig_name}"

            dup_path = os.path.join(output_dir, target_sub, name_variant)
            # Avoid collision if name already exists
            if os.path.exists(dup_path):
                dup_path = os.path.join(output_dir, target_sub, f"dup_{duplicate_copies_count}_{orig_name}")

            # Ultra-fast kernel-level file copy
            shutil.copyfile(orig["path"], dup_path)

            duplicate_clusters[orig["sha256"]].append(os.path.relpath(dup_path, output_dir))
            redundant_bytes_created += orig["size"]
            duplicate_copies_count += 1

    # Filter duplicate clusters to only those that actually have duplicates (count >= 2)
    active_dup_clusters = {k: v for k, v in duplicate_clusters.items() if len(v) > 1}

    total_files_count = len(unique_files) + duplicate_copies_count
    total_logical_bytes = current_unique_bytes + redundant_bytes_created
    dedup_ratio = total_logical_bytes / (total_logical_bytes - redundant_bytes_created)
    savings_pct = (1.0 - (1.0 / dedup_ratio)) * 100.0

    # ------------------------------------------------------------------
    # Step 5: Generate Detailed Format and Category Breakdown
    # ------------------------------------------------------------------
    format_stats = {}
    category_stats = {}

    for root, _, files in os.walk(output_dir):
        for f in files:
            if f == "ground_truth_manifest.json":
                continue
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)
            ext = os.path.splitext(f)[1].lower() or ".none"
            format_stats[ext] = format_stats.get(ext, {"count": 0, "bytes": 0})
            format_stats[ext]["count"] += 1
            format_stats[ext]["bytes"] += sz

            # Category check
            rel = os.path.relpath(fp, output_dir)
            cat = rel.split(os.sep)[0]
            category_stats[cat] = category_stats.get(cat, {"count": 0, "bytes": 0})
            category_stats[cat]["count"] += 1
            category_stats[cat]["bytes"] += sz

    # ------------------------------------------------------------------
    # Step 6: Export Ground Truth Manifest JSON
    # ------------------------------------------------------------------
    manifest = {
        "metadata": {
            "dataset_name": "DedupFS Mixed Documents & Images Benchmark Dataset",
            "generator_version": "2.0.0",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target_gb_setting": target_gb,
            "dup_ratio_setting": dup_ratio,
            "random_seed": seed,
            "root_directory": os.path.abspath(output_dir)
        },
        "ground_truth_summary": {
            "total_files": total_files_count,
            "unique_original_files": len(unique_files),
            "redundant_duplicate_copies": duplicate_copies_count,
            "total_logical_bytes": total_logical_bytes,
            "unique_original_bytes": current_unique_bytes,
            "wasted_duplicate_bytes": redundant_bytes_created,
            "reclaimable_space_mb": round(redundant_bytes_created / (1024 * 1024), 2),
            "expected_dedup_ratio": round(dedup_ratio, 4),
            "expected_space_savings_pct": round(savings_pct, 2)
        },
        "format_breakdown": {
            ext: {
                "count": data["count"],
                "total_mb": round(data["bytes"] / (1024 * 1024), 2)
            } for ext, data in sorted(format_stats.items(), key=lambda x: x[1]["bytes"], reverse=True)
        },
        "directory_breakdown": {
            cat: {
                "count": data["count"],
                "total_mb": round(data["bytes"] / (1024 * 1024), 2)
            } for cat, data in sorted(category_stats.items(), key=lambda x: x[1]["bytes"], reverse=True)
        },
        "edge_cases": edge_cases,
        "duplicate_groups_count": len(active_dup_clusters),
        "duplicate_clusters": active_dup_clusters
    }

    manifest_path = os.path.join(output_dir, "ground_truth_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    total_time = time.time() - t_start

    print("\n================================================================================")
    print("   DATASET GENERATION FINISHED SUCCESSFULLY!")
    print("================================================================================")
    print(f"  Total Files Generated:       {total_files_count}")
    print(f"  Unique Original Files:       {len(unique_files)}")
    print(f"  Redundant Duplicate Copies:  {duplicate_copies_count}")
    print(f"  Duplicate Equivalence Groups:{len(active_dup_clusters)}")
    print(f"  Total Logical Dataset Size:  {total_logical_bytes / (1024*1024*1024):.2f} GB ({total_logical_bytes / (1024*1024):.1f} MB)")
    print(f"  Unique Physical Footprint:   {current_unique_bytes / (1024*1024*1024):.2f} GB ({current_unique_bytes / (1024*1024):.1f} MB)")
    print(f"  Wasted Duplicate Size:       {redundant_bytes_created / (1024*1024):.2f} MB")
    print(f"  Expected Deduplication Ratio:{dedup_ratio:.2f}x (Space Savings: {savings_pct:.2f}%)")
    print(f"  Total Wall-Clock Time:       {total_time:.2f} seconds ({total_logical_bytes / (1024*1024) / total_time:.1f} MB/s)")
    print(f"  Ground Truth Manifest Saved: {manifest_path}")
    print("--------------------------------------------------------------------------------")
    print("Format Distribution:")
    for ext, st in sorted(format_stats.items(), key=lambda x: x[1]["bytes"], reverse=True):
        print(f"    {ext:10s}: {st['count']:4d} files | {st['bytes'] / (1024*1024):7.2f} MB")
    print("--------------------------------------------------------------------------------")
    print("\nRun DedupFS scan:")
    print(f"  ./bin/dedupfs scan {output_dir}")
    print("Run DedupFS dry-run audit:")
    print(f"  ./bin/dedupfs scan {output_dir} --verbose")
    print("Run DedupFS POSIX atomic optimization:")
    print(f"  ./bin/dedupfs optimize {output_dir}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DedupFS Mixed Documents & Images Dataset Generator")
    parser.add_argument("--output-dir", default="./datasets/mixed_docs_images", help="Destination directory path")
    parser.add_argument("--target-gb", type=float, default=2.5, help="Target total logical size in Gigabytes (e.g. 2.5)")
    parser.add_argument("--dup-ratio", type=float, default=0.35, help="Target duplicate fraction (0.0 to 1.0, e.g. 0.35)")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")
    parser.add_argument("--clean", action="store_true", help="Remove existing output directory before generating")
    parser.add_argument("--quick", action="store_true", help="Quick mode for testing (~250 MB)")
    args = parser.parse_args()

    target_gb = 0.25 if args.quick else args.target_gb
    generate_mixed_dataset(
        output_dir=args.output_dir,
        target_gb=target_gb,
        dup_ratio=args.dup_ratio,
        seed=args.seed,
        clean=args.clean
    )

