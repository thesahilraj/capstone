#!/usr/bin/env python3
"""Main Entry Point for OS-SimSuite.
Supports interactive menu mode, headless batch processing, comparative analysis, and report generation.
"""

import sys
import argparse
import os
from src.engine import SimulationEngine
from src.cli.menu import InteractiveMenu
from src.analytics.metrics import MetricsFormatter

def main():
    parser = argparse.ArgumentParser(
        description="OS-SimSuite: Integrated Operating System Resource-Management Simulator & Analytics Engine"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Launch the interactive terminal dashboard menu"
    )
    parser.add_argument(
        "--batch", "-b", type=str, metavar="CONFIG_FILE", help="Run simulation in headless batch mode using a JSON workload"
    )
    parser.add_argument(
        "--compare", "-c", choices=["cpu", "memory", "deadlock", "disk", "all"],
        help="Run comparative analysis for a specific module or all modules"
    )
    parser.add_argument(
        "--report", "-r", action="store_true", help="Generate publication-ready final PDF report"
    )
    parser.add_argument(
        "--student-name", type=str, default="Sahil Raj", help="Candidate name for the report"
    )
    parser.add_argument(
        "--roll-number", type=str, default="2401410004", help="Candidate roll number for the report"
    )
    parser.add_argument(
        "--test", "-t", action="store_true", help="Execute automated pytest regression tests"
    )

    args = parser.parse_args()
    engine = SimulationEngine()

    if args.test:
        import pytest
        sys.exit(pytest.main(["tests/", "-v"]))

    if args.batch:
        print(f"Executing batch workload from: {args.batch}")
        res = engine.run_full_suite(args.batch, student_name=args.student_name, roll_number=args.roll_number)
        print("Batch execution completed successfully. Report generated at:", res["pdf_report"])
        return

    if args.compare:
        config = engine.load_workload("data/sample_workload.json")
        target = args.compare.lower()
        if target in ["cpu", "all"]:
            cpu_res = engine.run_cpu_benchmark(config["cpu_scheduling"])
            print("\n[CPU SCHEDULING COMPARISON]")
            print(MetricsFormatter.format_cpu_comparison(cpu_res))
        if target in ["memory", "all"]:
            mem_res = engine.run_memory_benchmark(config)
            print("\n[PAGE REPLACEMENT COMPARISON]")
            print(MetricsFormatter.format_page_replacement_comparison(mem_res["paging"]))
        if target in ["deadlock", "all"]:
            dl_res = engine.run_deadlock_benchmark(config["deadlock_bankers"])
            print("\n[DEADLOCK SAFETY EVALUATION]")
            print(dl_res["safety"].explanation)
        if target in ["disk", "all"]:
            disk_res = engine.run_disk_benchmark(config["disk_scheduling"])
            print("\n[DISK SCHEDULING COMPARISON]")
            print(MetricsFormatter.format_disk_comparison(disk_res))
        return

    if args.report:
        print(f"Generating comprehensive PDF report for {args.student_name} ({args.roll_number})...")
        res = engine.run_full_suite("data/sample_workload.json", student_name=args.student_name, roll_number=args.roll_number)
        print(f"Final Report successfully compiled: {res['pdf_report']}")
        return

    # Default to interactive menu if no flags provided or --interactive specified
    menu = InteractiveMenu(engine)
    menu.main_menu()

if __name__ == "__main__":
    main()
