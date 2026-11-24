"""Animated Architecture Generator for OS Simulator.
Renders an animated high-tech system architecture topology diagram (GIF)
with flowing neon signal pulses between architectural tiers.
"""

import math
import os
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "C:\\Windows\\Fonts\\consola.ttf"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "assets", "architecture_animated.gif")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# Canvas Dimensions
WIDTH = 1000
HEIGHT = 580

# Dark Palette
BG_COLOR = (13, 17, 23)           # GitHub Dark
PANEL_BG = (22, 27, 34)           # Card background
PANEL_BORDER = (48, 54, 61)       # Subtle border
LINE_BASE = (33, 38, 45)          # Inactive bus line
TEXT_MAIN = (240, 246, 252)       # Bright text
TEXT_MUTED = (139, 148, 158)      # Dim text

# Accent Colors
CYAN = (88, 166, 255)
GREEN = (63, 185, 80)
PURPLE = (188, 140, 255)
AMBER = (210, 153, 34)
CORAL = (248, 81, 73)

def draw_rounded_card(draw: ImageDraw.Draw, box: Tuple[int, int, int, int], fill, border, radius=8):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=border, width=1)

def generate_frames() -> List[Image.Image]:
    font_title = ImageFont.truetype(FONT_PATH, 16)
    font_bold = ImageFont.truetype(FONT_PATH, 13)
    font_sm = ImageFont.truetype(FONT_PATH, 11)
    font_xs = ImageFont.truetype(FONT_PATH, 10)

    # Coordinates
    # Tier 1: Presentation (Top Center)
    t1_box = (200, 30, 800, 95)
    t1_center = ((t1_box[0] + t1_box[2]) // 2, t1_box[3])

    # Tier 2: Simulation Controller
    t2_box = (250, 140, 750, 205)
    t2_top = ((t2_box[0] + t2_box[2]) // 2, t2_box[1])
    t2_bottom = ((t2_box[0] + t2_box[2]) // 2, t2_box[3])

    # Tier 3: 4 Modules
    m_w = 210
    m_h = 135
    m_y = 265
    gap = 25
    total_m_w = 4 * m_w + 3 * gap
    start_x = (WIDTH - total_m_w) // 2

    m_boxes = [
        (start_x + i * (m_w + gap), m_y, start_x + i * (m_w + gap) + m_w, m_y + m_h)
        for i in range(4)
    ]
    m_tops = [((b[0] + b[2]) // 2, b[1]) for b in m_boxes]
    m_bottoms = [((b[0] + b[2]) // 2, b[3]) for b in m_boxes]

    # Tier 4: Analytics Engine (Bottom Center)
    t4_box = (180, 455, 820, 530)
    t4_top = ((t4_box[0] + t4_box[2]) // 2, t4_box[1])

    # Generate 45 frames for a smooth 1.8s loop (40ms per frame)
    num_frames = 45
    frames = []

    module_data = [
        ("1. CPU Scheduler", ["• FCFS & Round Robin", "• SJF & SRTF Preemptive", "• Priority Scheduling"], CYAN),
        ("2. Memory Manager", ["• First/Best/Worst Fit", "• Coalescing & Compact", "• FIFO, LRU, Optimal"], GREEN),
        ("3. Deadlock Guard", ["• Dijkstra's Banker's", "• Safety Sequence Solv.", "• Speculative Allocate"], AMBER),
        ("4. Storage Scheduler", ["• FCFS, SSTF & SCAN", "• C-SCAN, LOOK, C-LOOK", "• Trajectory Tracking"], CORAL),
    ]

    for f_idx in range(num_frames):
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)
        t = f_idx / num_frames  # normalized 0.0 to 1.0

        # ----------------------------------------------------
        # 1. Base Connections (Static bus lines)
        # ----------------------------------------------------
        # Line Tier 1 -> Tier 2
        draw.line([t1_center, t2_top], fill=LINE_BASE, width=2)

        # Bus Line Tier 2 -> Tier 3
        bus_y1 = 235
        draw.line([t2_bottom, (t2_bottom[0], bus_y1)], fill=LINE_BASE, width=2)
        draw.line([(m_tops[0][0], bus_y1), (m_tops[-1][0], bus_y1)], fill=LINE_BASE, width=2)
        for m_top in m_tops:
            draw.line([(m_top[0], bus_y1), m_top], fill=LINE_BASE, width=2)

        # Bus Line Tier 3 -> Tier 4
        bus_y2 = 425
        for m_bot in m_bottoms:
            draw.line([m_bot, (m_bot[0], bus_y2)], fill=LINE_BASE, width=2)
        draw.line([(m_bottoms[0][0], bus_y2), (m_bottoms[-1][0], bus_y2)], fill=LINE_BASE, width=2)
        draw.line([(t4_top[0], bus_y2), t4_top], fill=LINE_BASE, width=2)

        # ----------------------------------------------------
        # 2. Animated Signal Pulses / Flowing Energy
        # ----------------------------------------------------
        # Signal 1: Flowing from Tier 1 to Tier 2 (Phase: 0.0 to 0.25)
        p1 = (t * 2.0) % 1.0
        p1_y = int(t1_center[1] + p1 * (t2_top[1] - t1_center[1]))
        draw.ellipse([(t1_center[0] - 4, p1_y - 4), (t1_center[0] + 4, p1_y + 4)], fill=CYAN)
        draw.ellipse([(t1_center[0] - 2, p1_y - 2), (t1_center[0] + 2, p1_y + 2)], fill=(255, 255, 255))

        # Signal 2: Diverging from Tier 2 to 4 Modules (Phase: 0.25 to 0.65)
        p2 = (t + 0.25) % 1.0
        for idx, (m_top, (_, _, mod_col)) in enumerate(zip(m_tops, module_data)):
            # Segment along bus: vertical -> horizontal -> vertical
            if p2 < 0.3:
                curr_pt = (t2_bottom[0], int(t2_bottom[1] + (p2 / 0.3) * (bus_y1 - t2_bottom[1])))
            elif p2 < 0.7:
                hp = (p2 - 0.3) / 0.4
                curr_pt = (int(t2_bottom[0] + hp * (m_top[0] - t2_bottom[0])), bus_y1)
            else:
                vp = (p2 - 0.7) / 0.3
                curr_pt = (m_top[0], int(bus_y1 + vp * (m_top[1] - bus_y1)))
            draw.ellipse([(curr_pt[0] - 3, curr_pt[1] - 3), (curr_pt[0] + 3, curr_pt[1] + 3)], fill=mod_col)

        # Signal 3: Converging from 4 Modules to Tier 4 (Phase: 0.60 to 1.0)
        p3 = (t + 0.60) % 1.0
        for idx, (m_bot, (_, _, mod_col)) in enumerate(zip(m_bottoms, module_data)):
            if p3 < 0.35:
                curr_pt = (m_bot[0], int(m_bot[1] + (p3 / 0.35) * (bus_y2 - m_bot[1])))
            elif p3 < 0.75:
                hp = (p3 - 0.35) / 0.4
                curr_pt = (int(m_bot[0] + hp * (t4_top[0] - m_bot[0])), bus_y2)
            else:
                vp = (p3 - 0.75) / 0.25
                curr_pt = (t4_top[0], int(bus_y2 + vp * (t4_top[1] - bus_y2)))
            draw.ellipse([(curr_pt[0] - 3, curr_pt[1] - 3), (curr_pt[0] + 3, curr_pt[1] + 3)], fill=GREEN)

        # ----------------------------------------------------
        # 3. Draw Nodes (Cards)
        # ----------------------------------------------------
        # Tier 1 Card
        draw_rounded_card(draw, t1_box, PANEL_BG, PANEL_BORDER)
        draw.text((t1_box[0] + 16, t1_box[1] + 12), "PRESENTATION & WORKFLOW AUTOMATION LAYER", font=font_bold, fill=CYAN)
        draw.text((t1_box[0] + 16, t1_box[1] + 38), "• run.sh (Bash Orchestrator)   • run.ps1 (PowerShell)   • Interactive Terminal UI   • Headless CLI", font=font_sm, fill=TEXT_MUTED)

        # Tier 2 Card
        pulse_val = (math.sin(t * 2 * math.pi) + 1) / 2
        t2_border = (int(48 + 30 * pulse_val), int(54 + 50 * pulse_val), int(61 + 80 * pulse_val))
        draw_rounded_card(draw, t2_box, PANEL_BG, t2_border)
        draw.text((t2_box[0] + 20, t2_box[1] + 12), "SIMULATION CONTROLLER ENGINE (src/engine.py)", font=font_bold, fill=TEXT_MAIN)
        draw.text((t2_box[0] + 20, t2_box[1] + 36), "• Input Validation & Boundary Guard    • Structured Telemetry Logger    • Execution Dispatcher", font=font_sm, fill=TEXT_MUTED)

        # Tier 3: 4 OS Modules Cards
        for idx, (m_box, (mod_title, mod_items, mod_color)) in enumerate(zip(m_boxes, module_data)):
            # Glow pulse for active module
            phase_offset = idx * (math.pi / 2)
            card_pulse = (math.sin(t * 2 * math.pi + phase_offset) + 1) / 2
            card_border = tuple(int(PANEL_BORDER[c] + (mod_color[c] - PANEL_BORDER[c]) * 0.45 * card_pulse) for c in range(3))

            draw_rounded_card(draw, m_box, PANEL_BG, card_border)

            # Header bar accent
            draw.rectangle([(m_box[0] + 1, m_box[1] + 1), (m_box[2] - 1, m_box[1] + 4)], fill=mod_color)
            draw.text((m_box[0] + 12, m_box[1] + 14), mod_title, font=font_bold, fill=TEXT_MAIN)

            # Content bullets
            y_off = m_box[1] + 42
            for item in mod_items:
                draw.text((m_box[0] + 12, y_off), item, font=font_xs, fill=TEXT_MUTED)
                y_off += 22

            # Mini activity beacon
            beacon_alpha = int(120 + 135 * card_pulse)
            beacon_col = tuple(int(mod_color[c] * (beacon_alpha / 255)) for c in range(3))
            draw.ellipse([(m_box[2] - 18, m_box[1] + 14), (m_box[2] - 10, m_box[1] + 22)], fill=beacon_col)

        # Tier 4 Card
        t4_pulse = (math.sin(t * 2 * math.pi + math.pi) + 1) / 2
        t4_border = (int(48 + 40 * t4_pulse), int(54 + 80 * t4_pulse), int(61 + 40 * t4_pulse))
        draw_rounded_card(draw, t4_box, PANEL_BG, t4_border)
        draw.text((t4_box[0] + 24, t4_box[1] + 12), "ANALYTICS, VISUALIZATION & REPORTING ENGINE", font=font_bold, fill=GREEN)
        draw.text((t4_box[0] + 24, t4_box[1] + 36), "• Matplotlib Figures (Gantt, Trajectories, Bar Charts)   • CSV & Text Execution Traces   • Capstone Final PDF", font=font_sm, fill=TEXT_MUTED)

        # Watermark
        draw.text((WIDTH - 250, HEIGHT - 22), "OS Architecture Live Signal Flow", font=font_xs, fill=(80, 85, 95))

        frames.append(img)

    return frames

def build_gif():
    print("[ANIMATION] Rendering 45 high-tech architecture frames...")
    frames = generate_frames()

    # Convert to adaptive 256-color palette for sharp, lightweight GIF
    palette_frames = []
    for f in frames:
        p_frame = f.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
        palette_frames.append(p_frame)

    print(f"[ANIMATION] Saving optimized GIF to: {OUTPUT_PATH}")
    palette_frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=palette_frames[1:],
        duration=40,   # 40ms per frame = 25 FPS
        loop=0,        # Infinite loop
        optimize=True
    )

    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"[ANIMATION] Complete! File Size: {size_kb:.1f} KB")

if __name__ == "__main__":
    build_gif()
