#!/usr/bin/env python3
"""Add detailed debug logging to trace coordinate conversion."""
import os, re

script_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(script_dir, "main.py")

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# 1. Fix _onDown debug print
old_down = '        print(f"[DEBUG] _onDown: tool={self.tool}, stabilizerMethod={self.stabilizerMethod}, brushSize={self.brushSize}, brushHardness={self.brushHardness}, symmetry={self.symmetry}")'
new_down = """        # DEBUG: detail koordinat
        w_canvas = self.tkCanvas.winfo_width() or 800
        h_canvas = self.tkCanvas.winfo_height() or 600
        sw_ = int(self.CW * self.zoom)
        sh_ = int(self.CH * self.zoom)
        ox_ = self.offsetX if self.offsetX is not None else (w_canvas - sw_) // 2
        oy_ = self.offsetY if self.offsetY is not None else (h_canvas - sh_) // 2
        print(f"[DEBUG] _onDown: screen=({event.x},{event.y}), img=({round(x)},{round(y)}), zoom={self.zoom:.2f}, ox={ox_:.2f}, oy={oy_:.2f}, sw={sw_}, sh={sh_}, tool={self.tool}, mode={self.stabilizerMethod}")"""

if old_down in content:
    content = content.replace(old_down, new_down, 1)
    print("1. _onDown debug updated.")
    changes += 1
else:
    print("1. _onDown debug NOT FOUND!")

# 2. Fix _onMove debug print
old_move = """        self.currentStroke.append(self._pt(x_raw, y_raw))
        latest = self.currentStroke[-1]
        print(f\"[DEBUG] _onMove: pts={len(self.currentStroke)}, last_X={round(latest['x'])}, last_Y={round(latest['y'])}, color={latest['color']}, size={latest['size']}, opacity={latest['opacity']}, mode={latest['mode']}, layer={latest['layer']}\")"""

new_move = """        self.currentStroke.append(self._pt(x_raw, y_raw))
        latest = self.currentStroke[-1]
        # DEBUG: detail koordinat screen vs image
        wc = self.tkCanvas.winfo_width() or 800
        hc = self.tkCanvas.winfo_height() or 600
        sw_ = int(self.CW * self.zoom)
        sh_ = int(self.CH * self.zoom)
        ox_ = self.offsetX if self.offsetX is not None else (wc - sw_) // 2
        oy_ = self.offsetY if self.offsetY is not None else (hc - sh_) // 2
        print(f"[DEBUG] _onMove: pts={len(self.currentStroke)}, screen=({event.x},{event.y}), img=({round(latest['x'])},{round(latest['y'])}), zoom={self.zoom:.2f}, ox={ox_:.2f}, oy={oy_:.2f}, tool={self.tool}")"""

if old_move in content:
    content = content.replace(old_move, new_move, 1)
    print("2. _onMove debug updated.")
    changes += 1
else:
    print("2. _onMove debug NOT FOUND - trying alt pattern...")
    # Try the pattern without the latest = ... line
    old_move_alt = """        self.currentStroke.append(self._pt(x_raw, y_raw))
        print(f\"[DEBUG] _onMove: pts={len(self.currentStroke)}, last=({round(x_raw)},{round(y_raw)}), mode={self.stabilizerMethod}\")"""
    if old_move_alt in content:
        content = content.replace(old_move_alt, new_move, 1)
        print("2. _onMove debug updated (alt).")
        changes += 1
    else:
        print("2. _onMove NOT FOUND at all!")

# Save
if changes > 0:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    import py_compile
    try:
        compile(content, filepath, "exec")
        print(f"\nSYNTAX OK! {changes} change(s) applied.")
    except SyntaxError as e:
        print(f"\nSYNTAX ERROR at line {e.lineno}: {e.msg}")
else:
    print("\nNo changes made.")
