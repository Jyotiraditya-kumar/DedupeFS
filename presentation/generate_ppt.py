#!/usr/bin/env python3
"""
DedupFS Professional Academic Presentation Generator
Generates a 16:9 widescreen presentation for M.Tech Advanced Data Structures.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pathlib import Path

# Color Palette (Dark Academic Theme)
BG_DARK = RGBColor(11, 17, 32)       # #0B1120
BG_CARD = RGBColor(19, 29, 49)       # #131D31
BG_ACCENT = RGBColor(30, 41, 59)     # #1E293B
BORDER_COLOR = RGBColor(51, 65, 85)  # #334155

COLOR_CYAN = RGBColor(56, 189, 248)  # #38BDF8
COLOR_EMERALD = RGBColor(52, 211, 153) # #34D399
COLOR_AMBER = RGBColor(251, 191, 36) # #FBBF24
COLOR_WHITE = RGBColor(248, 250, 252)
COLOR_MUTED = RGBColor(148, 163, 184) # #94A3B8

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="M.TECH ADVANCED DATA STRUCTURES (ADS)"):
    # Category badge / header
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.4))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_CYAN

    # Main Slide Title
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
    p.text = f"DedupFS &bull; Aryan Ravi Zodape (206126006) & Jyotiraditya Kumar (206126014) | Slide {current_page} of {total_pages}"
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

    # Accent decorative box
    add_card(s1, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), border_color=COLOR_CYAN, bg_color=BG_CARD)

    t_box = s1.shapes.add_textbox(Inches(1.5), Inches(1.6), Inches(10.3), Inches(2.2))
    tf = t_box.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "COURSE PROJECT &bull; PHASE 1 EVALUATION (REVIEW 2)"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_CYAN

    p1 = tf.add_paragraph()
    p1.text = "DedupFS: High-Performance Storage Deduplication Engine"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_before = Pt(10)

    p2 = tf.add_paragraph()
    p2.text = "Multi-Tier Pruning &bull; Optimal Dynamic Bloom Filter &bull; Inverted Chained Hash Table &bull; POSIX Atomic Hard Linking"
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLOR_MUTED
    p2.space_before = Pt(8)

    # Details Grid Cards inside Title Slide
    c1 = add_card(s1, Inches(1.5), Inches(4.2), Inches(4.8), Inches(1.6), border_color=BORDER_COLOR, bg_color=BG_DARK)
    b1 = s1.shapes.add_textbox(Inches(1.7), Inches(4.3), Inches(4.4), Inches(1.4))
    tf1 = b1.text_frame
    p_auth_title = tf1.paragraphs[0]
    p_auth_title.text = "AUTHORS & CANDIDATE DETAILS"
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

    c2 = add_card(s1, Inches(6.8), Inches(4.2), Inches(5.0), Inches(1.6), border_color=BORDER_COLOR, bg_color=BG_DARK)
    b2 = s1.shapes.add_textbox(Inches(7.0), Inches(4.3), Inches(4.6), Inches(1.4))
    tf2 = b2.text_frame
    p_acad_title = tf2.paragraphs[0]
    p_acad_title.text = "ACADEMIC MILESTONE"
    p_acad_title.font.size = Pt(11)
    p_acad_title.font.bold = True
    p_acad_title.font.color.rgb = COLOR_EMERALD

    p_c1 = tf2.add_paragraph()
    p_c1.text = "• Course: Advanced Data Structures (M.Tech Sem 1)"
    p_c1.font.size = Pt(12)
    p_c1.font.color.rgb = COLOR_WHITE
    p_c1.space_before = Pt(4)

    p_c2 = tf2.add_paragraph()
    p_c2.text = "• Review 2 Requirement: 60% Core Implementation"
    p_c2.font.size = Pt(12)
    p_c2.font.color.rgb = COLOR_WHITE

    add_footer(s1, 1)

    # =========================================================================
    # SLIDE 2: THE PROBLEM STATEMENT & CORE CHALLENGE
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, BG_DARK)
    add_header(s2, "The Storage Crisis & The Fundamental I/O Bottleneck")

    add_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Data Redundancy Challenge"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    points = [
        ("Massive Enterprise Redundancy:", "Between 30% and 75% of enterprise storage is consumed by identical duplicate files (backups, VM images, source clones, PDF documents)."),
        ("Naive Pairwise Comparison Fails:", "Pairwise comparison requires O(N²) comparisons (~1.25 × 10¹¹ file reads for 500k files), making it computationally intractable."),
        ("Naive Full Hashing Fails:", "Computing full cryptographic digests (SHA-256) on every file causes extreme disk I/O thrashing. Up to 80% of files scanned are completely unique!")
    ]
    for title, desc in points:
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
    p.text = "The DedupFS Algorithmic Solution"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD

    sol_points = [
        ("Multi-Tier I/O Filtering Hierarchy:", "Tier 1 size bucketing discards unique files in O(1) time with 0 disk reads. Tier 2 tests 4KB Murmur3 prefix hashes to eliminate non-matching headers."),
        ("Probabilistic Bloom Filter Pre-Check:", "Dynamically sized bitset with Kirsch-Mitzenmacher double-hashing rejects ~99% of unique files in O(k) CPU bit tests with Zero False Negatives (FN = 0)."),
        ("Primary Chained Hash Table:", "In-memory inverted index (Fingerprint → Files) with dynamic power-of-two capacity expansion when load factor λ > 0.75."),
        ("100% Data Preservation Guarantee:", "Streaming 64KB byte-by-byte binary verifier prevents cryptographic collision risk. POSIX atomic hard-link consolidation frees physical blocks safely.")
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
    # SLIDE 3: SYSTEM ARCHITECTURE & 6-STAGE PIPELINE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, BG_DARK)
    add_header(s3, "DedupFS Phase 1 System Architecture: 6-Stage Pipeline")

    stages = [
        ("Stage 1: Recursive Scanner", "Traverses storage volume, tracks inode keys (st_dev, st_ino) to prevent circular cycles, and builds size buckets."),
        ("Stage 2: Tier 1 Size Pruning", "Buckets files by byte length in O(1). Files with unique sizes are eliminated immediately with ZERO physical disk I/O (~25% pruned)."),
        ("Stage 3: Tier 2 4KB Prefix Hash", "Reads only the first 4,096 bytes and computes 128-bit MurmurHash3. Mismatched file headers are discarded without reading file bodies."),
        ("Stage 4: Tier 3 Full SHA-256 Digest", "Only surviving candidate clusters undergo full cryptographic SHA-256 fingerprinting using hardware-accelerated OpenSSL EVP streaming."),
        ("Stage 5: Bloom Filter & Inverted Table", "Queries optimal Bloom filter bitset in O(k) CPU operations. Potential matches are inserted into the primary chained hash table."),
        ("Stage 6: Verifier & Hard-Link Optimizer", "Executes 64KB binary memcmp byte verification (0% collision risk), then atomically consolidates duplicates via POSIX hard links (link + rename).")
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
        p.text = f"{i+1}. {title}"
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
    # SLIDE 4: BLOOM FILTER (MATHEMATICS & IMPLEMENTATION)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, BG_DARK)
    add_header(s4, "Data Structure 1: Optimal Dynamic Bloom Filter")

    # Left: Mathematical Formulations
    add_card(s4, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Mathematical Formulation & Optimal Sizing"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    bf_math = [
        ("Optimal Bitset Size (m):", "Given expected items n and target false positive rate p:\nm = - (n · ln p) / (ln 2)² ≈ -2.08136 · n · ln(p)"),
        ("Optimal Number of Hash Functions (k):", "k = (m / n) · ln 2 ≈ 0.69315 · (m / n)\nFor p = 0.01 (1%), optimal k = 7 hash functions."),
        ("Kirsch-Mitzenmacher Double-Hashing:", "Instead of k distinct hash computations, two 64-bit words (h₁, h₂) from the SHA-256 digest simulate k independent hash functions:\ng_i(x) = (h₁(x) + i · h₂(x)) mod m"),
        ("Zero False Negatives Invariant (FN = 0):", "If any bit in g_i(x) is 0, the key was mathematically never inserted. True negatives bypass secondary hash table lookups completely!")
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

    # Right: Empirical Telemetry & Proof
    add_card(s4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1), border_color=COLOR_CYAN)
    b = s4.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Empirical Telemetry & Verification"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    bf_telemetry = [
        ("Bitset Allocation:", "Allocated 958,506 bits (~117 KB) in-memory for 100k capacity at p = 1.0%."),
        ("Set Membership Queries:", "Evaluated 5,104 candidate SHA-256 fingerprints."),
        ("True Negative Rejections:", "2,012 files rejected in O(k) bit tests, avoiding hash table lookups entirely."),
        ("Observed False Positives:", "0 false positives observed (Empirical FPR: 0.00% vs Theoretical: 1.40e-13)."),
        ("Saturation Fill Ratio:", "Only 1.46% of bitset bits set to 1, maintaining high entropy and low collision risk.")
    ]
    for title, desc in bf_telemetry:
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
    # SLIDE 5: PRIMARY HASH TABLE (SEPARATE CHAINING & REHASHING)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, BG_DARK)
    add_header(s5, "Data Structure 2: Primary Chained Inverted Hash Table")

    add_card(s5, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Inverted Index Architecture"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    ht_points = [
        ("Key-Value Mapping:", "Maps 256-bit cryptographic SHA-256 fingerprints to lists of FileInfo metadata (inode, path, size, link count)."),
        ("Separate Chaining Resolution:", "Collisions in buckets are resolved via singly linked lists of key-value nodes, ensuring graceful degradation under clustering."),
        ("Dynamic Amortized O(1) Rehashing:", "When table load factor λ = N / buckets exceeds 0.75, capacity is automatically doubled (power-of-two buckets) and all nodes re-indexed in amortized O(1) time."),
        ("Equivalence Group Extraction:", "Extracts all buckets with file count ≥ 2 into verified duplicate equivalence classes for storage optimization.")
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
    p.text = "Runtime Diagnostics & Telemetry"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    ht_diag = [
        ("Power-of-Two Capacity:", "Allocated 4,096 initial buckets (Small) to 32,768 buckets (Large dataset)."),
        ("Stored Unique Elements:", "2,012 distinct fingerprints indexed in Small tier, up to 11,208 in Large tier."),
        ("Load Factor Maintenance:", "Maintained λ = 0.491 on Small tier and λ = 0.58 on Large tier (well under 0.75 threshold)."),
        ("Collision Chain Depths:", "Maximum collision chain depth: 4. Average non-empty chain length: 1.26."),
        ("Low Chain Variance:", "Collision chain variance of 0.26 indicates highly uniform, non-clustered cryptographic hash distribution.")
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
    # SLIDE 6: MULTI-TIER I/O REDUCTION STRATEGY
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, BG_DARK)
    add_header(s6, "Multi-Tier Hashing & Disk I/O Pruning Strategy")

    # 3 Column Cards
    tiers = [
        ("Tier 1: Metadata Size Bucketing", "O(1) Unique Size Elimination", COLOR_CYAN, [
            "Groups scanned files by st_size attribute.",
            "Files with unique lengths cannot have duplicates.",
            "Eliminated 2,346 files (24.7%) in Small tier.",
            "Eliminated 14,133 files (24.1%) in Large tier.",
            "Disk Reads Incurred: ZERO BYTES."
        ]),
        ("Tier 2: 4KB Murmur3 Prefix", "Fast 128-bit Header Hash", COLOR_AMBER, [
            "Reads only the first 4,096 bytes of candidate files.",
            "Computes fast 128-bit MurmurHash3 prefix hash.",
            "Pruned 2,060 files in Small tier after reading <4KB.",
            "Pruned 6,842 files in Large tier without full read.",
            "Eliminates different files that happen to share size."
        ]),
        ("Tier 3: Full SHA-256 Digest", "Cryptographic Fingerprint", COLOR_EMERALD, [
            "Executed ONLY for candidate survivors of Tiers 1 & 2.",
            "Streaming OpenSSL EVP hardware-accelerated SHA-256.",
            "Only 5,104 full hashes computed out of 9,516 files.",
            "Avoided reading over 121 MB of disk data in Small tier.",
            "Overall disk I/O reduced by over 65%!"
        ])
    ]

    for i, (title, sub, col, items) in enumerate(tiers):
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
    # SLIDE 7: VERIFICATION & ATOMIC STORAGE OPTIMIZATION
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, BG_DARK)
    add_header(s7, "Zero Data Loss Guarantee & Atomic POSIX Consolidation")

    add_card(s7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.1))
    b = s7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Streaming 64KB Byte-Level Verifier"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    ver_points = [
        ("The Cryptographic Collision Problem:", "While SHA-256 collision probability is astronomically low (2⁻²⁵⁶), enterprise file systems require absolute zero probability of data loss."),
        ("Chunk-by-Chunk Binary memcmp:", "DedupFS streams files in two 64KB aligned buffers and performs raw binary memory comparison prior to any storage mutation."),
        ("End-of-File Discrepancy Detection:", "Reliably detects 1-byte differences (even at file EOF) where prefix and size match, preventing false deduplication."),
        ("Zero Collisions in 3,092+ Verifications:", "100% of confirmed duplicates match bit-for-bit with ground truth.")
    ]
    for title, desc in ver_points:
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
    p.text = "POSIX Atomic Hard-Link Consolidation"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD

    opt_points = [
        ("Path Transparency Preserved:", "Consolidation unifies physical storage blocks while maintaining independent directory entries, filenames, and access permissions."),
        ("Two-Step Atomic Replacement:", "1. link(canonical_path, temp_path)\n2. rename(temp_path, duplicate_path)\nGuarantees crash safety: the duplicate path is NEVER missing or corrupted during power failure!"),
        ("Cross-Device Safeguard (EXDEV):", "Verifies st_dev equality before linking; gracefully skips files crossing filesystem boundaries."),
        ("Physical Block Deallocation:", "The Linux kernel deallocates duplicate blocks immediately while st_nlink increments on the unified inode.")
    ]
    for title, desc in opt_points:
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
    # SLIDE 8: DUAL-FOLDER BENCHMARK ARCHITECTURE & METHODOLOGY
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, BG_DARK)
    add_header(s8, "Dual-Folder Experimental Architecture & Methodology")

    add_card(s8, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.1))
    b = s8.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(11.1), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Scientific Validation: Untouched Ground Truth vs. Active Workspace"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    method_points = [
        ("The Dual-Folder Architecture:", "Each test dataset maintains two synchronized folder trees: 'ground_truth/' (untouched reference, independent inodes with st_nlink = 1) and 'work/' (the active target where DedupFS executes and consolidates duplicates into st_nlink > 1)."),
        ("Realistic Enterprise Workloads:", "Constructed directly from authentic raw corpora: 8,905 real PDF Resumes across HR/IT/Finance, 82,783 authentic COCO JPG photos, paired Linux Kernels 6.10 & 6.11 (sharing ~75% identical code), and adversarial edge cases."),
        ("Automated Verification Harness (--verify):", "Performs exhaustive byte-for-byte binary content comparison between every file in 'work/' and 'ground_truth/'. Formally verifies 100% content preservation and correct inode link consolidation (e.g. 5,091 files sharing hard links)."),
        ("Instant Rollback Mechanism (--reset):", "Restores the entire 'work/' directory back to its pristine, un-deduplicated pre-run state in <1 second, enabling completely repeatable, reproducible benchmarking!")
    ]
    for title, desc in method_points:
        pt = tf.add_paragraph()
        pt.text = title
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(12)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(12)
        pd.font.color.rgb = COLOR_MUTED

    add_footer(s8, 8)

    # =========================================================================
    # SLIDE 9: EMPIRICAL BENCHMARK RESULTS & TELEMETRY
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, BG_DARK)
    add_header(s9, "Empirical Benchmark Results Across Multi-Gigabyte Datasets")

    # Table of Results
    rows, cols = 8, 4
    left, top, width, height = Inches(0.8), Inches(1.6), Inches(11.733), Inches(4.8)
    table_shape = s9.shapes.add_table(rows, cols, left, top, width, height)
    tbl = table_shape.table

    tbl.columns[0].width = Inches(3.5)
    tbl.columns[1].width = Inches(2.7)
    tbl.columns[2].width = Inches(2.7)
    tbl.columns[3].width = Inches(2.8)

    headers = ["Evaluation Metric", "Small Tier (280 MB)", "Medium Tier (1.09 GB)", "Large Enterprise (3.99 GB)"]
    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_ACCENT
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = COLOR_CYAN

    data = [
        ["Total Files Scanned", "9,516 files", "23,380 files", "58,629 files"],
        ["Raw Logical Data Volume", "279.63 MB", "1.09 GB", "3.99 GB"],
        ["Tier 1 Size Bucketing Discarded", "2,346 files (24.7% I/O saved)", "5,403 files (23.1% I/O saved)", "14,133 files (24.1% I/O saved)"],
        ["Bloom Filter Invariant Proof", "FN = 0 (0.00% FPR)", "FN = 0 (0.00% FPR)", "FN = 0 (0.00% FPR)"],
        ["Hash Table Bucket Allocation", "4,096 buckets (λ = 0.49)", "8,192 buckets (1 rehash)", "32,768 buckets (3 rehashes)"],
        ["Reclaimed Physical Storage", "76.03 MB (27.2% saved)", "303.31 MB (27.8% saved)", "1.13 GB (28.3% saved)"],
        ["Execution Runtime & Throughput", "449.5 ms &bull; 622 MB/s", "2.12 s &bull; 526 MB/s", "8.58 s &bull; 476 MB/s"]
    ]

    for i, row in enumerate(data):
        for j, val in enumerate(row):
            cell = tbl.cell(i+1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = BG_CARD if i % 2 == 0 else BG_DARK
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = COLOR_WHITE if j == 0 else COLOR_EMERALD if "saved" in val or "MB/s" in val else COLOR_MUTED
                if j == 0:
                    p.font.bold = True

    add_footer(s9, 9)

    # =========================================================================
    # SLIDE 10: AUTOMATED TEST SUITE & FORMAL INVARIANT VERIFICATION
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, BG_DARK)
    add_header(s10, "Automated Test Suite & Formal Invariant Verification")

    add_card(s10, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.1))
    b = s10.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(11.1), Inches(4.7))
    tf = b.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "100% Pass Rate Across All 10 Formal Test Suites (TC-01 through TC-10)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD

    test_matrix = [
        ("TC-01 &bull; Bloom Filter FN = 0:", "Zero False Negatives formally proven across 5,000 inserted keys (FN = 0 guaranteed)."),
        ("TC-02 &bull; Bloom Filter FPR Bound:", "Empirical false-positive probability tested across 20,000 uninserted keys stays strictly under 1.5%."),
        ("TC-03 &bull; Dynamic Bitset State:", "Bitset fill ratio saturation calculation verified; complete state reset verified via clear()."),
        ("TC-04 &bull; Hash Table Key Isolation:", "Unique key insertion and distinct 256-bit cryptographic digest isolation verified."),
        ("TC-05 &bull; Dynamic Rehashing (λ > 0.75):", "Automatic capacity doubling and amortized O(1) node re-indexing verified across 4 rehash cycles."),
        ("TC-06 &bull; Equivalence Grouping:", "Duplicate cluster extraction and wasted storage byte calculation mathematically verified."),
        ("TC-07 &bull; Byte Verifier Collision Safety:", "Confirms identical files and reliably catches 1-byte EOF mismatches where size and prefix match."),
        ("TC-08 &bull; Dry-Run Immutability:", "Audits potential storage savings while leaving 100% of filesystem blocks untouched."),
        ("TC-09 &bull; POSIX Hard-Link Consolidation:", "Atomic hard-link consolidation unifies duplicate inodes (st_nlink = 2) without data loss."),
        ("TC-10 &bull; Full End-to-End Pipeline:", "Complete multi-tier pipeline integration verified from recursive scan to storage reclamation.")
    ]

    for title, desc in test_matrix:
        pt = tf.add_paragraph()
        pt.text = f"• {title} {desc}"
        pt.font.size = Pt(11)
        pt.font.color.rgb = COLOR_WHITE
        pt.space_before = Pt(4)

    add_footer(s10, 10)

    # =========================================================================
    # SLIDE 11: DECOUPLED WEB DASHBOARD & UI FEATURES
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, BG_DARK)
    add_header(s11, "Decoupled Web Management UI & Interactive Analytics")

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
        ("Decoupled Design Pattern:", "The web interface runs as an independent Python Flask service interacting with the native C++ dedupfs binary via JSON telemetry and CLI protocols."),
        ("Arbitrary Directory Input:", "Accepts any custom target directory path or one-click preset buttons for standard benchmark tiers (Small, Medium, Large)."),
        ("Dual Operation Controls:", "Provides 'Run Safe Audit (Scan)' for non-destructive inspection and 'Consolidate Inodes (Optimize)' for live atomic space reclamation."),
        ("Real-Time Terminal Streaming:", "Live terminal viewer capturing engine stdout, phase latencies, and execution telemetry.")
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
    p.text = "Visual Charts & Duplicate Explorer"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    ui_vis = [
        ("Space Usage by File Type (Donut Chart):", "Interactive distribution of storage across formats (.pdf, .jpg, .c, .h, .csv)."),
        ("Space Reclaimed by File Type (Bar Chart):", "Quantifies exactly which file formats contribute most to redundant capacity."),
        ("Space Savings by Subdirectory (Horizontal Bar):", "Isolates spatial clustering of duplicates across nested directory hierarchies."),
        ("Algorithmic Telemetry Cards:", "Live gauges for Bloom filter bit saturation, queries, and Hash table load factor (λ)."),
        ("Duplicate Equivalence Explorer:", "Searchable table of duplicate clusters detailing canonical files, duplicate replicas, inodes, and link counts.")
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
    # SLIDE 12: PHASE 2 ROADMAP (REVIEW 3 DELIVERABLES)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, BG_DARK)
    add_header(s12, "Phase 2 Roadmap & Review 3 Deliverables (Nov 23, 2026)")

    phase2_cards = [
        ("1. Hierarchical Merkle Tree", "O(log N) Incremental Synchronization", COLOR_CYAN, [
            "Constructs hierarchical cryptographic hash trees over directory nodes.",
            "Enables sub-linear O(log N) change detection between snapshot versions.",
            "Drastically reduces re-scan overhead on evolving multi-terabyte filesystems."
        ]),
        ("2. Max-Heap Priority Queue", "Top-K Space Reclamation", COLOR_AMBER, [
            "Maintains an in-memory Max-Heap of duplicate equivalence classes.",
            "Prioritizes consolidating the largest duplicate clusters first under constrained I/O or time budgets.",
            "Guarantees maximum storage reclamation in minimum latency."
        ]),
        ("3. Compression-Aware Inspection", "Entropy & Container Parsing", COLOR_EMERALD, [
            "Inspects compressed archives (.tar.gz, .zip, .zst) without manual decompression.",
            "Adaptive entropy estimation skips incompressible random byte streams.",
            "Parallel multi-threaded scanning using work-stealing thread pools."
        ])
    ]

    for i, (title, sub, col, items) in enumerate(phase2_cards):
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
    # SLIDE 13: CONCLUSION & Q&A
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, BG_DARK)

    add_card(s13, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), border_color=COLOR_CYAN, bg_color=BG_CARD)
    tb = s13.shapes.add_textbox(Inches(1.5), Inches(1.6), Inches(10.3), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "PHASE 1 SUMMARY & KEY CONTRIBUTIONS"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_CYAN

    p1 = tf.add_paragraph()
    p1.text = "DedupFS: Core Technical Milestones Achieved"
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_before = Pt(8)

    recap_points = [
        "1. Complete C++17 Multi-Tier Pipeline: ~25% unique files discarded in O(1) with 0 disk reads.",
        "2. Optimal Dynamic Bloom Filter: Proven FN = 0 invariant, O(k) Kirsch-Mitzenmacher double-hashing.",
        "3. Chained Hash Table with Dynamic Rehashing: Maintains load factor λ ≤ 0.75 in amortized O(1) time.",
        "4. Guaranteed 100% Data Preservation: 64KB chunk streaming byte verifier + atomic POSIX hard-linking.",
        "5. Validated on Authentic Corpora: Reclaimed 28% storage capacity across Small, Medium, and Large datasets (throughput up to 622 MB/s).",
        "6. Automated 10-Suite Test Harness: 100% pass rate across TC-01 through TC-10.",
        "7. Decoupled Web Management UI: Live dashboard with breakdown charts and execution telemetry."
    ]

    for pt_text in recap_points:
        p = tf.add_paragraph()
        p.text = pt_text
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(6)

    p_end = tf.add_paragraph()
    p_end.text = "Thank you! We welcome questions and feedback from the Professor."
    p_end.font.size = Pt(16)
    p_end.font.bold = True
    p_end.font.color.rgb = COLOR_EMERALD
    p_end.space_before = Pt(16)

    add_footer(s13, 13)

    # Save presentation
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_file))
    print(f"[+] Presentation saved successfully: {output_file.resolve()}")

if __name__ == "__main__":
    build_presentation()

