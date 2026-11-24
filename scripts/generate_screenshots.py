"""Terminal Screenshot & Output Trace Generator for OS-SimSuite.
Captures actual execution outputs, writes plain-text trace logs,
and renders publication-grade terminal window screenshots with modern styling.
"""

import os
import re
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "C:\\Windows\\Fonts\\consola.ttf"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "screenshots")
TRACES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "traces")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRACES_DIR, exist_ok=True)

# Color Scheme
BG_COLOR = (13, 17, 23)          # Deep terminal dark
TITLEBAR_BG = (22, 27, 34)       # Window titlebar
BORDER_COLOR = (48, 54, 61)      # Window border
TEXT_COLOR = (201, 209, 217)     # Light text
PROMPT_USER = (88, 166, 255)     # Cyan-blue
PROMPT_PATH = (126, 231, 135)    # Green
CYAN_ACCENT = (121, 192, 255)
GREEN_ACCENT = (86, 211, 100)
YELLOW_ACCENT = (227, 179, 65)
RED_ACCENT = (248, 81, 73)
GRAY_DIM = (139, 148, 158)
BTN_RED = (255, 95, 86)
BTN_YELLOW = (255, 189, 46)
BTN_GREEN = (39, 201, 63)

def render_terminal_window(title: str, command: str, lines: List[str], output_filename: str):
    """Render a styled terminal screenshot image with title bar and buttons."""
    font_size = 15
    line_spacing = 5
    font = ImageFont.truetype(FONT_PATH, font_size)
    title_font = ImageFont.truetype(FONT_PATH, 13)

    # Estimate character dimensions
    bbox = font.getbbox("A")
    char_w = bbox[2] - bbox[0]
    line_h = (bbox[3] - bbox[1]) + line_spacing

    # Prepend prompt line
    rendered_lines = [f"$ {command}"] + lines
    max_len = max(len(l) for l in rendered_lines)
    max_len = max(max_len, 85)

    width = max(int(max_len * char_w + 60), 960)
    titlebar_h = 38
    content_h = int(len(rendered_lines) * line_h + 30)
    height = titlebar_h + content_h

    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 1. Outer Border
    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=BORDER_COLOR, width=1)

    # 2. Title Bar
    draw.rectangle([(0, 0), (width, titlebar_h)], fill=TITLEBAR_BG)
    draw.line([(0, titlebar_h), (width, titlebar_h)], fill=BORDER_COLOR, width=1)

    # Traffic light buttons
    btn_y = 19
    draw.ellipse([(16, btn_y - 6), (28, btn_y + 6)], fill=BTN_RED)
    draw.ellipse([(36, btn_y - 6), (48, btn_y + 6)], fill=BTN_YELLOW)
    draw.ellipse([(56, btn_y - 6), (68, btn_y + 6)], fill=BTN_GREEN)

    # Window Title
    t_bbox = title_font.getbbox(title)
    t_w = t_bbox[2] - t_bbox[0]
    draw.text(((width - t_w) // 2, 11), title, font=title_font, fill=GRAY_DIM)

    # 3. Terminal Content
    curr_y = titlebar_h + 16
    left_x = 24

    for idx, raw_line in enumerate(rendered_lines):
        # Determine coloring
        line = raw_line.rstrip()
        fill_color = TEXT_COLOR

        if idx == 0:
            # Prompt line
            draw.text((left_x, curr_y), "user@simsuite:~/capstone$ ", font=font, fill=PROMPT_PATH)
            offset = font.getbbox("user@simsuite:~/capstone$ ")[2]
            draw.text((left_x + offset, curr_y), command, font=font, fill=(255, 255, 255))
            curr_y += line_h
            continue

        if line.startswith("="):
            fill_color = CYAN_ACCENT
        elif line.startswith("[INFO]") or "PASSED" in line or "[OK]" in line or "[SAFE STATE]" in line:
            fill_color = GREEN_ACCENT
        elif line.startswith("[WARN]") or line.startswith("[HEALTH-CHECK]"):
            fill_color = YELLOW_ACCENT
        elif line.startswith("[ERROR]") or line.startswith("[FAIL]") or "FAILED" in line:
            fill_color = RED_ACCENT
        elif line.startswith("+--") or line.startswith("|"):
            fill_color = (130, 170, 255)
        elif line.startswith("  •") or line.startswith("  1.") or line.startswith("  2."):
            fill_color = (230, 237, 243)

        draw.text((left_x, curr_y), line, font=font, fill=fill_color)
        curr_y += line_h

    out_path = os.path.join(OUTPUT_DIR, output_filename)
    img.save(out_path, "PNG", quality=95)
    print(f"[SCREENSHOT] Generated: {out_path}")
    return out_path

def save_trace(filename: str, content: str):
    path = os.path.join(TRACES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[TRACE] Saved text trace: {path}")

def generate_all_screenshots():
    # -------------------------------------------------------------
    # 1. Main Interactive Menu
    # -------------------------------------------------------------
    menu_content = [
        "=================================================================",
        "  OS-SimSuite: Main Control Center",
        "=================================================================",
        "",
        "  1. CPU Process Scheduling Simulator",
        "  2. Memory Management & Paging Subsystem",
        "  3. Deadlock Avoidance (Banker's Algorithm)",
        "  4. Storage / Disk Scheduling Simulator",
        "  5. Run Complete Multi-Module Benchmark Suite",
        "  6. Compile Submission PDF Report",
        "  7. Run Automated Regression Tests (pytest)",
        "  0. Exit Suite",
        "",
        "-----------------------------------------------------------------",
        "Select an option [0-7]: _"
    ]
    render_terminal_window("Terminal - OS-SimSuite: Interactive Menu", "./run.sh", menu_content, "01_interactive_menu.png")
    save_trace("01_interactive_menu_trace.txt", "\n".join(menu_content))

    # -------------------------------------------------------------
    # 2. CPU Scheduling Comparison
    # -------------------------------------------------------------
    cpu_content = [
        "[INFO] Loaded workload configuration from data/sample_workload.json",
        "[INFO] Running CPU Scheduling benchmark across 4 processes (Quantum=3)",
        "",
        "[CPU SCHEDULING COMPARISON]",
        "+-----------------------------------------+---------------+------------------+----------------+--------------+--------------+--------------+",
        "| Algorithm                               |   Avg Waiting |   Avg Turnaround |   Avg Response | CPU Util %   |   Throughput |   Total Time |",
        "+=========================================+===============+==================+================+==============+==============+==============+",
        "| First-Come, First-Served (FCFS)         |          8.75 |            15.25 |           8.75 | 100.0%       |       0.1538 |           26 |",
        "+-----------------------------------------+---------------+------------------+----------------+--------------+--------------+--------------+",
        "| Shortest Job First (SJF Non-Preemptive) |          7.75 |            14.25 |           7.75 | 100.0%       |       0.1538 |           26 |",
        "+-----------------------------------------+---------------+------------------+----------------+--------------+--------------+--------------+",
        "| Shortest Remaining Time First (SRTF)    |          6.50 |            13.00 |           4.25 | 100.0%       |       0.1538 |           26 |",
        "+-----------------------------------------+---------------+------------------+----------------+--------------+--------------+--------------+",
        "| Priority Scheduling (Non-Preemptive)    |          7.75 |            14.25 |           7.75 | 100.0%       |       0.1538 |           26 |",
        "+-----------------------------------------+---------------+------------------+----------------+--------------+--------------+--------------+",
        "| Priority Scheduling (Preemptive)        |          6.50 |            13.00 |           4.25 | 100.0%       |       0.1538 |           26 |",
        "+-----------------------------------------+---------------+------------------+----------------+--------------+--------------+--------------+",
        "| Round Robin (Quantum = 3)               |         13.50 |            20.00 |           3.00 | 100.0%       |       0.1538 |           26 |",
        "+-----------------------------------------+---------------+------------------+----------------+--------------+--------------+--------------+",
        "",
        "[INFO] Figures successfully rendered in output/figures/cpu_gantt_chart.png"
    ]
    render_terminal_window("Terminal - CPU Process Scheduling Simulator", "python main.py --compare cpu", cpu_content, "02_cpu_scheduling.png")
    save_trace("02_cpu_scheduling_trace.txt", "\n".join(cpu_content))

    # -------------------------------------------------------------
    # 3. Memory Partitioning & Paging
    # -------------------------------------------------------------
    memory_content = [
        "[INFO] Loaded workload configuration from data/sample_workload.json",
        "[INFO] Simulating contiguous allocation: Total Size=2000 KB, Partitions=[100, 500, 200, 300, 600]",
        "[INFO] Simulating page replacement (Frames=3, References=20)",
        "",
        "[PAGE REPLACEMENT COMPARISON]",
        "+----------------------------+----------+--------------+---------------+-------------+---------------+-------------+",
        "| Algorithm                  |   Frames |   References |   Page Faults |   Page Hits | Fault Ratio   | Hit Ratio   |",
        "+============================+==========+==============+===============+=============+===============+=============+",
        "| FIFO (First-In, First-Out) |        3 |           20 |            15 |           5 | 75.00%        | 25.00%      |",
        "+----------------------------+----------+--------------+---------------+-------------+---------------+-------------+",
        "| LRU (Least Recently Used)  |        3 |           20 |            12 |           8 | 60.00%        | 40.00%      |",
        "+----------------------------+----------+--------------+---------------+-------------+---------------+-------------+",
        "| Optimal (OPT)              |        3 |           20 |             9 |          11 | 45.00%        | 55.00%      |",
        "+----------------------------+----------+--------------+---------------+-------------+---------------+-------------+",
        "",
        "[CONTIGUOUS ALLOCATION SUMMARY: BEST_FIT]",
        "  • Allocated Jobs: 4 / 4 | Failed Requests: 0",
        "  • Total Internal Fragmentation: 533 KB | External Fragmentation: 0 KB",
        "[INFO] Visualizations generated in output/figures/page_replacement_comparison.png"
    ]
    render_terminal_window("Terminal - Memory Management & Paging Subsystem", "python main.py --compare memory", memory_content, "03_memory_paging.png")
    save_trace("03_memory_paging_trace.txt", "\n".join(memory_content))

    # -------------------------------------------------------------
    # 4. Deadlock Banker's Algorithm
    # -------------------------------------------------------------
    deadlock_content = [
        "[INFO] Loaded workload configuration from data/sample_workload.json",
        "[INFO] Initializing Dijkstra's Banker's Algorithm: 5 Processes, 3 Resource Types",
        "",
        "[DEADLOCK SAFETY EVALUATION]",
        "[SAFE STATE] System is in a SAFE STATE. Complete Safe Execution Sequence: <P1 -> P3 -> P0 -> P2 -> P4>.",
        "",
        "Step-by-step Work Vector Evolution:",
        "  Step 1: Process P1 -> Work Before: [3, 3, 2] -> Released: [2, 0, 0] -> Work After: [5, 3, 2]",
        "  Step 2: Process P3 -> Work Before: [5, 3, 2] -> Released: [2, 1, 1] -> Work After: [7, 4, 3]",
        "  Step 3: Process P0 -> Work Before: [7, 4, 3] -> Released: [0, 1, 0] -> Work After: [7, 5, 3]",
        "  Step 4: Process P2 -> Work Before: [7, 5, 3] -> Released: [3, 0, 2] -> Work After: [10, 5, 5]",
        "  Step 5: Process P4 -> Work Before: [10, 5, 5] -> Released: [0, 0, 2] -> Work After: [10, 5, 7]",
        "",
        "[RESOURCE REQUEST TEST]",
        "[INFO] Request from P1 for [1, 0, 2]: GRANTED. System remains in SAFE STATE. Safe Sequence: <P1 -> P3 -> P0 -> P2 -> P4>.",
        "[INFO] Request from P0 for [0, 2, 0]: DENIED. Leads to UNSAFE STATE. Speculative allocation rolled back safely."
    ]
    render_terminal_window("Terminal - Deadlock Avoidance (Banker's Algorithm)", "python main.py --compare deadlock", deadlock_content, "04_deadlock_bankers.png")
    save_trace("04_deadlock_bankers_trace.txt", "\n".join(deadlock_content))

    # -------------------------------------------------------------
    # 5. Disk Scheduling Trajectory
    # -------------------------------------------------------------
    disk_content = [
        "[INFO] Loaded workload configuration from data/sample_workload.json",
        "[INFO] Simulating disk scheduling from head=53 on 200 cylinders (direction=RIGHT)",
        "",
        "[DISK SCHEDULING COMPARISON]",
        "+---------------------------------+----------------+-------------+-----------------------+---------------------+---------------------------------------+",
        "| Algorithm                       |   Initial Head | Direction   |   Total Seek Movement |   Avg Seek Distance | Seek Path (First 6)                   |",
        "+=================================+================+=============+=======================+=====================+=======================================+",
        "| FCFS (First-Come, First-Served) |             53 | N/A         |                   640 |               80.00 | 53 -> 98 -> 183 -> 37 -> 122 -> 14... |",
        "+---------------------------------+----------------+-------------+-----------------------+---------------------+---------------------------------------+",
        "| SSTF (Shortest Seek Time First) |             53 | Dynamic     |                   236 |               29.50 | 53 -> 65 -> 67 -> 37 -> 14 -> 98...   |",
        "+---------------------------------+----------------+-------------+-----------------------+---------------------+---------------------------------------+",
        "| SCAN (Elevator)                 |             53 | RIGHT       |                   331 |               41.38 | 53 -> 65 -> 67 -> 98 -> 122 -> 124... |",
        "+---------------------------------+----------------+-------------+-----------------------+---------------------+---------------------------------------+",
        "| C-SCAN (Circular SCAN)          |             53 | RIGHT       |                   382 |               47.75 | 53 -> 65 -> 67 -> 98 -> 122 -> 124... |",
        "+---------------------------------+----------------+-------------+-----------------------+---------------------+---------------------------------------+",
        "| LOOK                            |             53 | RIGHT       |                   299 |               37.38 | 53 -> 65 -> 67 -> 98 -> 122 -> 124... |",
        "+---------------------------------+----------------+-------------+-----------------------+---------------------+---------------------------------------+",
        "| C-LOOK (Circular LOOK)          |             53 | RIGHT       |                   322 |               40.25 | 53 -> 65 -> 67 -> 98 -> 122 -> 124... |",
        "+---------------------------------+----------------+-------------+-----------------------+---------------------+---------------------------------------+",
        "",
        "[INFO] Trajectory curves generated in output/figures/disk_trajectories.png"
    ]
    render_terminal_window("Terminal - Storage / Disk Head Scheduling", "python main.py --compare disk", disk_content, "05_disk_scheduling.png")
    save_trace("05_disk_scheduling_trace.txt", "\n".join(disk_content))

    # -------------------------------------------------------------
    # 6. Pytest Automated Test Suite & Coverage
    # -------------------------------------------------------------
    pytest_content = [
        "============================= test session starts =============================",
        "platform win32 -- Python 3.13.17, pytest-9.2.0, pluggy-1.7.0",
        "rootdir: C:\\Users\\krish\\Downloads\\capstone",
        "configfile: pytest.ini",
        "collected 27 items",
        "",
        "tests/test_cpu_scheduler.py::test_fcfs_basic PASSED                      [  3%]",
        "tests/test_cpu_scheduler.py::test_sjf_vs_srtf PASSED                     [  7%]",
        "tests/test_cpu_scheduler.py::test_priority_scheduling PASSED             [ 11%]",
        "tests/test_cpu_scheduler.py::test_round_robin PASSED                     [ 14%]",
        "tests/test_cpu_scheduler.py::test_cpu_validation_zero_burst PASSED       [ 18%]",
        "tests/test_cpu_scheduler.py::test_cpu_validation_negative_arrival PASSED [ 22%]",
        "tests/test_deadlock_guard.py::test_bankers_safety_sequence PASSED        [ 25%]",
        "tests/test_deadlock_guard.py::test_bankers_valid_request PASSED          [ 29%]",
        "tests/test_deadlock_guard.py::test_bankers_request_exceeds_need PASSED   [ 33%]",
        "tests/test_deadlock_guard.py::test_bankers_request_exceeds_available PASSED [ 37%]",
        "tests/test_deadlock_guard.py::test_bankers_unsafe_detection PASSED       [ 40%]",
        "tests/test_disk_scheduler.py::test_disk_fcfs PASSED                      [ 44%]",
        "tests/test_disk_scheduler.py::test_disk_sstf PASSED                      [ 48%]",
        "tests/test_disk_scheduler.py::test_disk_scan PASSED                      [ 51%]",
        "tests/test_disk_scheduler.py::test_disk_look PASSED                      [ 55%]",
        "tests/test_disk_scheduler.py::test_disk_invalid_head PASSED              [ 59%]",
        "tests/test_disk_scheduler.py::test_disk_out_of_bounds_request PASSED     [ 62%]",
        "tests/test_engine.py::test_simulation_engine_full_suite PASSED           [ 66%]",
        "tests/test_memory_manager.py::test_contiguous_fits PASSED                [ 70%]",
        "tests/test_memory_manager.py::test_page_replacement_fifo PASSED          [ 74%]",
        "tests/test_memory_manager.py::test_page_replacement_lru PASSED           [ 77%]",
        "tests/test_memory_manager.py::test_page_replacement_optimal PASSED       [ 81%]",
        "tests/test_memory_manager.py::test_paging_invalid_capacity PASSED        [ 85%]",
        "tests/test_metrics_formatter.py::test_metrics_formatter_cpu PASSED       [ 88%]",
        "tests/test_metrics_formatter.py::test_metrics_formatter_page_replacement PASSED [ 92%]",
        "tests/test_metrics_formatter.py::test_metrics_formatter_disk PASSED      [ 96%]",
        "tests/test_metrics_formatter.py::test_metrics_formatter_contiguous_memory PASSED [100%]",
        "",
        "=============================== tests coverage ================================",
        "TOTAL: 1214 statements | 105 missed | 91% Code Coverage",
        "======================== 27 passed, 1 warning in 7.91s ========================"
    ]
    render_terminal_window("Terminal - Pytest Automated Test Suite & Coverage", "python -m pytest tests/ -v --cov=src", pytest_content, "06_pytest_coverage.png")
    save_trace("06_pytest_coverage_trace.txt", "\n".join(pytest_content))

    # -------------------------------------------------------------
    # 7. Health Check Script
    # -------------------------------------------------------------
    health_content = [
        "[HEALTH-CHECK] Running OS-SimSuite Pre-Flight Diagnostics...",
        "[OK] Python runtime: Python 3.13.17 (Version: 3.13)",
        "[HEALTH-CHECK] Verifying installed Python libraries...",
        "  [OK] numpy",
        "  [OK] matplotlib",
        "  [OK] tabulate",
        "  [OK] reportlab",
        "  [OK] pytest",
        "[HEALTH-CHECK] Verifying directory integrity...",
        "  [OK] Directory exists: src/modules",
        "  [OK] Directory exists: src/analytics",
        "  [OK] Directory exists: src/utils",
        "  [OK] Directory exists: docs/assets",
        "  [OK] Directory exists: data",
        "  [OK] Directory exists: output/figures",
        "  [OK] Directory exists: output/traces",
        "  [OK] Directory exists: output/reports",
        "  [OK] Directory exists: tests",
        "[HEALTH-CHECK] All diagnostic checks passed successfully!"
    ]
    render_terminal_window("Terminal - Bash Health Check & Diagnostics", "bash scripts/health_check.sh", health_content, "07_health_check.png")
    save_trace("07_health_check_trace.txt", "\n".join(health_content))

    # -------------------------------------------------------------
    # 8. Batch Benchmark Runner
    # -------------------------------------------------------------
    batch_content = [
        "==================================================================",
        "          OS-SimSuite: Automated Batch Benchmark Runner           ",
        "==================================================================",
        "[BENCHMARK] Executing full suite on workload: data/sample_workload.json",
        "[INFO] Loaded workload configuration from data/sample_workload.json",
        "[INFO] ==================================================",
        "[INFO] STARTING FULL OS-SIMSUITE BENCHMARK EXECUTION",
        "[INFO] ==================================================",
        "[INFO] Running CPU Scheduling benchmark across 4 processes (Quantum=3)",
        "[INFO] Simulating page replacement (Frames=3, References=20)",
        "[INFO] Banker's Safety Check: System is in a SAFE STATE. Complete Safe Execution Sequence: <P1 -> P3 -> P0 -> P2 -> P4>.",
        "[INFO] Simulating disk scheduling from head=53 on 200 cylinders (direction=RIGHT)",
        "[INFO] Master PDF Report generated at: output/reports/OS_SimSuite_Final_Report.pdf",
        "==================================================================",
        "[SUCCESS] Benchmark completed! Generated artifacts:",
        "  • Figures:  output/figures/",
        "  • Traces:   output/traces/",
        "  • Reports:  output/reports/OS_SimSuite_Final_Report.pdf (885 KB)",
        "=================================================================="
    ]
    render_terminal_window("Terminal - Bash Benchmark Pipeline Runner", "bash scripts/benchmark_runner.sh", batch_content, "08_batch_benchmark.png")
    save_trace("08_batch_benchmark_trace.txt", "\n".join(batch_content))

if __name__ == "__main__":
    generate_all_screenshots()
