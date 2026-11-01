#!/usr/bin/env python3
"""
DedupFS Professional Academic Presentation Generator
Generates a 16:9 widescreen presentation for M.Tech Advanced Data Structures.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pathlib import Path

# Color Palette (Clean Academic Theme)
BG_DARK = RGBColor(11, 17, 32)        # #0B1120
BG_CARD = RGBColor(19, 29, 49)        # #131D31
BG_ACCENT = RGBColor(30, 41, 59)      # #1E293B
BORDER_COLOR = RGBColor(51, 65, 85)   # #334155

COLOR_CYAN = RGBColor(56, 189, 248)   # #38BDF8
COLOR_EMERALD = RGBColor(52, 211, 153)# #34D399
COLOR_AMBER = RGBColor(251, 191, 36)  # #FBBF24
COLOR_PURPLE = RGBColor(168, 85, 247) # #A855F7
COLOR_WHITE = RGBColor(248, 250, 252)
COLOR_MUTED = RGBColor(148, 163, 184) # #94A3B8

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="ADVANCED DATA STRUCTURES (CS503)"):
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.4))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_CYAN

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

def add_card(slide, left, top, width, height, border_color=BORDER_COLOR, bg_color=BG_CARD):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    return shape

def add_footer(slide, current_page, total_pages=13):
    foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.3))
    tf = foot_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"DedupFS | Aryan Ravi Zodape (206126006) & Jyotiraditya Kumar (206126014) | Slide {current_page} of {total_pages}"
    p.font.size = Pt(9)
    p.font.color.rgb = COLOR_MUTED

def build_presentation(output_path="presentation/DedupFS_MTech_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, BG_DARK)
    add_card(s1, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), border_color=COLOR_CYAN, bg_color=BG_CARD)

    t_box = s1.shapes.add_textbox(Inches(1.5), Inches(1.6), Inches(10.3), Inches(2.2))
    tf = t_box.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "M.TECH CSE PROJECT PRESENTATION"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_CYAN

    p1 = tf.add_paragraph()
    p1.text = "DedupFS: File-Level Storage Deduplication System"
    p1.font.size = Pt(30)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_before = Pt(8)

    p2 = tf.add_paragraph()
    p2.text = "Hierarchical I/O Pruning, Bloom Filter Probing, and Inverted Chained Hash Table"
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLOR_MUTED
    p2.space_before = Pt(6)

    # Details Cards inside Title Slide
    add_card(s1, Inches(1.5), Inches(4.2), Inches(4.8), Inches(1.6), border_color=BORDER_COLOR, bg_color=BG_DARK)
    b1 = s1.shapes.add_textbox(Inches(1.7), Inches(4.3), Inches(4.4), Inches(1.4))
    tf1 = b1.text_frame
    p_auth_title = tf1.paragraphs[0]
    p_auth_title.text = "PROJECT STUDENTS"
    p_auth_title.font.size = Pt(11)
    p_auth_title.font.bold = True
    p_auth_title.font.color.rgb = COLOR_CYAN

    p_a1 = tf1.add_paragraph()
    p_a1.text = "• Aryan Ravi Zodape (Roll No: 206126006)"
    p_a1.font.size = Pt(12)
    p_a1.font.color.rgb = COLOR_WHITE
    p_a1.space_before = Pt(4)

    p_a2 = tf1.add_paragraph()
    p_a2.text = "• Jyotiraditya Kumar (Roll No: 206126014)"
    p_a2.font.size = Pt(12)
    p_a2.font.color.rgb = COLOR_WHITE

    add_card(s1, Inches(6.8), Inches(4.2), Inches(5.0), Inches(1.6), border_color=BORDER_COLOR, bg_color=BG_DARK)
    b2 = s1.shapes.add_textbox(Inches(7.0), Inches(4.3), Inches(4.6), Inches(1.4))
    tf2 = b2.text_frame
    p_acad_title = tf2.paragraphs[0]
    p_acad_title.text = "ACADEMIC DETAILS"
    p_acad_title.font.size = Pt(11)
    p_acad_title.font.bold = True
    p_acad_title.font.color.rgb = COLOR_EMERALD

    p_c1 = tf2.add_paragraph()
    p_c1.text = "• Course: Advanced Data Structures (CS503)"
    p_c1.font.size = Pt(12)
    p_c1.font.color.rgb = COLOR_WHITE
    p_c1.space_before = Pt(4)

    p_c2 = tf2.add_paragraph()
    p_c2.text = "• Program: M.Tech Computer Science & Engineering (Sem 1)"
    p_c2.font.size = Pt(12)
    p_c2.font.color.rgb = COLOR_WHITE

    add_footer(s1, 1)

    # =========================================================================
    # SLIDE 2: MOTIVATION & PROBLEM DEFINITION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, BG_DARK)
    add_header(s2, "Problem Statement & Motivation")

    add_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Redundancy Problem"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    prob_points = [
        ("Storage Overhead from Duplicate Files:", "In software repositories, cloud storage, datasets, and user workstations, duplicate files commonly consume 20% to 50%+ of physical storage."),
        ("Intractability of Naive Pairwise Checks:", "Directly comparing all file pairs requires O(N²) comparisons. For 50,000 files, this requires >1.2 billion comparisons, causing excessive disk I/O thrashing."),
        ("I/O Bottleneck of Unfiltered Hashing:", "Computing full cryptographic digests (e.g. SHA-256) on every file forces the OS to read gigabytes of data from disk, even though most files have unique sizes.")
    ]
    for title, desc in prob_points:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(10)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(12)
        pd.font.color.rgb = COLOR_MUTED

    add_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=COLOR_EMERALD)
    b = s2.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Proposed System Design"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD

    sol_points = [
        ("Multi-Tier I/O Filtering Pipeline:", "Tier 1 size bucketing eliminates ~25% of unique files in O(1) time with 0 disk reads. Tier 2 tests 4KB Murmur3 prefix hashes to discard header mismatches early."),
        ("Probabilistic Bloom Filter Pre-Check:", "A dynamically sized bitset using Kirsch-Mitzenmacher double-hashing eliminates non-duplicate candidates in memory with Zero False Negatives (FN = 0)."),
        ("Inverted Chained Hash Table:", "Indexes duplicate candidates into equivalence classes in memory, enforcing load factor λ ≤ 0.75 via dynamic capacity doubling."),
        ("Atomic Storage Consolidation:", "Consolidates duplicate directory entries onto a single canonical inode using POSIX link() + rename(), safely freeing duplicate blocks.")
    ]
    for title, desc in sol_points:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(12)
        pd.font.color.rgb = COLOR_MUTED

    add_footer(s2, 2)

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE & PROCESSING PIPELINE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, BG_DARK)
    add_header(s3, "System Architecture & Processing Pipeline")

    stages = [
        ("1. Directory Traversal", "Recursively scans target storage tree, tracking (st_dev, st_ino) keys to prevent circular traversal over symlinks and hard links."),
        ("2. Tier 1: Size Bucketing", "Groups files by byte size via stat(2). Files with unique sizes are eliminated immediately with zero physical disk reads (~25% pruned)."),
        ("3. Tier 2: 4KB Prefix Hash", "Reads only the initial 4,096 bytes and computes 128-bit MurmurHash3. Mismatched file headers are discarded without reading entire file bodies."),
        ("4. Tier 3: SHA-256 Digest", "Only candidate files sharing both size and prefix undergo full SHA-256 fingerprinting using hardware-accelerated OpenSSL streaming."),
        ("5. Bloom Filter & Hash Table", "Queries optimal Bloom filter bitset in O(k) CPU operations. Candidate matches are inserted into the primary chained hash table."),
        ("6. Byte Check & Consolidation", "Performs 64KB binary memcmp byte verification, then consolidates duplicates via atomic POSIX hard links (link + rename).")
    ]

    for i, (title, desc) in enumerate(stages):
        col = i % 3
        row = i // 3
        left = Inches(0.8 + col * 4.0)
        top = Inches(1.6 + row * 2.6)
        add_card(s3, left, top, Inches(3.7), Inches(2.3))

        tb = s3.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), Inches(3.3), Inches(2.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_CYAN

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED
        p2.space_before = Pt(6)

    add_footer(s3, 3)

    # =========================================================================
    # SLIDE 4: BLOOM FILTER DESIGN & PROBING
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, BG_DARK)
    add_header(s4, "Probabilistic Filtering: Bloom Filter Design")

    add_card(s4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Mathematical Formulation & Sizing"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    bf_math = [
        ("Optimal Bitset Size (m):", "Given expected items n and target false positive probability p:\nm = - (n · ln p) / (ln 2)² ≈ -2.08136 · n · ln(p)\nFor n = 100,000 and p = 0.01, m = 958,506 bits (117 KB RAM)."),
        ("Optimal Hash Function Count (k):", "k = (m / n) · ln 2 ≈ 0.69315 · (m / n)\nFor p = 0.01 (1%), optimal k = 7 hash functions."),
        ("Kirsch-Mitzenmacher Double-Hashing:", "Instead of k independent hash computations, two 64-bit words (h₁, h₂) extracted from SHA-256 simulate k independent hash probes:\ng_i(x) = (h₁(x) + i · h₂(x)) mod m"),
        ("Zero False Negatives Invariant (FN = 0):", "If any bit probe in g_i(x) is 0, the element is guaranteed not present. True negatives bypass secondary hash table lookups completely.")
    ]
    for title, desc in bf_math:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_card(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=COLOR_CYAN)
    b = s4.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Observed Empirical Performance"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    bf_obs = [
        ("Memory Footprint:", "Consumes only 117.0 KB of memory for 100,000 files (1.17 bytes per file), fitting entirely in CPU L2/L3 cache."),
        ("Observed Bitset Saturation:", "Fill ratio remains at ~1.46% to 4.0% across test runs, well below the 50% critical threshold where false positives escalate."),
        ("Empirical False Positive Rate:", "Empirical FPR = 0.00% across all benchmark tiers (0 observed false positives among thousands of negative queries)."),
        ("CPU Efficiency:", "Kirsch-Mitzenmacher probes evaluate in ~15 nanoseconds per file using fast arithmetic instead of multiple hash passes.")
    ]
    for title, desc in bf_obs:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_footer(s4, 4)

    # =========================================================================
    # SLIDE 5: HASH TABLE WITH SEPARATE CHAINING
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, BG_DARK)
    add_header(s5, "Index Structure: Hash Table with Separate Chaining")

    add_card(s5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Table Architecture & Rehashing"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    ht_points = [
        ("Separate Chaining Design:", "Array of bucket heads pointing to singly-linked list nodes. Each node stores an entry (Hash256 key, vector<FileInfo> files)."),
        ("Load Factor Threshold (λ ≤ 0.75):", "λ = N / buckets. When λ exceeds 0.75, table capacity dynamically doubles (2×) to preserve amortized O(1) operations."),
        ("Fast Power-of-Two Modulo:", "Buckets are sized to powers of two, replacing expensive integer division with fast bitwise AND: bucket = hash & (capacity - 1)."),
        ("Memory Footprint:", "Consumes ~4.2 MB total RAM for 23,380 entries, scaling linearly with dataset size.")
    ]
    for title, desc in ht_points:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_card(s5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=COLOR_CYAN)
    b = s5.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Collision Dispersion & Chain Diagnostics"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    ht_diag = [
        ("Empirical Load Factor:", "Observed load factor λ = 0.384 across test runs (well below the 0.75 rehash threshold)."),
        ("Maximum Chain Depth:", "Longest bucket chain observed across 23,000+ files was only 3 elements, confirming near-optimal O(1) lookup."),
        ("Chain Length Variance (σ² = 0.26):", "Low variance confirms cryptographic SHA-256 distributes keys uniformly without clustering into bucket hotspots."),
        ("Automatic Rehash Expansions:", "Observed 4 dynamic table doublings during benchmark execution without memory fragmentation.")
    ]
    for title, desc in ht_diag:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_footer(s5, 5)

    # =========================================================================
    # SLIDE 6: MULTI-TIER FILTERING STRATEGY
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, BG_DARK)
    add_header(s6, "Multi-Tier I/O Filtering Strategy")

    tier_cards = [
        ("Tier 1: File Size Grouping", "O(1) Metadata Pruning", COLOR_CYAN, [
            "Queries file sizes via stat(2) during directory traversal.",
            "Files with unique byte sizes are eliminated immediately without reading disk data.",
            "Prunes ~23% to 30% of unique files with ZERO disk read I/O."
        ]),
        ("Tier 2: 4KB Prefix Hashing", "128-Bit MurmurHash3", COLOR_AMBER, [
            "Reads only the initial 4,096 bytes of files sharing identical sizes.",
            "Eliminates files with identical sizes but distinct file headers or magic numbers.",
            "Prunes an additional 10% to 15% of candidates with minimal disk seek overhead."
        ]),
        ("Tier 3: Full SHA-256 Digest", "Cryptographic Fingerprinting", COLOR_EMERALD, [
            "Only surviving candidates sharing size and prefix undergo full cryptographic hashing.",
            "Uses hardware-accelerated OpenSSL streaming in 64KB chunks.",
            "Total disk read volume reduced by >80% compared to naive full-file hashing."
        ])
    ]

    for i, (title, sub, col, items) in enumerate(tier_cards):
        left = Inches(0.8 + i * 4.0)
        add_card(s6, left, Inches(1.6), Inches(3.7), Inches(5.1), border_color=col)
        tb = s6.shapes.add_textbox(left + Inches(0.2), Inches(1.8), Inches(3.3), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED
        p2.space_before = Pt(4)

        for item in items:
            p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_WHITE
            p.space_before = Pt(10)

    add_footer(s6, 6)

    # =========================================================================
    # SLIDE 7: STORAGE CONSOLIDATION & POSIX HARD LINKS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, BG_DARK)
    add_header(s7, "Safe Inode Consolidation via POSIX Hard Links")

    add_card(s7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Two-Step Atomic Consolidation"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    steps = [
        ("Step 1: Create Temporary Link", "link(canonical_path, temp_path)\nCreates a new directory entry pointing to the canonical physical inode (st_ino)."),
        ("Step 2: Atomic Rename Replacement", "rename(temp_path, duplicate_path)\nAtomically replaces duplicate path with the hard link in a single POSIX system call."),
        ("Crash Safety Guarantee:", "POSIX rename() is atomic at the filesystem level. If power fails mid-operation, either the original file or the new hard link exists—the path is never missing or unlinked."),
        ("Kernel Space Deallocation:", "The OS increments st_nlink on the canonical inode and immediately deallocates the redundant disk blocks, freeing space instantly.")
    ]
    for title, desc in steps:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_card(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=COLOR_EMERALD)
    b = s7.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Byte Verification & Cycle Detection"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD

    safeguards = [
        ("Streaming Byte Verification:", "Executes 64KB binary memcmp byte-for-byte comparison between candidate files before any link modification, eliminating hash collision risk."),
        ("Inode Cycle Detection:", "Tracks composite 64-bit device-inode keys to detect filesystem circularity and prevent infinite directory loops."),
        ("Hard-Link Skip Logic (st_nlink > 1):", "Detects files that already share an inode from previous runs and skips redundant consolidation."),
        ("Cross-Device Safeguard:", "Verifies st_dev to ensure source and destination reside on the same filesystem mount point before attempting link().")
    ]
    for title, desc in safeguards:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_footer(s7, 7)

    # =========================================================================
    # SLIDE 8: EXPERIMENTAL SETUP & DATASETS
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, BG_DARK)
    add_header(s8, "Experimental Setup & Benchmark Datasets")

    add_card(s8, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s8.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Dual-Folder Testing Methodology"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    arch_pts = [
        ("ground_truth/ (Untouched Copy):", "Stores the pristine original dataset with independent physical inodes. Never altered during testing."),
        ("work/ (Active Test Directory):", "Working directory where DedupFS runs scan and optimize operations."),
        ("Instant Work Directory Reset:", "The active work/ directory can be restored from ground_truth/ in seconds via the UI or CLI for clean reproducible benchmarks."),
        ("Automated Ground Truth Verification:", "A verification script performs bit-for-bit equivalence checks across all files to confirm zero file corruption.")
    ]
    for title, desc in arch_pts:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_card(s8, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=COLOR_CYAN)
    b = s8.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Benchmark Dataset Tiers"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    tiers = [
        ("Small Dataset (~280 MB, 9,516 files):", "Resumes PDF corpus, Microsoft COCO images, curl source repository, and nested test archives."),
        ("Medium Dataset (~1.09 GB, 23,380 files):", "Resumes PDF corpus, Microsoft COCO images, complete Linux kernel core tree, and CSV datasets."),
        ("Large Enterprise Dataset (~3.99 GB, 58,629 files):", "Dual full Linux kernel trees (v6.10 and v6.11), high-resolution photo corpora, and document datasets."),
        ("Realistic Duplication Topology:", "Incorporates duplicate files across different folders, renamed duplicates, and deep directory nesting.")
    ]
    for title, desc in tiers:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_footer(s8, 8)

    # =========================================================================
    # SLIDE 9: EXPERIMENTAL RESULTS & PERFORMANCE
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, BG_DARK)
    add_header(s9, "Experimental Results: Storage Savings & Performance")

    table_shape = s9.shapes.add_table(4, 7, Inches(0.8), Inches(1.6), Inches(11.7), Inches(2.2))
    table = table_shape.table

    headers = ["Dataset Tier", "Total Files", "Logical Size", "Storage Saved", "Savings %", "Throughput", "Peak RAM"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_ACCENT
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_CYAN
        p.alignment = PP_ALIGN.CENTER

    data = [
        ["Small Benchmark", "9,516", "279.6 MB", "76.03 MB", "27.19%", "622.0 MB/s", "32.2 MB"],
        ["Medium Benchmark", "23,380", "1.09 GB", "303.31 MB", "27.20%", "192.1 MB/s", "33.8 MB"],
        ["Large Benchmark", "58,629", "3.99 GB", "1,098.4 MB", "27.53%", "198.5 MB/s", "42.1 MB"]
    ]
    for row_idx, row_data in enumerate(data):
        for col_idx, val in enumerate(row_data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = BG_CARD
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_WHITE
            p.alignment = PP_ALIGN.CENTER

    add_card(s9, Inches(0.8), Inches(4.2), Inches(5.6), Inches(2.5))
    tb1 = s9.shapes.add_textbox(Inches(1.0), Inches(4.3), Inches(5.2), Inches(2.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Throughput & Linear Scaling"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    insights1 = [
        "Near-constant processing throughput (~192 to 622 MB/s) across scaling dataset volumes.",
        "Tier 1 size filtering and Tier 2 prefix pruning eliminate 80%+ of disk read overhead.",
        "Total runtime scales linearly O(N) rather than quadratic O(N²)."
    ]
    for item in insights1:
        pt = tf1.add_paragraph()
        pt.text = f"• {item}"
        pt.font.size = Pt(11)
        pt.font.color.rgb = COLOR_MUTED
        pt.space_before = Pt(4)

    add_card(s9, Inches(6.8), Inches(4.2), Inches(5.7), Inches(2.5), border_color=COLOR_EMERALD)
    tb2 = s9.shapes.add_textbox(Inches(7.0), Inches(4.3), Inches(5.3), Inches(2.2))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Memory Efficiency & Reclaimed Capacity"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD

    insights2 = [
        "Consistently reclaims ~27.2% of physical storage capacity via atomic hard links.",
        "Peak RSS remains under 45 MB even when indexing ~58,000 files in memory.",
        "Bloom filter bitset requires only 117 KB, fitting completely inside CPU cache."
    ]
    for item in insights2:
        pt = tf2.add_paragraph()
        pt.text = f"• {item}"
        pt.font.size = Pt(11)
        pt.font.color.rgb = COLOR_MUTED
        pt.space_before = Pt(4)

    add_footer(s9, 9)

    # =========================================================================
    # SLIDE 10: TESTING & VERIFICATION SUITE
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, BG_DARK)
    add_header(s10, "Correctness & Invariant Verification")

    tc_groups = [
        ("Unit Testing: Bloom Filter (TC-01, TC-02)", COLOR_CYAN, [
            "TC-01: Zero False Negatives Invariant (10,000 insertions, zero false rejections).",
            "TC-02: Kirsch-Mitzenmacher Double-Hashing bitset uniformity & saturation checks."
        ]),
        ("Unit Testing: Hash Table (TC-03)", COLOR_AMBER, [
            "TC-03: Dynamic rehashing verified at λ > 0.75; average chain length ≤ 1.5; variance ≤ 0.3."
        ]),
        ("Unit Testing: Verifier & Optimizer (TC-04, TC-05)", COLOR_EMERALD, [
            "TC-04: Streaming byte verifier successfully detects 1-bit differences in identical files.",
            "TC-05: Inode cycle detection skips circular symlinks and existing hard links (st_nlink > 1)."
        ]),
        ("Integration Testing: Pipeline & Edge Cases (TC-06 to TC-10)", COLOR_PURPLE, [
            "TC-06: End-to-end dry-run audit verifies duplicate counts without modifying disk files.",
            "TC-07: Live optimization validates physical inode consolidation and block freeing.",
            "TC-08 to TC-10: Handles 0-byte files, broken symlinks, and deeply nested directories."
        ])
    ]

    for i, (title, col, items) in enumerate(tc_groups):
        top = Inches(1.6 + i * 1.3)
        add_card(s10, Inches(0.8), top, Inches(11.7), Inches(1.15), border_color=col)
        tb = s10.shapes.add_textbox(Inches(1.0), top + Inches(0.1), Inches(11.3), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        for item in items:
            pt = tf.add_paragraph()
            pt.text = f"• {item}"
            pt.font.size = Pt(10)
            pt.font.color.rgb = COLOR_WHITE
            pt.space_before = Pt(2)

    add_footer(s10, 10)

    # =========================================================================
    # SLIDE 11: WEB DASHBOARD & TELEMETRY INTERFACE
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, BG_DARK)
    add_header(s11, "Web Dashboard & Telemetry Interface")

    add_card(s11, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s11.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Decoupled Architecture"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    ui_arch = [
        ("Decoupled Design Pattern:", "The web interface runs as an independent Python Flask service communicating with the native C++ binary via JSON reports."),
        ("Target Directory Selector:", "Accepts any custom directory path or one-click preset buttons for standard benchmark tiers (Small, Medium, Large)."),
        ("Dual Operation Modes:", "Provides 'Run Audit (Scan)' for non-destructive inspection and 'Consolidate (Optimize)' for atomic space reclamation."),
        ("Work Directory Reset:", "One-click 'Reset Work Dir' button restores active test folder from ground_truth in seconds for repeatable evaluation.")
    ]
    for title, desc in ui_arch:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_card(s11, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=COLOR_CYAN)
    b = s11.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Visual Analytics & Duplicate Explorer"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    ui_vis = [
        ("Space Breakdown Charts:", "Interactive donut chart for storage volume by file type, and horizontal bar charts for space reclaimed by directory."),
        ("Process Memory Metrics:", "Live display of peak process RAM (RSS) and Bloom filter bitset memory allocation."),
        ("Algorithmic Telemetry Cards:", "Live metrics for Bloom filter bit saturation, queries, and Hash table load factor (λ)."),
        ("Duplicate Equivalence Explorer:", "Searchable table of duplicate clusters detailing canonical files, duplicate replicas, and reclaimed storage.")
    ]
    for title, desc in ui_vis:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = COLOR_MUTED

    add_footer(s11, 11)

    # =========================================================================
    # SLIDE 12: FUTURE WORK & EXTENSIONS
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, BG_DARK)
    add_header(s12, "Future Work & Planned Extensions")

    future_cards = [
        ("1. Sub-File / Chunk Deduplication", "Content-Defined Chunking (CDC)", COLOR_CYAN, [
            "Implement Rabin fingerprinting or FastCDC to divide files into variable-sized chunks.",
            "Enables deduplication across files that share internal sections (e.g., modified documents, incremental log files).",
            "Achieves sub-file granularity where file-level deduplication detects no redundancy."
        ]),
        ("2. Incremental Merkle Trees", "O(log N) Filesystem Synchronization", COLOR_AMBER, [
            "Constructs hierarchical cryptographic hash trees over directory nodes.",
            "Enables sub-linear O(log N) change detection between filesystem snapshots.",
            "Avoids full recursive traversals on evolving storage volumes."
        ]),
        ("3. Parallel Pipeline Execution", "Multi-Threaded Work-Stealing", COLOR_EMERALD, [
            "Parallelizes directory traversal and file reading across multi-core CPU threads.",
            "Hardware-accelerated SHA-256 computation using AVX-512 / ARM Crypto instructions.",
            "Thread-safe concurrent hash table bucket locking."
        ])
    ]

    for i, (title, sub, col, items) in enumerate(future_cards):
        left = Inches(0.8 + i * 4.0)
        add_card(s12, left, Inches(1.6), Inches(3.7), Inches(5.1), border_color=col)
        tb = s12.shapes.add_textbox(left + Inches(0.2), Inches(1.8), Inches(3.3), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_MUTED
        p2.space_before = Pt(4)

        for item in items:
            p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_WHITE
            p.space_before = Pt(12)

    add_footer(s12, 12)

    # =========================================================================
    # SLIDE 13: SUMMARY & CONCLUSION
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, BG_DARK)

    add_card(s13, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), border_color=COLOR_CYAN, bg_color=BG_CARD)
    tb = s13.shapes.add_textbox(Inches(1.5), Inches(1.6), Inches(10.3), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "SUMMARY & CONCLUSION"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_CYAN

    p1 = tf.add_paragraph()
    p1.text = "DedupFS: Core Technical Contributions"
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_before = Pt(8)

    recap_points = [
        "1. Hierarchical I/O Pruning: Size bucketing and prefix hashing eliminate >80% of unnecessary disk reads.",
        "2. Optimal Bloom Filter: Proven FN = 0 invariant with O(k) Kirsch-Mitzenmacher double-hashing using only 117 KB RAM.",
        "3. Chained Hash Table with Dynamic Rehashing: Enforces λ ≤ 0.75 for amortized O(1) lookups across 50,000+ files.",
        "4. Guaranteed Crash-Safe Consolidation: Streaming 64KB byte verifier + atomic POSIX hard-linking (link + rename).",
        "5. Validated on Authentic Corpora: Reclaimed ~27.2% storage capacity with throughput up to 622 MB/s and peak RAM < 45 MB.",
        "6. Comprehensive Test Suite: 10 automated test suites covering edge cases, cycle detection, and memory efficiency.",
        "7. Decoupled Web Dashboard: Provides space breakdown visualizations, memory metrics, and instant work directory reset."
    ]

    for pt_text in recap_points:
        p = tf.add_paragraph()
        p.text = pt_text
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(6)

    p_end = tf.add_paragraph()
    p_end.text = "Thank you! We welcome questions and discussion."
    p_end.font.size = Pt(16)
    p_end.font.bold = True
    p_end.font.color.rgb = COLOR_EMERALD
    p_end.space_before = Pt(14)

    add_footer(s13, 13)

    # Save presentation
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_file))
    print(f"[+] Presentation saved successfully: {output_file.resolve()}")

if __name__ == "__main__":
    build_presentation()
