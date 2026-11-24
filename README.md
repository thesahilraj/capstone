# Capstone: Integrated Operating System Resource-Management Simulator & Analytics Engine

**Candidate Name:** Sahil Raj  
**Roll Number:** 2401410004  
**Course / Project:** Operating Systems Capstone Project  

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/krishnakrsingh/capstone)
[![Tests Passing](https://img.shields.io/badge/tests-27%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)](tests/)
[![PDF Submission](https://img.shields.io/badge/PDF%20Report-1.4MB%20(Under%2025MB)-blue.svg)](output/reports/Sahil_Raj_2401410004_Capstone_Report.pdf)

> An integrated Python-and-Bash application that simulates major operating-system resource-management functions (CPU scheduling, memory management, deadlock avoidance, storage scheduling) and produces rigorous analytical results, visualizations, and comparative reports.

---

## System Architecture

![System Architecture Topology](docs/assets/architecture_animated.gif)

<details>
<summary><b>View Text-Based Layer Schematic</b></summary>

```
                      +-----------------------------------+
                      |      Presentation & Automation    |
                      |  • run.sh (Bash Orchestrator)     |
                      |  • run.ps1 (PowerShell Companion) |
                      |  • Interactive Terminal UI Menu   |
                      |  • Headless Batch CLI Parser      |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------------------------+
                      |   Simulation Engine Controller    |
                      |  • Input Validation & Schemas     |
                      |  • Structured Telemetry Logger    |
                      |  • Lifecycle Dispatcher           |
                      +-----------------+-----------------+
                                        |
       +------------------+-------------+-------------+------------------+
       |                  |                           |                  |
       v                  v                           v                  v
+--------------+  +---------------+           +---------------+  +---------------+
| 1. CPU       |  | 2. Memory     |           | 3. Deadlock   |  | 4. Storage    |
| Scheduler    |  | Manager       |           | Guard         |  | Scheduler     |
| • FCFS       |  | • First/Best/ |           | • Banker's    |  | • FCFS        |
| • SJF/SRTF   |  |   Worst Fit   |           |   Safety Algo |  | • SSTF        |
| • Priority   |  | • Page Repl.  |           | • Resource    |  | • SCAN/C-SCAN |
| • RoundRobin |  |   FIFO/LRU/OPT|           |   Request Algo|  | • LOOK/C-LOOK |
+-------+------+  +-------+-------+           +-------+-------+  +-------+-------+
        |                 |                           |                  |
        +-----------------+-------------+-------------+------------------+
                                        |
                                        v
                      +-----------------------------------+
                      |    Analysis & Reporting Engine    |
                      |  • Comparative Analytics Tables   |
                      |  • Visualizer (Matplotlib Charts) |
                      |  • PDF & Markdown Report Builder  |
                      +-----------------+-----------------+
```

</details>

---

## Subsystems & Project Deliverables

| Phase | Meaningful Title | Core Subsystems & Deliverables | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **System Design and Planning** | Problem formulation, modular architecture, data design, and implementation plan. | **Completed** |
| **Phase 2** | **Core Resource-Management Modules** | Implementation of CPU, Memory, Deadlock, and Disk subsystems with interactive menu flow and Bash integration. | **Completed** |
| **Phase 3** | **Analysis and Comparison** | Common workload benchmarking, comparative analysis tables, and labelled Matplotlib visualizations. | **Completed** |
| **Phase 4** | **Testing and Reliability** | Valid/invalid/boundary input testing, structured exception handling, and activity logging (92% coverage). | **Completed** |
| **Phase 5** | **Documentation and Demonstration** | Execution steps, output traces, screenshots, concise final report (PDF), and demonstration package. | **Completed** |

---

## Directory Structure

```
capstone/
├── README.md                      # Primary project documentation & execution guide
├── INSTRUCTIONS.md                # Official Capstone rubric & assignment requirements
├── requirements.txt               # Python package dependencies
├── run.sh                         # Bash entry point and orchestrator
├── run.ps1                        # PowerShell entry point for Windows
├── main.py                        # Python main application entry point
├── pytest.ini                     # Pytest configuration
├── docs/                          # Structured project documentation
│   ├── INSTRUCTIONS.md            # Preserved assignment instructions
│   ├── assets/                    # Portal reference images & visual diagrams
│   ├── screenshots/               # Terminal execution screenshots (01..08)
│   └── phases/                    # Individual phase milestone reports
│       ├── PHASE_1_SYSTEM_DESIGN.md
│       ├── PHASE_2_IMPLEMENTATION.md
│       ├── PHASE_3_ANALYSIS.md
│       ├── PHASE_4_TESTING.md
│       └── PHASE_5_FINAL_REPORT.md
├── data/                          # Standardized test & benchmark workloads (JSON)
│   ├── sample_workload.json
│   ├── sample_cpu.json
│   ├── sample_memory.json
│   ├── sample_deadlock.json
│   └── sample_disk.json
├── src/                           # Core application source code
│   ├── engine.py                  # Simulation Controller
│   ├── cli/menu.py                # Interactive ANSI terminal menu
│   ├── modules/                   # Operating System resource management modules
│   │   ├── cpu_scheduler.py       # FCFS, SJF, SRTF, Priority, Round Robin
│   │   ├── memory_manager.py      # Dynamic allocation & FIFO/LRU/OPT paging
│   │   ├── deadlock_guard.py      # Dijkstra's Banker's algorithm
│   │   └── disk_scheduler.py      # FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK
│   ├── analytics/                 # Analysis and visualization engine
│   │   ├── metrics.py             # Performance metric calculators & table formatter
│   │   ├── visualizer.py          # Gantt, trajectory & histogram plots
│   │   └── report_generator.py    # ReportLab automated PDF report generator
│   └── utils/                     # Exceptions, logging, and input validators
├── scripts/                       # Shell automation and diagnostic scripts
│   ├── benchmark_runner.sh        # Runs comparative suite across all modules
│   ├── health_check.sh            # Validates dependencies and environment
│   ├── generate_report.sh         # PDF report compilation trigger
│   └── generate_screenshots.py    # Terminal screenshot generator
├── tests/                         # Pytest automated test suite (27 tests, 92% coverage)
└── output/                        # Generated output traces, charts, and reports
    ├── figures/                   # High-resolution PNG visual plots
    ├── reports/                   # Submission PDF (Capstone_Final_Report.pdf)
    ├── tables/                    # Formatted text & CSV metrics
    └── traces/                    # Serialized execution logs & traces
```

---

## Quickstart & Execution Steps

### 1. Requirements & Setup
- Python 3.10 or higher
- Bash (or Git Bash / WSL on Windows; or PowerShell via `run.ps1`)

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Interactive Menu Mode
Launch the interactive terminal menu:
```bash
# On Linux / macOS / Git Bash:
./run.sh

# On Windows PowerShell:
.\run.ps1
```

### 3. Headless Batch Execution Mode
Run a complete benchmark run without interactive prompts:
```bash
./run.sh --batch data/full_benchmark_suite.json
```

### 4. Running Comparative Analysis
Compare all algorithms for a specific module:
```bash
python main.py --compare cpu
python main.py --compare memory
python main.py --compare deadlock
python main.py --compare disk
```

### 5. Automated Test Suite (Phase 4)
Run all automated test cases:
```bash
pytest tests/ -v --cov=src
```

---

## Visual Demonstrations & System Screenshots

### 1. Interactive Terminal Menu (CLI Control Center)
![Interactive Menu](docs/screenshots/01_interactive_menu.png)

### 2. CPU Process Scheduling Comparative Evaluation & Gantt Chart
![CPU Scheduling](docs/screenshots/02_cpu_scheduling.png)

### 3. Memory Partitioning (First/Best/Worst Fit) & Page Replacement (FIFO/LRU/Optimal)
![Memory & Paging](docs/screenshots/03_memory_paging.png)

### 4. Deadlock Avoidance (Dijkstra's Banker's Algorithm Safe State & Request Evaluation)
![Deadlock Banker's](docs/screenshots/04_deadlock_bankers.png)

### 5. Storage / Disk Head Trajectory Scheduling Comparison (FCFS, SSTF, SCAN, LOOK)
![Disk Scheduling](docs/screenshots/05_disk_scheduling.png)

### 6. Automated Pytest Suite & Coverage Verification (27 / 27 Passing, 91% Coverage)
![Pytest Coverage](docs/screenshots/06_pytest_coverage.png)

### 7. Bash Pre-Flight Diagnostics & Health Check
![Health Check](docs/screenshots/07_health_check.png)

### 8. Automated Bash Batch Benchmark Pipeline Execution
![Batch Benchmark](docs/screenshots/08_batch_benchmark.png)

---

## Documentation Links
- [Assignment Instructions & Rubric](INSTRUCTIONS.md)
- [Phase 1: System Design and Planning](docs/phases/PHASE_1_SYSTEM_DESIGN.md)
- [Phase 2: Core Resource-Management Implementation](docs/phases/PHASE_2_IMPLEMENTATION.md)
- [Phase 3: Analysis and Comparison](docs/phases/PHASE_3_ANALYSIS.md)
- [Phase 4: Testing and Reliability](docs/phases/PHASE_4_TESTING.md)
- [Phase 5: Demonstration & Final Report](docs/phases/PHASE_5_FINAL_REPORT.md)
- [Official Submission PDF Report (Sahil Raj)](output/reports/Sahil_Raj_2401410004_Capstone_Report.pdf) (~1.4 MB, < 25MB Portal Limit)
- [Official Submission PDF Report (Generic)](output/reports/Capstone_Final_Report.pdf) (~1.4 MB)
- [Assignment Rubric Image](docs/assets/capstone_assignment_portal.png)
