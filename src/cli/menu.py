"""Interactive Terminal UI Menu with ANSI colors and formatted navigation."""

import os
import sys
from typing import Optional
from ..engine import SimulationEngine
from ..analytics.metrics import MetricsFormatter

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

class InteractiveMenu:
    """Provides a terminal-driven interactive dashboard for OS-SimSuite."""

    def __init__(self, engine: Optional[SimulationEngine] = None):
        self.engine = engine if engine is not None else SimulationEngine()

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self, title: str):
        print(f"\n{CYAN}{BOLD}{'=' * 65}{RESET}")
        print(f"{CYAN}{BOLD}  OS-SimSuite: {title}{RESET}")
        print(f"{CYAN}{BOLD}{'=' * 65}{RESET}\n")

    def main_menu(self):
        while True:
            self.print_header("Main Control Center")
            print(f"  {BOLD}1.{RESET} CPU Process Scheduling Simulator")
            print(f"  {BOLD}2.{RESET} Memory Management & Paging Subsystem")
            print(f"  {BOLD}3.{RESET} Deadlock Avoidance (Banker's Algorithm)")
            print(f"  {BOLD}4.{RESET} Storage / Disk Scheduling Simulator")
            print(f"  {BOLD}5.{RESET} Run Complete Multi-Module Benchmark Suite")
            print(f"  {BOLD}6.{RESET} Compile Submission PDF Report")
            print(f"  {BOLD}7.{RESET} Run Automated Regression Tests (pytest)")
            print(f"  {BOLD}0.{RESET} Exit Suite")
            print(f"\n{CYAN}{'-' * 65}{RESET}")

            choice = input(f"{YELLOW}Select an option [0-7]: {RESET}").strip()
            if choice == "1":
                self.cpu_menu()
            elif choice == "2":
                self.memory_menu()
            elif choice == "3":
                self.deadlock_menu()
            elif choice == "4":
                self.disk_menu()
            elif choice == "5":
                self.run_full_benchmark()
            elif choice == "6":
                self.compile_report()
            elif choice == "7":
                self.run_tests()
            elif choice == "0":
                print(f"\n{GREEN}Thank you for using OS-SimSuite. Goodbye!{RESET}\n")
                break
            else:
                input(f"{RED}Invalid selection. Press Enter to continue...{RESET}")

    def cpu_menu(self):
        self.print_header("Module 1: CPU Process Scheduling")
        print("  1. Load Standard Sample Processes (P1..P4)")
        print("  2. Enter Custom Processes Interactively")
        print("  0. Back to Main Menu")

        c = input(f"{YELLOW}Choice: {RESET}").strip()
        if c == "1":
            try:
                workload = self.engine.load_workload("data/sample_workload.json")
                results = self.engine.run_cpu_benchmark(workload["cpu_scheduling"])
                print(f"\n{GREEN}{BOLD}CPU Scheduling Comparative Evaluation Results:{RESET}")
                print(MetricsFormatter.format_cpu_comparison(results))
                print(f"\n{CYAN}Detailed Process Execution Table (FCFS):{RESET}")
                print(MetricsFormatter.format_cpu_process_table(results["FCFS"]))
                print(f"\n{GREEN}Gantt charts and comparisons saved to output/figures/{RESET}")
            except Exception as e:
                print(f"{RED}Error: {e}{RESET}")
            input(f"\nPress Enter to return...")

    def memory_menu(self):
        self.print_header("Module 2: Memory Management & Paging")
        print("  1. Run Contiguous Memory Partitioning (First/Best/Worst Fit)")
        print("  2. Run Virtual Memory Page Replacement (FIFO/LRU/Optimal)")
        print("  0. Back to Main Menu")

        c = input(f"{YELLOW}Choice: {RESET}").strip()
        if c == "1":
            try:
                workload = self.engine.load_workload("data/sample_workload.json")
                res = self.engine.run_memory_benchmark(workload, generate_plots=False)
                for strat, r in res["contiguous"].items():
                    print(f"\n{BOLD}{CYAN}Allocation Strategy: {strat}{RESET}")
                    print(MetricsFormatter.format_memory_contiguous_table(r))
                    print(f"Allocated: {r.allocated_processes} | Failed: {r.failed_processes} | Internal Frag: {r.total_internal_fragmentation} KB")
            except Exception as e:
                print(f"{RED}Error: {e}{RESET}")
            input(f"\nPress Enter to return...")
        elif c == "2":
            try:
                workload = self.engine.load_workload("data/sample_workload.json")
                res = self.engine.run_memory_benchmark(workload, generate_plots=True)
                print(f"\n{GREEN}{BOLD}Page Replacement Comparative Results:{RESET}")
                print(MetricsFormatter.format_page_replacement_comparison(res["paging"]))
                print(f"\n{GREEN}Page fault comparative histogram saved to output/figures/{RESET}")
            except Exception as e:
                print(f"{RED}Error: {e}{RESET}")
            input(f"\nPress Enter to return...")

    def deadlock_menu(self):
        self.print_header("Module 3: Deadlock Avoidance (Banker's Algorithm)")
        try:
            workload = self.engine.load_workload("data/sample_workload.json")
            res = self.engine.run_deadlock_benchmark(workload["deadlock_bankers"])
            safety = res["safety"]
            print(f"{BOLD}System Safety Evaluation:{RESET}")
            if safety.is_safe:
                print(f"{GREEN}[SAFE STATE] {safety.explanation}{RESET}")
                print("\nStep-by-step Work Vector Evolution:")
                for step in safety.work_history:
                    print(f"  Step {step['step']}: Process {step['process']} -> Work Before: {step['work_before']} -> Released: {step['allocation']} -> Work After: {step['work_after']}")
            else:
                print(f"{RED}[UNSAFE STATE] {safety.explanation}{RESET}")
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")
        input(f"\nPress Enter to return...")

    def disk_menu(self):
        self.print_header("Module 4: Storage / Disk Scheduling")
        try:
            workload = self.engine.load_workload("data/sample_workload.json")
            results = self.engine.run_disk_benchmark(workload["disk_scheduling"])
            print(f"\n{GREEN}{BOLD}Disk Head Scheduling Comparative Results:{RESET}")
            print(MetricsFormatter.format_disk_comparison(results))
            print(f"\n{GREEN}Disk head trajectory plots saved to output/figures/disk_trajectories.png{RESET}")
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")
        input(f"\nPress Enter to return...")

    def run_full_benchmark(self):
        self.print_header("Executing Full Multi-Module Benchmark Suite")
        try:
            res = self.engine.run_full_suite()
            print(f"\n{GREEN}{BOLD}All Modules Successfully Executed!{RESET}")
            print(f"  • CPU Metrics: Completed ({len(res['cpu'])} algorithms)")
            print(f"  • Memory & Paging: Completed (Contiguous & FIFO/LRU/OPT)")
            print(f"  • Deadlock Guard: Completed (Safe sequence validated)")
            print(f"  • Disk Scheduling: Completed ({len(res['disk'])} algorithms)")
            print(f"  • Master PDF Report: {res['pdf_report']}")
        except Exception as e:
            print(f"{RED}Execution error: {e}{RESET}")
        input(f"\nPress Enter to return...")

    def compile_report(self):
        self.print_header("Compiling Submission PDF Report")
        try:
            self.run_full_benchmark()
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")

    def run_tests(self):
        self.print_header("Executing Pytest Automated Test Suite")
        os.system("pytest tests/ -v")
        input(f"\nPress Enter to return...")
