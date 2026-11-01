#!/usr/bin/env python3
"""
DedupFS Decoupled Web Management UI & Telemetry Dashboard
Flask backend interacting with the native C++ dedupfs binary.
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BINARY_PATH = PROJECT_ROOT / "bin" / "dedupfs"
REPORTS_DIR = PROJECT_ROOT / "reports"

PRESETS = {
    "small": {
        "label": "Small Benchmark (~280 MB)",
        "path": str(PROJECT_ROOT / "datasets" / "test_small_250MB" / "work"),
        "desc": "Resumes PDF, COCO Photos, curl release code, nested archives (9,516 files)"
    },
    "medium": {
        "label": "Medium Benchmark (~1.09 GB)",
        "path": str(PROJECT_ROOT / "datasets" / "test_medium_1GB" / "work"),
        "desc": "Resumes PDF, COCO Photos, Linux kernel core, nested archives (23,380 files)"
    },
    "large": {
        "label": "Large Enterprise Benchmark (~3.99 GB)",
        "path": str(PROJECT_ROOT / "datasets" / "test_large_3.5GB" / "work"),
        "desc": "Dual Linux 6.10 & 6.11 trees, COCO Photos, Resumes PDF (58,629 files)"
    }
}

def parse_duplicate_clusters(max_clusters=50):
    """Parses reports/duplicates_latest.txt into structured JSON."""
    dup_file = REPORTS_DIR / "duplicates_latest.txt"
    if not dup_file.exists():
        return []

    clusters = []
    current_cluster = None

    try:
        with open(dup_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line.startswith("DUPLICATE GROUP #"):
                    if current_cluster:
                        clusters.append(current_cluster)
                        if len(clusters) >= max_clusters:
                            break
                    current_cluster = {
                        "group_id": line.split("#")[-1].strip(),
                        "sha256": "",
                        "prefix_murmur3": "",
                        "file_size": "",
                        "cardinality": "",
                        "wasted_storage": "",
                        "original": "",
                        "duplicates": []
                    }
                elif not current_cluster:
                    continue
                elif line.startswith("SHA-256 Fingerprint:"):
                    current_cluster["sha256"] = line.split(":", 1)[1].strip()
                elif line.startswith("4KB Prefix Murmur3:"):
                    current_cluster["prefix_murmur3"] = line.split(":", 1)[1].strip()
                elif line.startswith("File Size:"):
                    current_cluster["file_size"] = line.split(":", 1)[1].strip()
                elif line.startswith("Cluster Cardinality:"):
                    current_cluster["cardinality"] = line.split(":", 1)[1].strip()
                elif line.startswith("Wasted Storage:"):
                    current_cluster["wasted_storage"] = line.split(":", 1)[1].strip()
                elif line.startswith("[ORIGINAL]"):
                    current_cluster["original"] = line.replace("[ORIGINAL]", "").strip()
                elif line.startswith("[DUP #"):
                    current_cluster["duplicates"].append(re.sub(r"^\[DUP #\d+\]", "", line).strip())

            if current_cluster and len(clusters) < max_clusters:
                clusters.append(current_cluster)
    except Exception as e:
        print(f"Error parsing duplicates: {e}")

    return clusters

def run_dedupfs_binary(command_type, target_dir, min_size=1, fpr=0.01):
    """Executes ./bin/dedupfs scan|optimize <target_dir> and captures output."""
    if not BINARY_PATH.exists():
        return {
            "success": False,
            "error": f"Binary not found at {BINARY_PATH}. Please compile via 'make all' first."
        }

    cmd = [
        str(BINARY_PATH),
        command_type,
        str(target_dir),
        "--min-size", str(min_size),
        "--fpr", str(fpr)
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=180
        )
        output = proc.stdout

        # Read JSON report
        json_file = REPORTS_DIR / "report_latest.json"
        metrics_data = {}
        if json_file.exists():
            with open(json_file, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)

        return {
            "success": (proc.returncode == 0),
            "returncode": proc.returncode,
            "output": output,
            "metrics": metrics_data,
            "command": " ".join(cmd)
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "DedupFS operation timed out after 180 seconds."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route("/")
def index():
    return render_template("index.html", presets=PRESETS)

@app.route("/api/presets", methods=["GET"])
def get_presets():
    return jsonify(PRESETS)

@app.route("/api/metrics", methods=["GET"])
def get_latest_metrics():
    json_file = REPORTS_DIR / "report_latest.json"
    if json_file.exists():
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify({"success": True, "metrics": data})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    return jsonify({"success": False, "error": "No metrics report generated yet."})

@app.route("/api/duplicates", methods=["GET"])
def get_duplicates():
    limit = request.args.get("limit", default=50, type=int)
    clusters = parse_duplicate_clusters(max_clusters=limit)
    return jsonify({"success": True, "clusters": clusters})

@app.route("/api/scan", methods=["POST"])
def scan_directory():
    data = request.json or {}
    path = data.get("path", "").strip()
    min_size = data.get("min_size", 1)
    fpr = data.get("fpr", 0.01)

    if not path:
        return jsonify({"success": False, "error": "Path cannot be empty."}), 400

    result = run_dedupfs_binary("scan", path, min_size, fpr)
    return jsonify(result)

@app.route("/api/optimize", methods=["POST"])
def optimize_directory():
    data = request.json or {}
    path = data.get("path", "").strip()
    min_size = data.get("min_size", 1)
    fpr = data.get("fpr", 0.01)

    if not path:
        return jsonify({"success": False, "error": "Path cannot be empty."}), 400

    result = run_dedupfs_binary("optimize", path, min_size, fpr)
    return jsonify(result)

@app.route("/api/report/html", methods=["GET"])
def get_html_report():
    html_file = REPORTS_DIR / "report_latest.html"
    if html_file.exists():
        return send_file(html_file)
    return "HTML report not generated yet.", 404

@app.route("/presentation")
def get_presentation_slides():
    slides_file = PROJECT_ROOT / "presentation" / "index.html"
    if slides_file.exists():
        return send_file(slides_file)
    return "Presentation slides not found.", 404

@app.route("/presentation/download")
def download_presentation_pptx():
    pptx_file = PROJECT_ROOT / "presentation" / "DedupFS_MTech_Presentation.pptx"
    if pptx_file.exists():
        return send_file(pptx_file, as_attachment=True, download_name="DedupFS_MTech_Presentation.pptx")
    return "Presentation PPTX not found.", 404

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    print(f"\n=======================================================")
    print(f"  DedupFS Web Telemetry Dashboard Started!")
    print(f"  Access UI at: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
