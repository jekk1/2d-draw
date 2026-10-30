import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD # type: ignore
import json, os, io, time, threading, math, base64, gzip, re
from datetime import datetime
from PIL import Image, ImageChops, ImageDraw, ImageTk, ImageFilter # pyright: ignore[reportMissingImports]

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
PROJECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# warna tema - pure dark, no blue
C = {
        "bg":       "#121212",
        "panel":    "#1e1e1e",
        "card":     "#282828",
        "hover":    "#333333",
        "border":   "#3a3a3a",
        "accent":   "#ff6b35",
        "accent2":  "#ff8c42",
        "accent3":  "#e85d26",
        "text":     "#f0f0f0",
        "dim":      "#888888",
        "muted":    "#5a5a5a",
        "success":  "#4caf50",
        "danger":   "#ef5350",
        "canvas_bg":"#404040",
    }

FONT        = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI", 10, "bold")
FONT_SM     = ("Segoe UI", 8)
FONT_XS     = ("Segoe UI", 7)
FONT_ICON   = ("Segoe UI Symbol", 14)
FONT_TITLE  = ("Segoe UI", 24, "bold")
FONT_SUB    = ("Segoe UI", 14)

CANVAS_PRESETS = [
        {"label": "Square",       "ratio": "1:1",  "w": 1000, "h": 1000},
        {"label": "HD 16:9",      "ratio": "16:9", "w": 1920, "h": 1080},
        {"label": "2K 16:9",      "ratio": "16:9", "w": 2560, "h": 1440},
        {"label": "4K UHD",       "ratio": "16:9", "w": 3840, "h": 2160},
        {"label": "Portrait 9:16","ratio": "9:16", "w": 1080, "h": 1920},
        {"label": "2K Portrait",  "ratio": "9:16", "w": 1440, "h": 2560},
        {"label": "4:3",          "ratio": "4:3",  "w": 1600, "h": 1200},
        {"label": "A4 Portrait",  "ratio": "A4",   "w": 2480, "h": 3508},
        {"label": "A4 Landscape", "ratio": "A4L",  "w": 3508, "h": 2480},
        {"label": "Instagram",    "ratio": "1:1",  "w": 1080, "h": 1080},
        {"label": "Custom",       "ratio": "?",    "w": None, "h": None},
    ]

# Built-in brush library.  Each preset maps to the brush engine's real
# parameters (size, opacity, hardness, and tool); custom brushes use the same
# portable format and are stored with the project.
BRUSH_PRESETS = [
        ("Ink", 8, 100, 100, "brush"), ("Fine Liner", 3, 100, 100, "brush"),
        ("G-Pen", 12, 100, 100, "brush"), ("Round Pen", 16, 92, 100, "brush"),
        ("Felt Tip", 18, 85, 100, "brush"), ("Marker", 28, 96, 85, "brush"),
        ("Highlighter", 42, 72, 35, "brush"), ("Soft Airbrush", 55, 18, 45, "brush"),
        ("Hard Airbrush", 38, 55, 55, "brush"), ("Watercolor", 48, 25, 40, "brush"),
        ("Gouache", 32, 78, 80, "brush"), ("Oil", 36, 88, 90, "brush"),
        ("Acrylic", 24, 94, 95, "brush"), ("Chalk", 22, 48, 75, "brush"),
        ("Charcoal", 30, 40, 85, "brush"), ("Pastel", 34, 38, 70, "brush"),
        ("Crayon", 20, 64, 90, "brush"), ("Pencil HB", 6, 100, 90, "pencil"),
        ("Pencil 2B", 10, 92, 86, "pencil"), ("Pencil 6B", 16, 72, 82, "pencil"),
        ("Pixel", 4, 100, 100, "brush"), ("Mono", 10, 100, 100, "brush"),
        ("Calligraphy", 18, 100, 100, "brush"), ("Sumi", 26, 82, 92, "brush"),
        ("Cloud", 64, 12, 35, "brush"), ("Mist", 80, 8, 20, "brush"),
        ("Glow", 35, 28, 55, "brush"), ("Neon", 14, 96, 95, "brush"),
        ("Texture", 26, 52, 80, "brush"), ("Dry Brush", 24, 58, 68, "brush"),
        ("Hair", 7, 86, 90, "brush"), ("Fur", 19, 50, 75, "brush"),
        ("Leaf", 32, 70, 88, "brush"), ("Ribbon", 22, 92, 90, "brush"),
        ("Spray", 46, 20, 38, "brush"), ("Blur", 60, 10, 30, "brush"),
        ("Eraser Soft", 35, 30, 100, "eraser"), ("Eraser Hard", 22, 100, 100, "eraser"),
        ("Blend", 30, 45, 60, "smudge"), ("Custom", 12, 100, 100, "brush"),
    ]


# ──────────────────────────────────────────────────────────────
# CUSTOM WIDGET HELPERS
# ──────────────────────────────────────────────────────────────
def flatBtn(parent, text, command, bg=None, fg=None, font=None,
                padx=14, pady=7, width=None, anchor="center", icon=None):
        bg   = bg   or C["card"]
        fg   = fg   or C["text"]
        font = font or FONT
        display = f" {icon}  {text}" if icon else text
        kw   = dict(text=display, command=command, bg=bg, fg=fg, bd=0,
                    relief="flat", cursor="hand2", font=font,
                    activebackground=C["hover"], activeforeground=C["text"],
                    padx=padx, pady=pady, anchor=anchor)
        if width:
            kw["width"] = width
        b = tk.Button(parent, **kw)
        def onEnter(e):
            b.config(bg=C["hover"])
            if bg != C["accent"] and bg != C["danger"]:
                b.config(fg=C["accent"])
        def onLeave(e):
            b.config(bg=bg, fg=fg)
        b.bind("<Enter>", onEnter)
        b.bind("<Leave>", onLeave)
        return b


def sectionTitle(parent, text, icon=""):
        f = tk.Frame(parent, bg=C["panel"])
        f.pack(fill="x", padx=12, pady=(16, 4))
        lbl_text = f"{icon} {text}" if icon else text
        tk.Label(f, text=lbl_text, bg=C["panel"], fg=C["accent"],
                font=("Segoe UI", 8, "bold")).pack(side="left")
        # Gradient-style line
        line = tk.Frame(f, bg=C["border"], height=1)
        line.pack(side="left", fill="x", expand=True, padx=(10, 0))
        # Small accent dot at end
        dot = tk.Frame(f, bg=C["accent"], width=4, height=4)
        dot.pack(side="right", padx=(6, 0))
        # Round the dot
        dot.update()
        try:
            dot.config(highlightthickness=0)
        except:
            pass


def sep(parent, pad=(0, 0)):
        container = tk.Frame(parent, bg=C["panel"])
        container.pack(fill="x", padx=12, pady=pad)
        tk.Frame(container, bg=C["border"], height=1).pack(fill="x")
        # Accent hint
        tk.Frame(container, bg=C["accent"], width=3, height=1).pack(side="right")


# ──────────────────────────────────────────────────────────────
# LAYER
# ──────────────────────────────────────────────────────────────
class Layer:
        def __init__(self, name="Layer", w=1920, h=1080):
            self.name    = name
            self.visible = True
            self.opacity = 255
            self.locked  = False
            self.image   = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            self.draw    = ImageDraw.Draw(self.image)
            self.w, self.h = w, h

        def snapshot(self):
            buf = io.BytesIO()
            self.image.save(buf, "PNG")
            return buf.getvalue()

        def restore(self, data):
            self.image = Image.open(io.BytesIO(data)).convert("RGBA")
            self.draw  = ImageDraw.Draw(self.image)

        def toDict(self):
            import base64
            return {
                "name": self.name, "visible": self.visible,
                "opacity": self.opacity, "locked": self.locked,
                "img": base64.b64encode(self.snapshot()).decode(),
            }

        @classmethod
        def fromDict(cls, d, w, h):
            import base64
            layer = cls(d["name"], w, h)
            layer.visible = d["visible"]
            layer.opacity = d["opacity"]
            layer.locked  = d.get("locked", False)
            layer.image = Image.open(io.BytesIO(base64.b64decode(d["img"]))).convert("RGBA")
            layer.draw    = ImageDraw.Draw(layer.image)
            return layer


# ──────────────────────────────────────────────────────────────
# ERASE SPATIAL INDEX
# ──────────────────────────────────────────────────────────────
class EraseGrid:
    """Spatial index for eraser-stroke footprints.

    Eraser strokes are turned into a set of (x, y, radius) holes.  A uniform
    grid lets us test "is this point erased?" in near-O(1) instead of checking
    every hole, so masking vector strokes stays fast even with hundreds of
    eraser strokes.
    """
    def __init__(self, cell=64):
        self.cell = max(1, cell)
        self.buckets = {}
        self.holes = []
        self.max_r = 0.0

    def add(self, hx, hy, r):
        idx = len(self.holes)
        self.holes.append((hx, hy, r))
        if r > self.max_r:
            self.max_r = r
        c0x = int((hx - r) // self.cell)
        c1x = int((hx + r) // self.cell)
        c0y = int((hy - r) // self.cell)
        c1y = int((hy + r) // self.cell)
        for cx in range(c0x, c1x + 1):
            for cy in range(c0y, c1y + 1):
                self.buckets.setdefault((cx, cy), []).append(idx)

    def query(self, x, y, extra=0.0):
        """True if (x, y) lies inside any hole expanded by ``extra``."""
        if not self.buckets:
            return False
        rad = extra + self.max_r
        c0x = int((x - rad) // self.cell)
        c1x = int((x + rad) // self.cell)
        c0y = int((y - rad) // self.cell)
        c1y = int((y + rad) // self.cell)
        for cx in range(c0x, c1x + 1):
            for cy in range(c0y, c1y + 1):
                for hi in self.buckets.get((cx, cy), ()):
                    hx, hy, r = self.holes[hi]
                    rr = r + extra
                    if (x - hx) * (x - hx) + (y - hy) * (y - hy) <= rr * rr:
                        return True
        return False


# ──────────────────────────────────────────────────────────────
# LAUNCH SCREEN
# ──────────────────────────────────────────────────────────────
class LaunchScreen:
        def __init__(self, root):
            self.root = root
            self.root.title("2D Draw Studio")
            self.root.configure(bg=C["bg"])
            self.root.geometry("1060x680")
            self.root.minsize(860, 560)

            self.selectedIdx = None
            self.customW     = tk.IntVar(value=1920)
            self.customH     = tk.IntVar(value=1080)

            self._buildUI()
            self._loadRecent()

        def _buildUI(self):
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(1, weight=1)

            # sidebar
            side = tk.Frame(self.root, bg=C["panel"], width=300)
            side.grid(row=0, column=0, sticky="nsew")
            side.grid_propagate(False)
            self._buildSidebar(side)

            # main
            main = tk.Frame(self.root, bg=C["bg"])
            main.grid(row=0, column=1, sticky="nsew")
            main.grid_rowconfigure(1, weight=1)
            main.grid_columnconfigure(0, weight=1)
            self._buildMain(main)

        def _buildSidebar(self, side):
            # logo
            logoArea = tk.Frame(side, bg=C["panel"])
            logoArea.pack(fill="x", padx=24, pady=(32, 0))

            # Logo with accent underline
            logoFrame = tk.Frame(logoArea, bg=C["panel"])
            logoFrame.pack(anchor="w")
            tk.Label(logoFrame, text="2D", bg=C["panel"], fg=C["accent"],
                    font=("Segoe UI", 30, "bold")).pack(side="left")
            tk.Label(logoFrame, text="Draw", bg=C["panel"], fg=C["text"],
                    font=("Segoe UI", 30, "bold")).pack(side="left")
            tk.Label(logoArea, text="Studio", bg=C["panel"], fg=C["dim"],
                    font=("Segoe UI", 12)).pack(anchor="w", padx=(2, 0))
            # Accent underline
            underline = tk.Frame(logoArea, bg=C["accent"], height=2)
            underline.pack(fill="x", pady=(4, 0))

            sep(side, pad=(20, 0))

            # action buttons
            btnArea = tk.Frame(side, bg=C["panel"])
            btnArea.pack(fill="x", padx=16, pady=16)

            newBtn = tk.Button(btnArea, text="  ✦  New Project",
                            command=self._openNewPanel,
                            bg=C["accent"], fg="#fff", bd=0, relief="flat",
                            font=("Segoe UI", 10, "bold"), cursor="hand2", pady=12, padx=0,
                            activebackground=C["accent2"], activeforeground="#fff")
            newBtn.pack(fill="x", pady=(0, 8))
            # Hover glow
            newBtn.bind("<Enter>", lambda e: newBtn.config(bg=C["accent2"]))
            newBtn.bind("<Leave>", lambda e: newBtn.config(bg=C["accent"]))

            openBtn = flatBtn(btnArea, "  Open Project", self._browseOpen,
                            padx=0, pady=9, anchor="center")
            openBtn.pack(fill="x")

            sep(side, pad=(12, 4))

            tk.Label(side, text="RECENT", bg=C["panel"], fg=C["dim"],
                    font=("Segoe UI", 7, "bold")).pack(anchor="w", padx=16, pady=(8, 4))

            # recent scroll
            rCanvas = tk.Canvas(side, bg=C["panel"], highlightthickness=0)
            sb = tk.Scrollbar(side, orient="vertical", command=rCanvas.yview,
                            bg=C["panel"], troughcolor=C["card"], bd=0,
                            highlightthickness=0, relief="flat", width=6)
            rCanvas.configure(yscrollcommand=sb.set)
            rCanvas.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")
            self._rightScrollCanvas = rCanvas

            self.recentFrame = tk.Frame(rCanvas, bg=C["panel"])
            winId = rCanvas.create_window((0, 0), window=self.recentFrame, anchor="nw")

            self.recentFrame.bind("<Configure>",
                lambda e: rCanvas.configure(scrollregion=rCanvas.bbox("all")))
            rCanvas.bind("<Configure>",
                lambda e: rCanvas.itemconfig(winId, width=e.width))
            rCanvas.bind("<MouseWheel>",
                lambda e: rCanvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        def _buildMain(self, main):
            # header
            hdr = tk.Frame(main, bg=C["bg"])
            hdr.grid(row=0, column=0, sticky="ew", padx=28, pady=(28, 0))
            tk.Label(hdr, text="Choose Canvas Size", bg=C["bg"], fg=C["text"],
                    font=FONT_TITLE).pack(side="left")
            tk.Label(hdr, text="start creating", bg=C["bg"], fg=C["dim"],
                    font=FONT_SUB).pack(side="left", padx=(12, 0))

            # preset scroll area
            wrapper = tk.Frame(main, bg=C["bg"])
            wrapper.grid(row=1, column=0, sticky="nsew", padx=24, pady=12)
            wrapper.grid_rowconfigure(0, weight=1)
            wrapper.grid_columnconfigure(0, weight=1)

            pc = tk.Canvas(wrapper, bg=C["bg"], highlightthickness=0)
            pc.grid(row=0, column=0, sticky="nsew")
            self.presetFrame = tk.Frame(pc, bg=C["bg"])
            self.presetWin   = pc.create_window((0, 0), window=self.presetFrame, anchor="nw")
            pc.bind("<Configure>", lambda e: (
                pc.itemconfig(self.presetWin, width=e.width),
                self._drawPresets()
            ))
            self.presetCanvas = pc

            # bottom bar
            bottom = tk.Frame(main, bg=C["panel"], height=72)
            bottom.grid(row=2, column=0, sticky="ew")
            bottom.grid_propagate(False)
            # Top accent line
            tk.Frame(bottom, bg=C["border"], height=1).pack(fill="x")

            self.selectedLbl = tk.Label(bottom, text="Select a canvas preset",
                                        bg=C["panel"], fg=C["dim"], font=("Segoe UI", 10))
            self.selectedLbl.pack(side="left", padx=24, pady=24)

            self.createBtn = tk.Button(
                bottom, text="  Create Project  →", command=self._create,
                bg=C["accent"], fg="#fff", bd=0, relief="flat",
                font=("Segoe UI", 10, "bold"), cursor="hand2", padx=28, pady=12,
                activebackground=C["accent2"], activeforeground="#fff",
                state="disabled"
            )
            self.createBtn.pack(side="right", padx=24, pady=16)

            # nama project
            nameFrame = tk.Frame(bottom, bg=C["panel"])
            nameFrame.pack(side="right", pady=14, padx=4)
            tk.Label(nameFrame, text="Name:", bg=C["panel"],
                    fg=C["dim"], font=FONT_SM).pack(side="left", padx=(0, 6))
            self.nameVar = tk.StringVar()
            nameEntry = tk.Entry(nameFrame, textvariable=self.nameVar,
                                bg=C["card"], fg=C["text"], insertbackground=C["text"],
                                bd=0, font=FONT, width=18, relief="flat",
                                highlightthickness=1, highlightcolor=C["accent"],
                                highlightbackground=C["border"])
            nameEntry.pack(side="left", ipadx=8, ipady=5)

            self._drawPresets()

        def _drawPresets(self):
            for w in self.presetFrame.winfo_children():
                w.destroy()

            cw   = self.presetCanvas.winfo_width() or 640
            cols = max(2, cw // 170)

            for i, preset in enumerate(CANVAS_PRESETS):
                row = i // cols
                col = i % cols
                isSelected = (self.selectedIdx == i)
                self._makePresetCard(self.presetFrame, preset, i, isSelected, row, col)

            for c in range(cols):
                self.presetFrame.grid_columnconfigure(c, weight=1)

        def _makePresetCard(self, parent, preset, idx, selected, row, col):
            bg  = C["accent"] if selected else C["card"]
            fg  = "#fff"      if selected else C["text"]
            dfg = "#ddd"      if selected else C["dim"]

            card = tk.Frame(parent, bg=bg, cursor="hand2",
                            highlightthickness=0, bd=0)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", ipadx=6, ipady=12)

            # Add subtle border highlight
            borderFrame = tk.Frame(card, bg=C["accent"] if selected else C["border"], bd=0, highlightthickness=0)
            borderFrame.pack(fill="both", expand=True, padx=0, pady=0)
            
            innerCard = tk.Frame(borderFrame, bg=bg, bd=0, highlightthickness=0)
            innerCard.pack(fill="both", expand=True, padx=1, pady=1)

            # ratio icon (canvas drawing) - bigger
            ic = tk.Canvas(innerCard, bg=bg, highlightthickness=0, width=100, height=68)
            ic.pack(pady=(16, 8))
            self._drawRatioIcon(ic, preset, "#fff" if selected else C["text"])

            tk.Label(innerCard, text=preset["label"], bg=bg, fg="#fff" if selected else C["text"],
                    font=("Segoe UI", 11, "bold") if selected else ("Segoe UI", 10, "bold")).pack()
            tk.Label(innerCard, text=preset["ratio"], bg=bg, fg="#ddd" if selected else C["dim"],
                    font=FONT_SM).pack()

            if preset["w"]:
                tk.Label(innerCard, text=f"{preset['w']} × {preset['h']}",
                        bg=bg, fg="#ddd" if selected else C["muted"], font=("Consolas", 8)).pack(pady=(4, 10))
            else:
                tk.Label(innerCard, text="custom size", bg=bg, fg="#ddd" if selected else C["dim"],
                        font=FONT_SM).pack(pady=(4, 10))

            def _bind_all(widget, i=idx):
                try:
                    widget.bind("<Button-1>", lambda e, i=i: self._selectPreset(i))
                    widget.bind("<Enter>",    lambda e, c=card, s=selected, b=bg: (
                        None if s else c.config(bg=C["hover"])))
                    widget.bind("<Leave>",    lambda e, c=card, s=selected, b=bg: (
                        None if s else c.config(bg=b)))
                except Exception:
                    pass
                for child in widget.winfo_children():
                    _bind_all(child, i=i)
            _bind_all(card)

        def _drawRatioIcon(self, ic, preset, color):
            iw, ih = 80, 58
            pad = 8
            if not preset["w"] or not preset["h"]:
                ic.create_text(iw//2, ih//2, text="?", fill=color,
                            font=("Segoe UI", 22, "bold"))
                return
            ratio = preset["w"] / preset["h"]
            maxW  = iw - pad * 2
            maxH  = ih - pad * 2
            if ratio >= 1:
                rw = maxW
                rh = max(6, int(maxW / ratio))
            else:
                rh = maxH
                rw = max(6, int(maxH * ratio))
            x0 = (iw - rw) // 2
            y0 = (ih - rh) // 2
            ic.create_rectangle(x0, y0, x0+rw, y0+rh, outline=color, width=2)

        def _selectPreset(self, idx):
            self.selectedIdx = idx
            preset = CANVAS_PRESETS[idx]
            if preset["w"] is None:
                self._customDialog()
            else:
                self.selectedLbl.config(
                    text=f"{preset['label']}  |  {preset['w']} × {preset['h']} px",
                    fg=C["text"])
                self.createBtn.config(state="normal")
            self._drawPresets()

        def _customDialog(self):
            dlg = tk.Toplevel(self.root)
            dlg.title("Custom Size")
            dlg.geometry("340x220")
            dlg.configure(bg=C["panel"])
            dlg.resizable(False, False)
            dlg.transient(self.root)
            dlg.grab_set()

            tk.Label(dlg, text="Custom Canvas Size", bg=C["panel"], fg=C["text"],
                    font=("Segoe UI", 12, "bold")).pack(pady=(22, 4))
            tk.Label(dlg, text="Enter dimensions in pixels (100 – 8000)",
                    bg=C["panel"], fg=C["dim"], font=FONT_SM).pack(pady=(0, 16))

            for label, var in [("Width", self.customW), ("Height", self.customH)]:
                row = tk.Frame(dlg, bg=C["panel"])
                row.pack(fill="x", padx=36, pady=4)
                tk.Label(row, text=label+":", bg=C["panel"], fg=C["dim"],
                        font=FONT, width=7, anchor="w").pack(side="left")
                e = tk.Entry(row, textvariable=var, bg=C["card"], fg=C["text"],
                            insertbackground=C["text"], bd=0, font=FONT,
                            width=10, relief="flat", highlightthickness=1,
                            highlightcolor=C["accent"], highlightbackground=C["border"])
                e.pack(side="left", ipadx=8, ipady=5)
                tk.Label(row, text=" px", bg=C["panel"], fg=C["dim"],
                        font=FONT_SM).pack(side="left")

            def apply():
                try:
                    w, h = int(self.customW.get()), int(self.customH.get())
                    if not (100 <= w <= 8000 and 100 <= h <= 8000):
                        raise ValueError
                    CANVAS_PRESETS[-1]["w"] = w
                    CANVAS_PRESETS[-1]["h"] = h
                    CANVAS_PRESETS[-1]["ratio"] = f"{w}:{h}"
                    self.selectedLbl.config(text=f"Custom  |  {w} × {h} px",
                                            fg=C["text"])
                    self.createBtn.config(state="normal")
                    dlg.destroy()
                except ValueError:
                    messagebox.showwarning("Invalid", "Enter valid pixel values (100-8000)",
                                        parent=dlg)

            tk.Button(dlg, text="Apply", command=apply,
                    bg=C["accent"], fg="#fff", bd=0, relief="flat",
                    font=FONT_BOLD, cursor="hand2", padx=24, pady=8,
                    activebackground=C["accent2"], activeforeground="#fff").pack(pady=16)

        def _create(self):
            if self.selectedIdx is None:
                return
            preset = CANVAS_PRESETS[self.selectedIdx]
            name   = self.nameVar.get().strip() or \
                    f"Project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            safe   = "".join(c for c in name if c.isalnum() or c in " _-").strip() or "Untitled"
            path   = os.path.join(PROJECTS_DIR, safe)
            n = 1
            base = path
            while os.path.exists(path):
                path = f"{base}_{n}"; n += 1
            os.makedirs(path)
            self._launch(safe, path, preset["w"], preset["h"])

        def _openNewPanel(self):
            self.selectedIdx = None
            self.nameVar.set("")
            self.selectedLbl.config(text="Select a canvas preset", fg=C["dim"])
            self.createBtn.config(state="disabled")
            self._drawPresets()

        def _browseOpen(self):
            path = filedialog.askdirectory(initialdir=PROJECTS_DIR,
                                        title="Open Project Folder")
            if not path:
                return
            dataPath = os.path.join(path, "projectData.json")
            if not os.path.exists(dataPath):
                messagebox.showerror("Error", "No valid project found.")
                return
            with open(dataPath) as f:
                data = json.load(f)
            self._launch(data.get("name", os.path.basename(path)), path,
                        data["canvasWidth"], data["canvasHeight"], loadData=data)

        # * Memuat daftar proyek yang baru saja dibuat/disimpan berdasarkan waktu modifikasi
        def _loadRecent(self):
            for w in self.recentFrame.winfo_children():
                w.destroy()

            projects = []
            if os.path.exists(PROJECTS_DIR):
                for item in os.listdir(PROJECTS_DIR):
                    p = os.path.join(PROJECTS_DIR, item)
                    dp = os.path.join(p, "projectData.json")
                    if os.path.isdir(p) and os.path.exists(dp):
                        try:
                            mtime = os.path.getmtime(dp)
                            projects.append((item, p, dp, mtime))
                        except Exception:
                            pass
                projects.sort(key=lambda x: x[3], reverse=True)

            if not projects:
                tk.Label(self.recentFrame, text="No recent projects",
                        bg=C["panel"], fg=C["dim"], font=FONT_SM).pack(pady=16)
                return

            for name, path, dp, _ in projects[:20]:
                self._recentCard(name, path, dp)

        def _recentCard(self, name, path, dp):
            try:
                with open(dp) as f:
                    meta = json.load(f)
                w    = meta.get("canvasWidth",  "?")
                h    = meta.get("canvasHeight", "?")
                date = meta.get("savedAt", "")[:10]
            except Exception:
                w = h = "?"; date = ""

            card = tk.Frame(self.recentFrame, bg=C["panel"], cursor="hand2")
            card.pack(fill="x", padx=8, pady=2)

            previewPath = os.path.join(path, "preview.png")
            if os.path.exists(previewPath):
                try:
                    img   = Image.open(previewPath).resize((52, 38), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    lbl   = tk.Label(card, image=photo, bg=C["card"], bd=0)
                    lbl.image = photo
                    lbl.pack(side="left", padx=(6, 8), pady=6)
                except Exception:
                    tk.Frame(card, bg=C["card"], width=52, height=38).pack(
                        side="left", padx=(6, 8), pady=6)
            else:
                tk.Frame(card, bg=C["card"], width=52, height=38).pack(
                    side="left", padx=(6, 8), pady=6)

            info = tk.Frame(card, bg=C["panel"])
            info.pack(side="left", fill="both", expand=True, pady=6)
            tk.Label(info, text=name, bg=C["panel"], fg=C["text"],
                    font=FONT_BOLD, anchor="w").pack(anchor="w")
            tk.Label(info, text=f"{w} × {h}   {date}", bg=C["panel"],
                    fg=C["dim"], font=("Consolas", 7), anchor="w").pack(anchor="w")

            def openIt(e=None):
                try:
                    with open(dp) as f:
                        data = json.load(f)
                    self._launch(data.get("name", name), path,
                                data["canvasWidth"], data["canvasHeight"], loadData=data)
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            deleteBtn = tk.Label(card, text="✕", bg=C["panel"], fg=C["danger"],
                                 font=FONT_BOLD, cursor="hand2", width=2)
            deleteBtn.pack(side="right", padx=8, pady=8)

            def deleteIt(event=None):
                if messagebox.askyesno("Delete Project",
                    f"Delete project '{name}' and all its files? This cannot be undone."):
                    try:
                        import shutil
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        self._loadRecent()
                    except Exception as exc:
                        messagebox.showerror("Error", str(exc))
                return "break"

            deleteBtn.bind("<Button-1>", deleteIt)
            for w_ in [card] + card.winfo_children() + info.winfo_children():
                if w_ is deleteBtn:
                    continue
                try:
                    w_.bind("<Button-1>", openIt)
                    w_.bind("<Enter>", lambda e, c=card: c.config(bg=C["hover"]))
                    w_.bind("<Leave>", lambda e, c=card: c.config(bg=C["panel"]))
                except Exception:
                    pass

        def _launch(self, name, path, w, h, loadData=None):
            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.geometry("1400x900")
            self.root.state("zoomed")
            DrawingApp(self.root, name, path, w, h, loadData=loadData)


# ──────────────────────────────────────────────────────────────
# DRAWING APP
# ──────────────────────────────────────────────────────────────
class DrawingApp:
        # Global Render Mode Presets: maps render mode to (drawQuality, filter, ssaa_label)
        # All tools will automatically use these settings when a render mode is selected
        RENDER_MODES = {
            "fast":     {"quality": 1,  "desc": "Fast (1x SSAA)"},
            "normal":   {"quality": 2,  "desc": "Normal (2x SSAA)"},
            "high":     {"quality": 4,  "desc": "High (4x SSAA)"},
            "ultra":    {"quality": 12, "desc": "Ultra (12x SSAA)"},
        }

        def __init__(self, root, name, path, cw, ch, loadData=None):
            self.root        = root
            self.projectName = name
            self.projectPath = path
            self.CW, self.CH = cw, ch
            # Persistent internal undo cache: cache/<project>/undo_000..255.
            # This lives outside the project data so it is safe to treat as a
            # disposable working cache while keeping each project's steps separate.
            cache_name = re.sub(r'[^A-Za-z0-9._-]+', '_', os.path.basename(path) or name).strip('._') or "project"
            self.undoCacheDir = os.path.join(CACHE_DIR, cache_name)
            os.makedirs(self.undoCacheDir, exist_ok=True)
            self._undoCacheSlot = 0

            # Background layer dengan putih
            bgLayer = Layer("Background", cw, ch)
            # The canvas composite already supplies a white base.  Keeping this
            # layer transparent lets a reference beneath drawn lines stay visible.
            bgLayer.image = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            bgLayer.draw = ImageDraw.Draw(bgLayer.image)
            self.layers = [bgLayer]
            self.activeIdx = 0
            self.timelapseDisabledLayers = set()
            self.timelapseDisabledLayerNames = set()
            self._timelapseDisableArmed = False
            self.strokeHistory  = []
            self.currentStroke  = []
            self.startTime      = 0.0
            # Vector strokes are immutable once recorded, so their smoothed
            # polylines can be cached instead of rebuilt on every render.
            self._smoothCache   = {}

            self.brushColor   = "#1a1a1a"
            self.brushSize    = 12
            self.brushOpacity = 255
            self.brushHardness = 100
            self.tool         = "brush"
            self.strokeRenderer = "brush"  # brush | pencil | vector_pen; Shapes inherit this
            self.customBrushes = []
            self.symmetry     = False

            self.lastX = self.lastY = None
            self.isPlaying  = False
            self.playSpeed  = 2.0

            self.undoStack  = []
            self.redoStack  = []

            self.zoom    = 1.0
            self.offsetX = None
            self.offsetY = None
            self._px     = 0
            self._py     = 0
            self.autoSaveId = None
            self.autoSaveId = None
            self.zoomLbl = None
            self.coordLbl = None

            self.stabilizerVal = 0  # Disable stabilizer untuk fix performa

            # Draw directly while dragging.  The final pass still repaints the
            # stroke at high quality, but this keeps the live stroke continuous.
            self.stabilizerMethod = "Real-time"
            self._smoothBufX = []
            self._smoothBufY = []
            
            self.fadeEnabled = False
            self.forceFade = False
            self.fadeStartPercent = 0
            self.fadeEndPercent = 0
            self.fadeShape = "Lancip"

            self.shapeMode = "free"
            self.shapeStartPoint = None
            self.polylinePoints = []
            self.bezierAnchorPoints = []
            self.shapeStartTime = 0.0
            self.dragSplinePoint = None
            
            self.rulerActive = False
            self.rulerAngle = 0.0
            self.rulerX = cw / 2
            self.rulerY = ch / 2
            self.rulerIsDragging = False


            # Frame settings
            self.frameEnabled = False
            self.frameStyle   = "Solid"
            self.frameColor   = "#e53935"
            self.frameSize    = 40

            self.strokeLbl = None

            self.previewX = None
            self.previewY = None
            self.selectionStart = None
            self.selectionRect = None
            self.selectedStrokeIndex = None
            self._selectionPayload = None
            self._selectionOriginRect = None
            self._selectionDragStart = None
            self.activeHandle = None

            # throttle rendering
            self._renderPending = False
            self._qualityAfterId = None
            self._lastRender    = 0

            # draw & render quality (configurable via View menu)
            # Keep the drawing surface crisp by default.  Rendering may still use a
            # cheaper filter while the pointer is moving, but the pixels written to
            # a layer are always produced at high resolution first.
            self.drawQuality = 4      # 1–12 supersample factor for new strokes
            # pixel | fast | balanced | high | ultra.  This setting only affects
            # presentation; it cannot invent new source pixels after extreme zoom.
            self.renderQuality = "ultra"
            self.onePixelMode = "crisp"  # 1px strokes stay sharp and do not blur
            self._playbackLayers = None  # temporary layers used only by timelapse
            # composite cache — skip layer compositing during zoom/pan
            self._cacheDirty       = True
            self._cachedComposite  = None
            self._strokeBaseImage  = None

            if loadData:
                self._loadData(loadData)
                self._makeBackgroundWhiteTransparent()
            self._restoreUndoCache()
            # Disk cache is kept as a recovery artifact and is restored into the
            # live Undo stack on startup.  A circular cache cannot reliably
            # distinguish discarded Redo states after a new edit, which made
            # Undo order wrong.

            self._buildUI()
            self.root.protocol("WM_DELETE_WINDOW", self._closeProjectWindow)
            self.root.after(120, self._centerCanvas)
            self._save(showPopup=False)

        def _loadData(self, d):
            self.layers        = [Layer.fromDict(ld, self.CW, self.CH) for ld in d["layers"]]
            self.strokeHistory = d.get("strokeHistory", [])
            self.activeIdx     = d.get("activeLayerIdx", 0)
            self.timelapseDisabledLayers = set(d.get("timelapseDisabledLayers", []))
            self.timelapseDisabledLayerNames = set(d.get("timelapseDisabledLayerNames", []))
            self.renderQuality = d.get("renderQuality", "ultra")
            if self.renderQuality not in self.RENDER_MODES:
                self.renderQuality = "ultra"
            # Draw quality is now automatically set based on render mode
            self.drawQuality = self.RENDER_MODES[self.renderQuality]["quality"]
            self.onePixelMode = d.get("onePixelMode", "crisp")
            if self.onePixelMode not in ("smooth", "crisp"):
                self.onePixelMode = "crisp"
            self.stabilizerVal = max(0, min(10, int(d.get("stabilizerVal", self.stabilizerVal))))
            self.stabilizerMethod = d.get("stabilizerMethod", self.stabilizerMethod)
            if self.stabilizerMethod not in ("Real-time", "Before-After"):
                self.stabilizerMethod = "Real-time"
            self.fadeEnabled = bool(d.get("fadeEnabled", self.fadeEnabled))
            self.forceFade = bool(d.get("forceFade", self.forceFade))
            if self.fadeEnabled:
                self.forceFade = False
            self.fadeStartPercent = max(0, min(100, int(d.get("fadeStartPercent", self.fadeStartPercent))))
            self.fadeEndPercent = max(0, min(100, int(d.get("fadeEndPercent", self.fadeEndPercent))))
            self.fadeShape = d.get("fadeShape", self.fadeShape)
            if self.fadeShape not in ("Lancip", "Halus agak lancip"):
                self.fadeShape = "Lancip"
            self.customBrushes = d.get("customBrushes", [])[:20]

            # Lanjutkan timeline waktu agar coretan baru nyambung ke sesi sebelumnya
            max_t = 0.0
            for stroke in self.strokeHistory:
                if stroke:
                    for pt in stroke:
                        if isinstance(pt, dict) and "t" in pt:
                            max_t = max(max_t, float(pt["t"]))
            self.startTime = time.time() - max_t

        def _makeBackgroundWhiteTransparent(self):
            """Migrate old opaque-white Background layers without deleting ink."""
            for layer in self.layers:
                if layer.name.lower() != "background":
                    continue
                pixels = list(layer.image.getdata())
                if not any(a and r > 250 and g > 250 and b > 250 for r, g, b, a in pixels):
                    continue
                layer.image.putdata([(r, g, b, 0) if a and r > 250 and g > 250 and b > 250
                                    else (r, g, b, a) for r, g, b, a in pixels])
                layer.draw = ImageDraw.Draw(layer.image)

        # * Inisialisasi komponen UI utama aplikasi
        def _buildUI(self):
            self.root.title(f"2D Draw Studio  ·  {self.projectName}")
            self.root.configure(bg=C["bg"])
            
            # Menubar: packed at top (no gap)
            self._buildMenubar()
            
            # Content container: fills remaining space below menubar
            self.contentFrame = tk.Frame(self.root, bg=C["bg"])
            self.contentFrame.pack(side="top", fill="both", expand=True)
            self.contentFrame.grid_rowconfigure(0, weight=1)
            self.contentFrame.grid_columnconfigure(1, weight=1)
            self._buildToolbar()
            self._buildCanvas()
            self._buildRightPanel()
            self._startAutoSave()


        def _startAutoSave(self):
            if self.autoSaveId is not None:
                self.root.after_cancel(self.autoSaveId)
            self.autoSaveId = self.root.after(60000, self._doAutoSave)
        
        def _doAutoSave(self):
            try:
                self._save(showPopup=False)
            except:
                pass
            self.autoSaveId = self.root.after(60000, self._doAutoSave)

        def _closeProjectWindow(self):
            """Persist stroke history before a normal window close."""
            try:
                self._save(showPopup=False)
            finally:
                self.root.destroy()
        
        # * Menu bar — File, Edit, View, Tools, Help
        def _buildMenubar(self):
            self._menu_dds = []  # keep refs to dropdowns
            mb = tk.Frame(self.root, bg=C["panel"], height=28)
            mb.pack(side="top", fill="x")
            mb.pack_propagate(False)
            
            def make_menu(text, items_fn):
                """Create a menu label that shows a dropdown."""
                btn = tk.Label(mb, text=text + "  \u25bc", bg=C["panel"], fg=C["text"],
                            font=("Segoe UI", 9), cursor="hand2", padx=10, pady=2)
                btn.pack(side="left")
                
                dd = tk.Frame(self.root, bg=C["card"], bd=0,
                            highlightbackground=C["border"], highlightthickness=1)
                self._menu_dds.append(dd)
                
                def rebuild_and_show():
                    """Rebuild dropdown items with fresh state, then show."""
                    # Clear old items
                    for w in dd.winfo_children():
                        w.destroy()
                    
                    items = items_fn()  # fresh state each time!
                    for label, cmd, enabled in items:
                        if label == "---":
                            tk.Frame(dd, bg=C["border"], height=1).pack(fill="x", pady=2)
                            continue
                        fg = C["text"] if enabled else C["muted"]
                        curs = "hand2" if enabled else "arrow"
                        item = tk.Label(dd, text="  " + label, bg=C["card"], fg=fg,
                                    font=("Segoe UI", 9), cursor=curs,
                                    anchor="w", padx=10, pady=3)
                        item.pack(fill="x")
                        if enabled:
                            item.bind("<Enter>", lambda e, w=item: w.config(bg=C["hover"]))
                            item.bind("<Leave>", lambda e, w=item: w.config(bg=C["card"]))
                            item.bind("<Button-1>", lambda e, cb=cmd: [cb(), dd.place_forget()])
                    
                    # Position and show
                    x = btn.winfo_rootx() - self.root.winfo_rootx()
                    y = btn.winfo_rooty() - self.root.winfo_rooty() + btn.winfo_height()
                    dd.place(x=x, y=y, width=210)
                    dd.lift()
                
                btn.bind("<Enter>", lambda e: btn.config(bg=C["hover"]))
                btn.bind("<Leave>", lambda e: btn.config(bg=C["panel"]))
                btn.bind("<Button-1>", lambda e: self.root.after_idle(rebuild_and_show))
                
                return btn
            
            # --- FILE ---
            make_menu("File", lambda: [
                ("New Project", self._goHome, True),
                ("---", None, True),
                ("Save", self._save, True),
                ("Delete Project", self._deleteProject, True),
                ("Export PNG", self._exportPNG, True),
                ("Import Image", self._importImageToLayer, True),
                ("---", None, True),
                ("Exit", self.root.quit, True),
            ])
            
            # --- EDIT ---
            make_menu("Edit", lambda: [
                ("Undo", self._undo, len(self.undoStack) > 0),
                ("Redo", self._redo, len(self.redoStack) > 0),
                ("---", None, True),
                ("Clear Canvas", self._clearCanvas, True),
            ])
            
            # --- VIEW ---
            make_menu("View", lambda: [
                ("Zoom In    (+)", lambda: self._zoom(1.25), True),
                ("Zoom Out   (-)", lambda: self._zoom(0.8), True),
                ("Reset Zoom (0)", self._resetZoom, True),
                ("Center Canvas", self._centerCanvas, True),
                ("---", None, True),
                ("Ruler", self._toggleRuler, True),
                ("Symmetry", self._toggleSym, True),
                ("Frame", self._toggleFrame, True),
                ("---", None, True),
                (f"Canvas  {self.CW} × {self.CH}", self._showResolutionDialog, True),
                ("Resolution Settings...", self._showResolutionDialog, True),
                ("---", None, True),
                (f"Render Mode: Fast (1x){'  ✓' if self.renderQuality == 'fast' else ''}",
                lambda: self._setRenderQuality("fast"), True),
                (f"Render Mode: Normal (2x){'  ✓' if self.renderQuality == 'normal' else ''}",
                lambda: self._setRenderQuality("normal"), True),
                (f"Render Mode: High (4x){'  ✓' if self.renderQuality == 'high' else ''}",
                lambda: self._setRenderQuality("high"), True),
                (f"Render Mode: Ultra (12x){'  ✓' if self.renderQuality == 'ultra' else ''}",
                lambda: self._setRenderQuality("ultra"), True),
            ])
            
            # --- TOOLS ---
            make_menu("Tools", lambda: [
                ("Brush",     lambda: self._setTool("brush"), self.tool != "brush"),
                ("Pencil",    lambda: self._setTool("pencil"), self.tool != "pencil"),
                ("Eraser",    lambda: self._setTool("eraser"), self.tool != "eraser"),
                ("Fill",      lambda: self._setTool("fill"), self.tool != "fill"),
                ("Eyedrop",   lambda: self._setTool("eyedrop"), self.tool != "eyedrop"),
                ("Smudge",    lambda: self._setTool("smudge"), self.tool != "smudge"),
                ("---", None, True),
                ("ℹ  Vector Pen auto-activates with High/Ultra render mode", None, False),
            ])
            
            # --- HELP ---
            make_menu("Help", lambda: [
                ("About 2D Draw Studio", self._showAbout, True),
            ])
            
            # Close any open dropdown on root click (non-accumulating)
            def close_menus(event):
                for dd in self._menu_dds:
                    try:
                        dd.place_forget()
                    except:
                        pass
            self.root.bind("<Button-1>", close_menus, "+")
            
            # Bottom accent line inside menubar
            tk.Frame(mb, bg=C["accent"], height=1).pack(side="bottom", fill="x")
        
        def _showAbout(self):
            import tkinter.messagebox
            tkinter.messagebox.showinfo("About", "2D Draw Studio v1.0\nPython + Tkinter + PIL")

        def _setDrawQuality(self, level):
            self.drawQuality = max(1, min(12, level))
            self._scheduleRender(fast=False)

        def _setRenderQuality(self, mode):
            """
            Sets global rendering mode, which automatically updates draw quality for all tools.
            Modes: fast (1x), normal (2x), high (4x), ultra (12x)
            
            Also auto-switches tool:
            - High/Ultra → Vector Pen (activated automatically)
            - Fast/Normal → Brush
            """
            if mode in self.RENDER_MODES:
                self.renderQuality = mode
                # Automatically update draw quality based on render mode
                self.drawQuality = self.RENDER_MODES[mode]["quality"]

                if mode in ("high", "ultra") and self.tool in ("brush", "pencil", "shape", "vector_pen"):
                    self.strokeRenderer = "vector_pen"
                elif mode not in ("high", "ultra") and self.tool in ("brush", "pencil"):
                    self.strokeRenderer = self.tool

                # Update status labels
                if hasattr(self, "qualityLabel"):
                    self.qualityLabel.config(text=self.RENDER_MODES[mode]["desc"])

                self._debugVectorState("_setRenderQuality")
                print(f"[Render Mode] {mode.upper()} - {self.RENDER_MODES[mode]['desc']}")
                self._scheduleRender(fast=False)
            else:
                print(f"[WARNING] Invalid render mode: {mode}")

        def _renderFilter(self, fast):
            # Use fast filter during interactions for responsiveness
            if fast:
                return Image.BILINEAR
            
            # Use quality-appropriate filter based on render mode
            if self.renderQuality == "ultra":
                return Image.LANCZOS
            elif self.renderQuality == "high":
                return Image.BICUBIC
            elif self.renderQuality == "normal":
                return Image.BICUBIC
            elif self.renderQuality == "fast":
                return Image.BILINEAR
            return Image.LANCZOS

        def _showResolutionDialog(self):
            dlg = tk.Toplevel(self.root)
            dlg.title("Resolution Settings")
            dlg.configure(bg=C["panel"])
            dlg.resizable(False, False)
            dlg.transient(self.root)
            dlg.grab_set()

            pad = {"padx": 16, "pady": 6}
            tk.Label(dlg, text="Canvas Size", bg=C["panel"], fg=C["accent"],
                    font=FONT_BOLD).grid(row=0, column=0, columnspan=2, sticky="w", **pad)

            sizeRow = tk.Frame(dlg, bg=C["panel"])
            sizeRow.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16)
            wVar = tk.IntVar(value=self.CW)
            hVar = tk.IntVar(value=self.CH)
            tk.Label(sizeRow, text="W", bg=C["panel"], fg=C["dim"], font=FONT_SM).pack(side="left")
            wEntry = tk.Entry(sizeRow, textvariable=wVar, width=8, bg=C["card"], fg=C["text"],
                            insertbackground=C["text"], relief="flat")
            wEntry.pack(side="left", padx=(4, 12))
            tk.Label(sizeRow, text="H", bg=C["panel"], fg=C["dim"], font=FONT_SM).pack(side="left")
            hEntry = tk.Entry(sizeRow, textvariable=hVar, width=8, bg=C["card"], fg=C["text"],
                            insertbackground=C["text"], relief="flat")
            hEntry.pack(side="left", padx=4)

            presetRow = tk.Frame(dlg, bg=C["panel"])
            presetRow.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 8))
            tk.Label(presetRow, text="Preset:", bg=C["panel"], fg=C["dim"], font=FONT_SM).pack(side="left")
            presetVar = tk.StringVar(value="Custom")
            presetMenu = ttk.Combobox(presetRow, textvariable=presetVar, state="readonly", width=18)
            presetLabels = []
            presetMap = {}
            for p in CANVAS_PRESETS:
                if p["w"] and p["h"]:
                    label = f"{p['label']} ({p['w']}×{p['h']})"
                    presetLabels.append(label)
                    presetMap[label] = (p["w"], p["h"])
            presetMenu["values"] = presetLabels
            presetMenu.pack(side="left", padx=8)

            def onPreset(_=None):
                sel = presetMap.get(presetVar.get())
                if sel:
                    wVar.set(sel[0])
                    hVar.set(sel[1])
            presetMenu.bind("<<ComboboxSelected>>", onPreset)

            tk.Frame(dlg, bg=C["border"], height=1).grid(row=3, column=0, columnspan=2, sticky="ew", padx=16, pady=8)

            tk.Label(dlg, text="Draw Quality", bg=C["panel"], fg=C["accent"],
                    font=FONT_BOLD).grid(row=4, column=0, columnspan=2, sticky="w", **pad)
            tk.Label(dlg, text="Global render mode affects all tools: Brush, Pencil, Vector Pen, Eraser, Shape, Smudge, Fill & Zoom",
                    bg=C["panel"], fg=C["dim"], font=FONT_XS).grid(row=5, column=0, columnspan=2, sticky="w", padx=16)

            renderVar = tk.StringVar(value=self.renderQuality)
            renderRow = tk.Frame(dlg, bg=C["panel"])
            renderRow.grid(row=6, column=0, columnspan=2, sticky="w", padx=16, pady=4)
            for val, lbl in [("fast", "🚀 Fast (1x)"), ("normal", "⚡ Normal (2x)"), 
                            ("high", "🎨 High (4x)"), ("ultra", "✨ Ultra (12x)")]:
                tk.Radiobutton(renderRow, text=lbl, variable=renderVar, value=val,
                            bg=C["panel"], fg=C["text"], selectcolor=C["card"],
                            activebackground=C["panel"], activeforeground=C["accent"],
                            font=FONT_SM).pack(side="left", padx=(0, 10))

            btnRow = tk.Frame(dlg, bg=C["panel"])
            btnRow.grid(row=7, column=0, columnspan=2, pady=16)
            def apply():
                try:
                    nw = max(100, min(8192, int(wVar.get())))
                    nh = max(100, min(8192, int(hVar.get())))
                except tk.TclError:
                    messagebox.showerror("Invalid", "Canvas size must be numbers.", parent=dlg)
                    return
                if nw != self.CW or nh != self.CH:
                    if not messagebox.askyesno(
                        "Resize Canvas",
                        f"Ubah canvas dari {self.CW}×{self.CH} ke {nw}×{nh}?\n"
                        "Semua layer akan di-scale ke ukuran baru.",
                        parent=dlg,
                    ):
                        return
                    self._resizeCanvas(nw, nh)
                # Update render mode and automatically set draw quality
                newRenderMode = renderVar.get()
                if newRenderMode in self.RENDER_MODES:
                    self.renderQuality = newRenderMode
                    self.drawQuality = self.RENDER_MODES[newRenderMode]["quality"]
                    print(f"[Settings] Render Mode: {newRenderMode.upper()} → Draw Quality: {self.drawQuality}x")
                self._cacheDirty = True
                self._scheduleRender(fast=False)
                dlg.destroy()

            flatBtn(btnRow, "Cancel", dlg.destroy, padx=12, pady=6).pack(side="left", padx=6)
            flatBtn(btnRow, "Apply", apply, bg=C["accent"], fg="#fff", padx=12, pady=6).pack(side="left", padx=6)

            dlg.update_idletasks()
            rx = self.root.winfo_rootx() + (self.root.winfo_width() - dlg.winfo_width()) // 2
            ry = self.root.winfo_rooty() + (self.root.winfo_height() - dlg.winfo_height()) // 2
            dlg.geometry(f"+{rx}+{ry}")

        def _resizeCanvas(self, new_w, new_h):
            # Index 0 is the top-most layer in the UI; composite bottom-to-top.
            for layer in reversed(self.layers):
                layer.image = layer.image.resize((new_w, new_h), Image.LANCZOS)
                layer.draw = ImageDraw.Draw(layer.image)
                layer.w, layer.h = new_w, new_h
            self.CW, self.CH = new_w, new_h
            self.rulerX = min(self.rulerX, new_w - 1)
            self.rulerY = min(self.rulerY, new_h - 1)
            self._cacheDirty = True
            self.root.title(f"2D Draw Studio  ·  {self.projectName}")
            self._scheduleRender(fast=False)
        
        def _zoom(self, factor):
            self.zoom = max(0.1, min(10, self.zoom * factor))
            if self.zoomLbl:
                self.zoomLbl.config(text=f"{int(self.zoom * 100)}%")
            self._scheduleRender(fast=False)
        
        def _resetZoom(self):
            self._centerCanvas()
        
        # * Membuat toolbar panel alat di sebelah kiri layar dengan popout compact
        def _buildToolbar(self):
            self._tbFrame = tk.Frame(self.contentFrame, bg=C["panel"], width=64)
            self._tbFrame.grid(row=0, column=0, sticky="nsew")
            self._tbFrame.grid_propagate(False)
            tb = self._tbFrame

            self.toolVar   = tk.StringVar(value="brush")
            self._popout   = None
            self._popoutId = None

            tools = [
                ("✏",  "brush",   "Brush"),
                ("✒",  "pencil",  "Pencil"),
                ("◌",  "eraser",  "Eraser"),
                ("■",  "fill",    "Fill"),
                ("⊙",  "eyedrop", "Eyedrop"),
                ("~",  "smudge",  "Smudge"),
            ]

            tk.Label(tb, text="TOOLS", bg=C["panel"], fg=C["dim"],
                    font=("Segoe UI", 7, "bold"), pady=8).pack(fill="x")
            tk.Frame(tb, bg=C["border"], height=1).pack(fill="x", padx=8, pady=(0, 5))
            for icon, mode, tip in tools:
                self._toolBtn(tb, icon, mode, tip)

            self._toolBtn(tb, "▣", "select", "Select: click a stroke or drag an area")

            tk.Frame(tb, bg=C["border"], height=1).pack(fill="x", pady=(6, 2))

            # Tombol Shape — toggle popout shapes
            self.shapeTabBtn = tk.Label(tb, text="⬡", bg=C["panel"], fg=C["dim"],
                                        font=("Segoe UI Symbol", 13), cursor="hand2",
                                        pady=6, width=4)
            self.shapeTabBtn.pack(fill="x", pady=1)
            self.shapeTabBtn.bind("<Button-1>", lambda e: self._togglePopout("shape"))
            self._makeTooltip(self.shapeTabBtn, "Shapes")

            # Tombol Stabilizer — toggle popout stabilizer
            self.stabTabBtn = tk.Label(tb, text="≋", bg=C["panel"], fg=C["dim"],
                                    font=("Segoe UI", 13), cursor="hand2",
                                    pady=6, width=4)
            self.stabTabBtn.pack(fill="x", pady=1)
            self.stabTabBtn.bind("<Button-1>", lambda e: self._togglePopout("stab"))
            self._makeTooltip(self.stabTabBtn, "Stabilizer & Fade")

            tk.Frame(tb, bg=C["border"], height=1).pack(fill="x", pady=6)

            # color dot
            self.colorDot = tk.Label(tb, bg=self.brushColor, width=2, height=1,
                                    cursor="hand2", bd=2, relief="groove")
            self.colorDot.pack(pady=4, padx=8, fill="x")
            self.colorDot.bind("<Button-1>", lambda e: self._pickColor())

            # symmetry
            self.symBtn = tk.Label(tb, text="⇄", bg=C["panel"], fg=C["dim"],
                                    font=("Segoe UI", 12), cursor="hand2", pady=4)
            self.symBtn.pack(fill="x", pady=(4,0))
            self.symBtn.bind("<Button-1>", lambda e: self._toggleSym())
            self._makeTooltip(self.symBtn, "Symmetry")

        # * Toggle tampilkan/sembunyikan popout panel compact di toolbar kiri
        def _togglePopout(self, panelId):
            if self._popout and self._popoutId == panelId:
                self._closePopout()
                return
            self._closePopout()
            self._popoutId = panelId
            self._openPopout(panelId)

        def _closePopout(self):
            if self._popout:
                self._popout.destroy()
                self._popout = None
            self._popoutId = None
            if hasattr(self, 'shapeTabBtn'):
                self.shapeTabBtn.config(bg=C["panel"], fg=C["dim"])
            if hasattr(self, 'stabTabBtn'):
                self.stabTabBtn.config(bg=C["panel"], fg=C["dim"])

        # * Membuka popout compact panel di sebelah kanan toolbar
        def _openPopout(self, panelId):
            container = self.tkCanvas.master
            pop = tk.Frame(container, bg=C["panel"], width=200,
                        highlightthickness=1, highlightbackground=C["border"])
            # Keep the popover clear of the floating Undo/Redo controls.
            pop.place(x=72, y=16, anchor="nw")
            pop.lift()
            self._popout = pop

            if panelId == "shape":
                self.shapeTabBtn.config(bg=C["accent"], fg="#fff")
                self._buildShapePopout(pop)
            elif panelId == "stab":
                self.stabTabBtn.config(bg=C["accent"], fg="#fff")
                self._buildStabPopout(pop)

            # tutup kalau klik di luar popout
            self.tkCanvas.bind("<Button-1>", self._onCanvasClickClosePopout, add="+")

        def _onCanvasClickClosePopout(self, event):
            self._closePopout()
            self._popoutOpen = False

        # * Membangun isi popout panel Stabilizer & Fade
        def _buildStabPopout(self, p):
            def lbl(parent, txt, bold=False):
                f = ("Segoe UI", 8, "bold") if bold else FONT_SM
                tk.Label(parent, text=txt, bg=C["panel"], fg=C["accent"] if bold else C["dim"],
                        font=f, anchor="w").pack(fill="x", padx=10, pady=(8, 1) if bold else (0, 0))

            def closer():
                self._closePopout()

            hdr = tk.Frame(p, bg=C["panel"])
            hdr.pack(fill="x", padx=8, pady=(8, 4))
            tk.Label(hdr, text="STABILIZER", bg=C["panel"], fg=C["accent"],
                    font=("Segoe UI", 8, "bold")).pack(side="left")
            tk.Button(hdr, text="x", command=closer, bg=C["panel"], fg=C["dim"],
                    bd=0, relief="flat", cursor="hand2", font=FONT_SM).pack(side="right")

            tk.Frame(p, bg=C["border"], height=1).pack(fill="x", padx=8)

            # slider stabilizer
            self.stabilizerVar = tk.IntVar(value=self.stabilizerVal)
            self._popoutSliderRow(p, "Stabilizer", self.stabilizerVar, 0, 10,
                                self._setStabilizerVal)

            # method dropdown
            mRow = tk.Frame(p, bg=C["panel"])
            mRow.pack(fill="x", padx=10, pady=2)
            tk.Label(mRow, text="Method", bg=C["panel"], fg=C["dim"],
                    font=FONT_SM, width=8, anchor="w").pack(side="left")
            self.stabilizerMethodVar = tk.StringVar(value=self.stabilizerMethod)
            om = ttk.OptionMenu(mRow, self.stabilizerMethodVar, self.stabilizerMethod,
                                "Real-time", "Before-After",
                                command=lambda v: setattr(self, "stabilizerMethod", v))
            om.configure(width=10)
            om.pack(side="left", fill="x", expand=True)

            tk.Frame(p, bg=C["border"], height=1).pack(fill="x", padx=8, pady=(6, 2))

            # Fade choices are mutually exclusive: off, normal fade, or force fade.
            chkRow = tk.Frame(p, bg=C["panel"])
            chkRow.pack(fill="x", padx=10, pady=2)
            self.fadeModeVar = tk.StringVar(value="force" if self.forceFade else "fade" if self.fadeEnabled else "off")
            for value, label in (("off", "Off"), ("fade", "Fade"), ("force", "Force")):
                tk.Radiobutton(chkRow, text=label, variable=self.fadeModeVar, value=value,
                            command=lambda v=value: self._setFadeMode(v), bg=C["panel"],
                            fg=C["text"], selectcolor=C["card"], activebackground=C["panel"],
                            activeforeground=C["accent"], font=FONT_SM).pack(side="left", padx=(0, 5))

            self.fadeStartVar = tk.IntVar(value=self.fadeStartPercent)
            self.fadeStartScale = self._popoutSliderRow(p, "Awal %", self.fadeStartVar, 0, 100,
                                                        lambda v: setattr(self, "fadeStartPercent", int(float(v))))

            self.fadeEndVar = tk.IntVar(value=self.fadeEndPercent)
            self.fadeEndScale = self._popoutSliderRow(p, "Akhir %", self.fadeEndVar, 0, 100,
                                                    lambda v: setattr(self, "fadeEndPercent", int(float(v))))

            # fade type
            fRow = tk.Frame(p, bg=C["panel"])
            fRow.pack(fill="x", padx=10, pady=(2, 8))
            tk.Label(fRow, text="Bentuk", bg=C["panel"], fg=C["dim"],
                    font=FONT_SM, width=8, anchor="w").pack(side="left")
            self.fadeShapeBtns = []
            for value, icon in (("Lancip", "◢"), ("Halus agak lancip", "◣")):
                btn = tk.Button(fRow, text=icon, command=lambda v=value: self._setFadeShape(v),
                                bg=C["accent"] if self.fadeShape == value else C["card"],
                                fg="#fff" if self.fadeShape == value else C["text"], bd=0,
                                relief="flat", cursor="hand2", font=("Segoe UI Symbol", 14), width=4)
                btn.pack(side="left", padx=3)
                self.fadeShapeBtns.append((value, btn))
            self._updateFadeControls()

        # * Membangun isi popout panel Shapes
        def _buildShapePopout(self, p):
            def closer():
                self._closePopout()

            hdr = tk.Frame(p, bg=C["panel"])
            hdr.pack(fill="x", padx=8, pady=(8, 4))
            tk.Label(hdr, text="SHAPES", bg=C["panel"], fg=C["accent"],
                    font=("Segoe UI", 8, "bold")).pack(side="left")
            tk.Button(hdr, text="x", command=closer, bg=C["panel"], fg=C["dim"],
                    bd=0, relief="flat", cursor="hand2", font=FONT_SM).pack(side="right")

            tk.Frame(p, bg=C["border"], height=1).pack(fill="x", padx=8)

            gridFrame = tk.Frame(p, bg=C["panel"])
            gridFrame.pack(fill="x", padx=8, pady=6)

            shapes = [
                ("line",         "Line"),
                ("rect",         "Rectangle"),
                ("circle",       "Circle"),
                ("hexagon",      "Hexagon"),
                ("arrow",        "Arrow"),
                ("oval",         "Oval"),
                ("rounded_rect", "Rounded rectangle"),
                ("bezier",       "Spline"),
                ("polyline",     "Polyline"),
                ("bubble",       "Speech bubble"),
            ]

            def draw_icon(icon, mode, selected):
                """Draw the actual geometric shape, not a text-only label."""
                bg = C["accent"] if selected else C["card"]
                fg = "#ffffff" if selected else C["text"]
                icon.configure(bg=bg, highlightbackground=C["accent"] if selected else C["border"])
                icon.delete("all")
                if mode == "line":
                    icon.create_line(15, 35, 67, 15, fill=fg, width=3)
                elif mode == "rect":
                    icon.create_rectangle(17, 13, 65, 37, outline=fg, width=2)
                elif mode == "circle":
                    icon.create_oval(25, 11, 57, 43, outline=fg, width=2)
                elif mode == "hexagon":
                    icon.create_polygon(27, 11, 55, 11, 69, 25, 55, 39, 27, 39, 13, 25,
                                        outline=fg, fill="", width=2)
                elif mode == "arrow":
                    icon.create_line(14, 25, 65, 25, fill=fg, width=3)
                    icon.create_line(51, 12, 66, 25, 51, 38, fill=fg, width=3)
                elif mode == "oval":
                    icon.create_oval(16, 15, 66, 35, outline=fg, width=2)
                elif mode == "rounded_rect":
                    icon.create_rectangle(16, 13, 66, 37, outline=fg, width=2)
                    icon.create_oval(16, 13, 28, 25, outline=fg, width=2)
                    icon.create_oval(54, 25, 66, 37, outline=fg, width=2)
                elif mode == "bezier":
                    icon.create_line(13, 35, 28, 13, 48, 40, 68, 14,
                                    fill=fg, width=3, smooth=True)
                elif mode == "polyline":
                    icon.create_line(13, 35, 29, 14, 46, 34, 68, 13, fill=fg, width=3)
                elif mode == "bubble":
                    icon.create_oval(15, 11, 67, 35, outline=fg, width=2)
                    icon.create_line(31, 32, 25, 43, 42, 35, fill=fg, width=2)

            self.shapeBtns = {}
            for i, (mode, tooltip) in enumerate(shapes):
                selected = self.shapeMode == mode
                icon = tk.Canvas(gridFrame, width=80, height=48, bg=C["card"], bd=0,
                                highlightthickness=1, cursor="hand2")
                draw_icon(icon, mode, selected)
                icon.grid(row=i // 2, column=i % 2, padx=3, pady=3, sticky="ew")
                icon.bind("<Button-1>", lambda e, m=mode: self._setShapeModePopout(m))
                icon.bind("<Enter>", lambda e, w=icon: w.config(highlightbackground=C["accent"]))
                icon.bind("<Leave>", lambda e, w=icon, m=mode: w.config(
                    highlightbackground=C["accent"] if self.shapeMode == m else C["border"]))
                self._makeTooltip(icon, tooltip)
                self.shapeBtns[mode] = icon

            for c in range(2):
                gridFrame.grid_columnconfigure(c, weight=1)

        def _setShapeModePopout(self, mode):
            self.shapeMode = mode
            self._setTool("shape")
            self.polylinePoints.clear()
            self.bezierAnchorPoints.clear()
            for m, btn in self.shapeBtns.items():
                btn.config(bg=C["accent"] if m == mode else C["card"])
            self._closePopout()
            self._scheduleRender(fast=False)

        # * Helper slider compact untuk popout panel
        def _popoutSliderRow(self, parent, label, var, mn, mx, cmd, res=1):
            row = tk.Frame(parent, bg=C["panel"])
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=label, bg=C["panel"], fg=C["dim"],
                    font=FONT_SM, width=8, anchor="w").pack(side="left")
            sl = tk.Scale(row, variable=var, from_=mn, to=mx,
                        orient="horizontal", showvalue=True, resolution=res,
                        bg=C["panel"], fg=C["text"], troughcolor=C["card"],
                        highlightthickness=0, bd=0, sliderlength=10,
                        activebackground=C["accent"], font=FONT_SM,
                        command=cmd, length=90)
            sl.pack(side="left", fill="x", expand=True)
            return sl

        def _setFadeMode(self, mode):
            self.fadeEnabled = mode == "fade"
            self.forceFade = mode == "force"
            if hasattr(self, "fadeModeVar"):
                self.fadeModeVar.set(mode)
            self._updateFadeControls()

        def _setFadeShape(self, shape):
            self.fadeShape = shape
            for value, button in getattr(self, "fadeShapeBtns", []):
                selected = value == shape
                button.config(bg=C["accent"] if selected else C["card"],
                            fg="#fff" if selected else C["text"])

        def _updateFadeControls(self):
            enabled = self.fadeEnabled or self.forceFade
            state = "normal" if enabled else "disabled"
            for widget in (getattr(self, "fadeStartScale", None), getattr(self, "fadeEndScale", None)):
                if widget is not None:
                    widget.config(state=state)
            for _, button in getattr(self, "fadeShapeBtns", []):
                button.config(state=state)

        def _toolBtn(self, parent, icon, mode, tip):
            btn = tk.Radiobutton(
                parent, text=icon, variable=self.toolVar, value=mode,
                bg=C["panel"], fg=C["dim"],
                selectcolor=C["bg"],
                activebackground=C["panel"], activeforeground=C["text"],
                indicatoron=0, bd=0, width=4, height=2,
                font=("Segoe UI Symbol", 14), relief="flat", cursor="hand2",
                command=lambda m=mode: self._setTool(m)
            )
            btn.pack(pady=1, padx=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=C["text"], bg=C["hover"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(
                fg=C["accent"] if self.toolVar.get() == mode else C["dim"],
                bg=C["panel"]))
            self._makeTooltip(btn, tip)

        def _setTool(self, mode):
            """Switch tools and clear the temporary selection overlay."""
            if mode != "select":
                self.selectionStart = None
                self.selectionRect = None
                self.selectedStrokeIndex = None
                self._selectionPayload = None
                self._selectionOriginRect = None
                self._selectionDragStart = None
                self.activeHandle = None
            self.tool = mode
            if mode in ("brush", "pencil", "shape") and self.renderQuality in ("high", "ultra"):
                self.strokeRenderer = "vector_pen"
            elif mode in ("brush", "pencil", "vector_pen", "eraser", "smudge"):
                self.strokeRenderer = mode
            else:
                self.strokeRenderer = mode
            self.toolVar.set(mode)
            self._resetBrushPresetForTool(mode)
            if hasattr(self, "toolStatusLabel"):
                if self._usingVectorRenderer() and mode in ("brush", "pencil", "vector_pen", "shape"):
                    render_desc = self.RENDER_MODES[self.renderQuality]["desc"]
                    self.toolStatusLabel.config(
                        text=f"✦  Vector Pen ({render_desc})",
                        fg=C["accent"],
                    )
                else:
                    self.toolStatusLabel.config(
                        text=f"Tool: {mode.replace('_', ' ').title()}",
                        fg=C["dim"],
                    )
            self._resetBrushPresetForTool(mode)
            self._enforceVectorIfHighUltra(mode)
            self._debugVectorState("_setTool")
            self._scheduleRender(fast=False)

        def _usingVectorRenderer(self):
            if self.tool not in ("brush", "pencil", "vector_pen", "shape"):
                return False
            return self.strokeRenderer == "vector_pen" or self.renderQuality in ("high", "ultra")

        def _vectorizeStroke(self, stroke):
            if not stroke:
                return []
            first = stroke[0]
            if first.get("mode") == "eraser":
                return [pt.copy() for pt in stroke]
            if self.stabilizerVal > 0:
                smoothed = []
                window_size = min(self.stabilizerVal * 3, len(stroke))
                for i, pt in enumerate(stroke):
                    start = max(0, i - window_size + 1)
                    window = stroke[start:i+1]
                    sum_x = sum_y = total_weight = 0
                    n_w = len(window)
                    for j, w_pt in enumerate(window):
                        weight = math.pow((j + 1) / n_w, 0.5 + (10 - self.stabilizerVal) * 0.15)
                        sum_x += w_pt["x"] * weight
                        sum_y += w_pt["y"] * weight
                        total_weight += weight
                    new_pt = pt.copy()
                    new_pt["x"] = sum_x / total_weight
                    new_pt["y"] = sum_y / total_weight
                    smoothed.append(new_pt)
                stroke = smoothed

            pts = [(pt["x"], pt["y"]) for pt in stroke]
            if len(pts) <= 2:
                smooth_pts = pts
            else:
                smooth_pts = self._catmull_rom(pts, num_segments=24)
            return [{
                "x": x, "y": y,
                "color": first["color"],
                "size": first["size"],
                "opacity": first["opacity"],
                "mode": "vector_pen",
                "layer": first["layer"],
                "layer_name": first["layer_name"],
                "t": time.time() - self.startTime
            } for x, y in smooth_pts]

        def _enforceVectorIfHighUltra(self, mode=None):
            if self.renderQuality in ("high", "ultra") and mode in ("brush", "pencil", "shape"):
                self.strokeRenderer = "vector_pen"
            elif self.renderQuality not in ("high", "ultra") and mode in ("brush", "pencil"):
                self.strokeRenderer = mode

        def _resetBrushPresetForTool(self, mode):
            if mode in ("brush", "pencil") and hasattr(self, "brushPresetVar"):
                current = self.brushPresetVar.get()
                self._applyBrushPreset(current, applyTool=False)

        def _debugVectorState(self, context):
            state = self._usingVectorRenderer()

        def _handleUndoShortcut(self, event=None):
            """Undo a pending spline/polyline anchor before changing artwork."""
            if self.tool == "shape" and self.shapeMode == "bezier" and self.bezierAnchorPoints:
                self.bezierAnchorPoints.pop()
                self.previewX = self.previewY = None
                self._scheduleRender(fast=False)
                return "break"
            if self.tool == "shape" and self.shapeMode == "polyline" and self.polylinePoints:
                self.polylinePoints.pop()
                self.previewX = self.previewY = None
                self._scheduleRender(fast=False)
                return "break"
            self._undo()
            return "break"

        def _handleUndoOrTimelapseArm(self, event=None):
            """Windows often reports Ctrl+Shift+Z as Ctrl+Z with a Shift state."""
            if event is not None and (event.state & 0x0001):  # Shift modifier
                return self._armTimelapseLayerDisable(event)
            return self._handleUndoShortcut(event)

        # * Membuat container canvas utama beserta widget melayang di atasnya
        def _buildCanvas(self):
            container = tk.Frame(self.contentFrame, bg="#ffffff")
            container.grid(row=0, column=1, sticky="nsew")
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)

            self.tkCanvas = tk.Canvas(container, bg="#ffffff",
                                    cursor="crosshair", highlightthickness=0)
            self.tkCanvas.grid(row=0, column=0, sticky="nsew")

            # Floating Undo/Redo melayang di pojok kiri atas canvas
            self.floatingUndoRedo = tk.Frame(container, bg=C["panel"], bd=0, highlightthickness=1,
                                            highlightbackground=C["border"])
            self.floatingUndoRedo.place(x=16, y=16, anchor="nw")

            undoBtn = flatBtn(self.floatingUndoRedo, "  ↩", self._undo, padx=8, pady=5)
            undoBtn.configure(font=("Segoe UI", 9))
            undoBtn.pack(side="left", padx=1)

            sepFrame = tk.Frame(self.floatingUndoRedo, bg=C["border"], width=1, height=20)
            sepFrame.pack(side="left", padx=2)

            redoBtn = flatBtn(self.floatingUndoRedo, "  ↪", self._redo, padx=8, pady=5)
            redoBtn.configure(font=("Segoe UI", 9))
            redoBtn.pack(side="left", padx=1)

            # Info koordinat dan zoom melayang di pojok kanan bawah
            self.floatingInfo = tk.Frame(container, bg=C["panel"], bd=0, highlightthickness=1,
                                        highlightbackground=C["border"])
            self.floatingInfo.place(relx=1.0, rely=1.0, x=-16, y=-16, anchor="se")

            self.coordLbl = tk.Label(self.floatingInfo, text="0, 0", bg=C["panel"], fg=C["dim"], font=("Consolas", 9), padx=10, pady=5)
            self.coordLbl.pack(side="left")

            # Separator
            sepF = tk.Frame(self.floatingInfo, bg=C["border"], width=1, height=16)
            sepF.pack(side="left", padx=0)

            self.zoomLbl = tk.Label(self.floatingInfo, text="100%", bg=C["panel"],
                                    fg=C["text"], font=("Segoe UI", 9, "bold"),
                                    padx=10, pady=5)
            self.zoomLbl.pack(side="left")

            # Initialize mouse position tracking for cursor preview
            self.mouseX = 0
            self.mouseY = 0

            # Canvas input bindings.  Keep these on the drawing canvas itself so
            # the right control panel never steals a brush drag or zoom wheel.
            self.tkCanvas.bind("<ButtonPress-1>", self._onDown)
            self.tkCanvas.bind("<B1-Motion>", self._onMove)
            self.tkCanvas.bind("<ButtonRelease-1>", self._onUp)
            self.tkCanvas.bind("<ButtonPress-2>", self._panStart)
            self.tkCanvas.bind("<B2-Motion>", self._panMove)
            self.tkCanvas.bind("<ButtonPress-3>", self._panStart)
            self.tkCanvas.bind("<B3-Motion>", self._panMove)
            self.tkCanvas.bind("<MouseWheel>", self._onScroll)
            self.tkCanvas.bind("<Motion>", self._onHover)
            self.tkCanvas.bind("<Configure>", lambda e: self._scheduleRender())
            self.tkCanvas.bind("<Double-Button-1>", lambda e: self._finishShape())

            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind("<<Drop>>", self._handleDrop)
            self.root.bind("<Control-z>", self._handleUndoOrTimelapseArm)
            self.root.bind("<Control-Z>", self._handleUndoOrTimelapseArm)
            self.root.bind("<Control-y>", lambda e: self._redo())
            self.root.bind("<Control-s>", lambda e: self._save())
            self.root.bind("<bracketleft>", lambda e: self._changeBrushSize(-2))
            self.root.bind("<bracketright>", lambda e: self._changeBrushSize(2))
            self.root.bind("<Return>", lambda e: self._finishShape())
            self.root.bind("<Control-x>", self._handleTimelapseToggleShortcut)
            self.root.bind("<Control-X>", self._handleTimelapseToggleShortcut)
            
        # * Membuat panel kanan yang dapat di-scroll berisi semua kontrol tools
        def _buildRightPanel(self):
            panel = tk.Frame(self.contentFrame, bg=C["panel"], width=230)
            panel.grid(row=0, column=2, sticky="nsew")
            panel.grid_propagate(False)

            # scrollable inner
            rCanvas = tk.Canvas(panel, bg=C["panel"], highlightthickness=0, width=230)
            sb = tk.Scrollbar(panel, orient="vertical", command=rCanvas.yview,
                            bg=C["panel"], troughcolor=C["card"], bd=0,
                            highlightthickness=0, relief="flat", width=5)
            rCanvas.configure(yscrollcommand=sb.set)
            rCanvas.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")

            inner = tk.Frame(rCanvas, bg=C["panel"])
            winId = rCanvas.create_window((0, 0), window=inner, anchor="nw")
            inner.bind("<Configure>",
                lambda e: rCanvas.configure(scrollregion=rCanvas.bbox("all")))
            rCanvas.bind("<Configure>",
                lambda e: rCanvas.itemconfig(winId, width=e.width))
            rCanvas.bind("<MouseWheel>",
                lambda e: rCanvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
            inner.bind("<MouseWheel>",
                lambda e: rCanvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

            # header nama project
            hdr = tk.Frame(inner, bg=C["panel"])
            hdr.pack(fill="x", padx=12, pady=(16, 2))
            iconLbl = tk.Label(hdr, text="🎨", bg=C["panel"], fg=C["dim"],
                            font=("Segoe UI", 10))
            iconLbl.pack(side="left", padx=(0, 6))
            tk.Label(hdr, text=self.projectName, bg=C["panel"], fg=C["text"],
                    font=("Segoe UI", 11, "bold"), anchor="w",
                    wraplength=170).pack(side="left", anchor="w")

            status = tk.Frame(inner, bg=C["card"], highlightthickness=1,
                            highlightbackground=C["border"])
            status.pack(fill="x", padx=12, pady=(6, 4))
            tk.Label(status, text="AUTOSAVE ON", bg=C["card"], fg=C["success"],
                    font=("Segoe UI", 7, "bold"), padx=8, pady=5).pack(side="left")
            self.qualityLabel = tk.Label(status, text=f"{self.RENDER_MODES[self.renderQuality]['desc']}", bg=C["card"], fg=C["dim"],
                    font=("Segoe UI", 7, "bold"), padx=8, pady=5)
            self.qualityLabel.pack(side="right")

            # Project Actions
            actionFrame = tk.Frame(inner, bg=C["panel"])
            actionFrame.pack(fill="x", padx=12, pady=(4, 2))

            homeBtn = flatBtn(actionFrame, "Home", self._goHome, bg=C["card"], padx=8, pady=6, icon="◀")
            homeBtn.pack(side="left", padx=2)

            saveBtn = flatBtn(actionFrame, "Save", self._save, bg=C["accent"], fg="#fff", padx=10, pady=6)
            saveBtn.pack(side="right", padx=2)

            exportBtn = flatBtn(actionFrame, "Export", self._exportPNG, bg=C["card"], padx=8, pady=6, icon="⬇")
            exportBtn.pack(side="right", padx=2)

            self._buildBrushSection(inner)
            self._buildFrameSection(inner)
            self._buildRulerSection(inner)
            self._buildColorSection(inner)
            self._buildLayerSection(inner)
            self._buildTimelapseSection(inner)

            def scroll_panel(event):
                rCanvas.yview_scroll(int(-event.delta / 120), "units")
                return "break"
            def bind_scroll(widget):
                widget.bind("<MouseWheel>", scroll_panel, add="+")
                for child in widget.winfo_children():
                    bind_scroll(child)
            # Bind after every section exists so wheel works over sliders/buttons too.
            self.root.after_idle(lambda: bind_scroll(inner))

        def _buildBrushSection(self, p):
            sectionTitle(p, "BRUSH")

            self.toolStatusLabel = tk.Label(
                p, text="Tool: Brush", bg=C["panel"], fg=C["dim"], font=FONT_XS,
                anchor="w")
            self.toolStatusLabel.pack(fill="x", padx=12, pady=(0, 4))

            self.brushSizeVar = tk.IntVar(value=self.brushSize)
            self._sliderRow(p, "Size",     self.brushSizeVar, 1, 200,
                            lambda v: setattr(self, "brushSize", int(float(v))))
            self.opacityVar = tk.IntVar(value=100)
            self._sliderRow(p, "Opacity",  self.opacityVar,   1, 100,
                            lambda v: setattr(self, "brushOpacity", int(float(v) * 2.55)))
            self.hardVar = tk.IntVar(value=100)
            self._sliderRow(p, "Hardness", self.hardVar,      1, 100,
                            lambda v: setattr(self, "brushHardness", int(float(v))))

            tk.Label(p, text="BRUSH LIBRARY", bg=C["panel"], fg=C["accent"],
                    font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
            self.brushPresetVar = tk.StringVar(value="Ink")
            names = [item[0] for item in BRUSH_PRESETS] + [item.get("name", "Custom") for item in self.customBrushes]
            picker = ttk.Combobox(p, textvariable=self.brushPresetVar, values=names,
                                state="readonly", font=FONT_SM)
            self.brushPicker = picker
            picker.pack(fill="x", padx=12, pady=(0, 4))
            picker.bind("<<ComboboxSelected>>", lambda e: self._applyBrushPreset(self.brushPresetVar.get()))
            flatBtn(p, "Save Current as Custom", self._saveCustomBrush,
                    padx=8, pady=5, font=FONT_SM).pack(fill="x", padx=12, pady=(0, 4))

            icon_grid = tk.Frame(p, bg=C["panel"])
            icon_grid.pack(fill="x", padx=12, pady=(2, 6))
            for index, (name, size, hardness, opacity, mode) in enumerate(BRUSH_PRESETS):
                icon = tk.Canvas(icon_grid, width=24, height=24, bg=C["card"], bd=0,
                                highlightthickness=1, highlightbackground=C["border"], cursor="hand2")
                color = C["danger"] if mode == "eraser" else C["accent"]
                radius = max(3, min(10, int(size / 8)))
                if mode == "pencil":
                    icon.create_line(5, 19, 18, 6, fill=color, width=2)
                elif mode == "smudge":
                    icon.create_arc(5, 5, 19, 19, start=30, extent=280, outline=color, width=2)
                elif mode == "eraser":
                    icon.create_rectangle(7, 7, 17, 17, outline=color, width=2)
                else:
                    icon.create_oval(12-radius, 12-radius, 12+radius, 12+radius, fill=color, outline="")
                icon.grid(row=index // 8, column=index % 8, padx=1, pady=1)
                icon.bind("<Button-1>", lambda e, n=name: self._applyBrushPreset(n))
                self._makeTooltip(icon, name)

        def _applyBrushPreset(self, name, applyTool=True):
            preset = next((item for item in BRUSH_PRESETS if item[0] == name), None)
            if preset is None:
                custom = next((item for item in self.customBrushes if item.get("name") == name), None)
                if custom:
                    _, size, hardness, opacity, mode = (name, custom["size"], custom["hardness"],
                                                        custom["opacity"], custom["mode"])
                else:
                    return
            else:
                _, size, hardness, opacity, mode = preset
            self.brushSize, self.brushHardness = size, hardness
            self.brushOpacity = int(opacity * 2.55)
            if applyTool:
                self._setTool(mode)
            if hasattr(self, "brushSizeVar"): self.brushSizeVar.set(size)
            if hasattr(self, "hardVar"): self.hardVar.set(hardness)
            if hasattr(self, "opacityVar"): self.opacityVar.set(opacity)

        def _saveCustomBrush(self):
            name = simpledialog.askstring("Custom Brush", "Brush name:", parent=self.root)
            if not name:
                return
            self.customBrushes = [item for item in self.customBrushes if item.get("name") != name]
            self.customBrushes.append({"name": name, "size": self.brushSize,
                                    "hardness": self.brushHardness,
                                    "opacity": int(round(self.brushOpacity / 2.55)),
                                    "mode": self.tool})
            self.customBrushes = self.customBrushes[-20:]
            if hasattr(self, "brushPicker"):
                self.brushPicker["values"] = [item[0] for item in BRUSH_PRESETS] + [item["name"] for item in self.customBrushes]
            if hasattr(self, "brushPresetVar"):
                self.brushPresetVar.set(name)


        # * Membuat section ruler penggaris lurus di panel samping kanan
        def _buildRulerSection(self, p):
            sectionTitle(p, "RULER")
            row = tk.Frame(p, bg=C["panel"])
            row.pack(fill="x", padx=12, pady=4)
            
            self.rulerBtn = flatBtn(row, "Straight Ruler: OFF", self._toggleRuler, padx=10, pady=6)
            self.rulerBtn.pack(fill="x")
            
            self.rulerAngleVar = tk.DoubleVar(value=self.rulerAngle)
            self._sliderRow(p, "Ruler Angle", self.rulerAngleVar, 0, 180,
                            self._setRulerAngle, res=1)

        def _toggleRuler(self):
            self.rulerActive = not self.rulerActive
            self.rulerBtn.config(text="Straight Ruler: ON" if self.rulerActive else "Straight Ruler: OFF",
                                bg=C["accent"] if self.rulerActive else C["card"])
            self._scheduleRender(fast=False)

        def _setRulerAngle(self, val):
            self.rulerAngle = float(val)
            self._scheduleRender(fast=False)

        # -------- FRAME SECTION --------
        def _buildFrameSection(self, p):
            sectionTitle(p, "FRAME")
            row = tk.Frame(p, bg=C["panel"])
            row.pack(fill="x", padx=12, pady=4)
            self.frameBtn = flatBtn(row, "Frame: OFF", self._toggleFrame, padx=10, pady=6)
            self.frameBtn.pack(fill="x")

            # Style
            styleRow = tk.Frame(p, bg=C["panel"])
            styleRow.pack(fill="x", padx=12, pady=(8, 2))
            tk.Label(styleRow, text="Style", bg=C["panel"], fg=C["dim"],
                    font=("Segoe UI", 8)).pack(side="left", padx=(0, 8))
            self.frameStyleVar = tk.StringVar(value=self.frameStyle)
            styleOpt = tk.OptionMenu(styleRow, self.frameStyleVar,
                                    "Solid", "Double", "Polaroid", "Neon", "Dashed",
                                    command=self._setFrameStyle)
            styleOpt.config(bg=C["card"], fg=C["text"], bd=0, relief="flat",
                        highlightthickness=1, highlightbackground=C["border"],
                        activebackground=C["hover"], activeforeground=C["text"],
                        font=("Segoe UI", 8), padx=6, pady=2)
            styleOpt["menu"].config(bg=C["card"], fg=C["text"], bd=0,
                                activebackground=C["hover"], activeforeground=C["text"])
            styleOpt.pack(side="right", fill="x", expand=True, padx=(4, 0))

            # Size
            self.frameSizeVar = tk.IntVar(value=self.frameSize)
            self._sliderRow(p, "Border W", self.frameSizeVar, 10, 120, self._setFrameSize)

            # Color swatches
            fcRow = tk.Frame(p, bg=C["panel"])
            fcRow.pack(fill="x", padx=12, pady=(2, 8))
            fcolors = ["#e53935","#fb8c00","#fdd835","#43a047","#1e88e5",
                    "#8e24aa","#ffffff","#1a1a1a","#888888","#ff6d00"]
            for c in fcolors:
                sw = tk.Label(fcRow, bg=c, width=2, height=1, cursor="hand2",
                            bd=0, relief="flat",
                            highlightthickness=1, highlightbackground=C["border"])
                sw.pack(side="left", padx=2)
                sw.bind("<Button-1>", lambda e, co=c: self._setFrameColor(co))
                sw.bind("<Enter>", lambda e, w=sw: w.config(highlightbackground=C["accent"]))
                sw.bind("<Leave>", lambda e, w=sw: w.config(highlightbackground=C["border"]))

        def _toggleFrame(self):
            self.frameEnabled = not self.frameEnabled
            self.frameBtn.config(text="Frame: ON" if self.frameEnabled else "Frame: OFF",
                                bg=C["accent"] if self.frameEnabled else C["card"])
            self._scheduleRender(fast=False)

        def _setFrameStyle(self, val):
            self.frameStyle = val
            self._scheduleRender(fast=False)

        def _setFrameSize(self, val):
            self.frameSize = int(float(val))
            self._scheduleRender(fast=False)

        def _setFrameColor(self, color):
            self.frameColor = color
            self._scheduleRender(fast=False)

        def _drawFrame(self, canvas, ox, oy, sw, sh):
            if not self.frameEnabled:
                return
            fs = self.frameSize
            fc = self.frameColor
            style = self.frameStyle

            if style == "Solid":
                canvas.create_rectangle(ox-fs, oy-fs, ox+sw+fs, oy+sh+fs,
                                        outline=fc, width=fs)

            elif style == "Double":
                inner = max(3, fs // 5)
                gap = max(4, fs // 3)
                canvas.create_rectangle(ox-fs, oy-fs, ox+sw+fs, oy+sh+fs,
                                        outline=fc, width=fs)
                canvas.create_rectangle(ox-gap-inner, oy-gap-inner,
                                        ox+sw+gap+inner, oy+sh+gap+inner,
                                        outline=C["text"], width=inner)

            elif style == "Polaroid":
                pad = fs
                caption_h = pad // 2
                canvas.create_rectangle(ox-pad, oy-pad, ox+sw+pad, oy+sh+caption_h+pad,
                                        fill="#f5f4f0", outline=C["border"], width=1)
                shadow = max(2, pad // 8)
                canvas.create_rectangle(ox-pad+shadow, oy-pad+shadow,
                                        ox+sw+pad+shadow, oy+sh+caption_h+pad+shadow,
                                        outline="#555555", fill="#cccccc", stipple="gray25", width=0)

            elif style == "Neon":
                for i in range(3):
                    spread = fs * (0.2 + i * 0.4)
                    w = max(2, fs // (i + 1))
                    # Lighter outer layers for glow effect
                    r = int(fc[1:3], 16) if len(fc) >= 7 else 200
                    g = int(fc[3:5], 16) if len(fc) >= 7 else 200
                    b = int(fc[5:7], 16) if len(fc) >= 7 else 200
                    factor = 0.3 + 0.35 * i
                    r = min(255, int(r + (255 - r) * factor))
                    g = min(255, int(g + (255 - g) * factor))
                    b = min(255, int(b + (255 - b) * factor))
                    glow = f"#{r:02x}{g:02x}{b:02x}"
                    canvas.create_rectangle(ox-spread, oy-spread, ox+sw+spread, oy+sh+spread,
                                            outline=glow, width=w)

            elif style == "Dashed":
                canvas.create_rectangle(ox-fs//2, oy-fs//2, ox+sw+fs//2, oy+sh+fs//2,
                                        outline=fc, width=fs//2, dash=(8, 6))

        # * Membuat color picker dan swatches di panel samping kanan
        def _buildColorSection(self, p):
            sectionTitle(p, "COLOR")

            row = tk.Frame(p, bg=C["panel"])
            row.pack(fill="x", padx=12, pady=4)

            self.colorPreview = tk.Label(row, bg=self.brushColor, width=4, height=2,
                                        cursor="hand2", bd=0, relief="flat")
            self.colorPreview.pack(side="left", padx=(0, 10))
            self.colorPreview.bind("<Button-1>", lambda e: self._pickColor())

            self.hexEntry = tk.Entry(row, bg=C["card"], fg=C["text"],
                                    insertbackground=C["text"], bd=0, font=("Consolas", 10),
                                    width=10, relief="flat", highlightthickness=1,
                                    highlightcolor=C["accent"], highlightbackground=C["border"])
            self.hexEntry.pack(side="left", fill="x", expand=True, ipadx=6, ipady=4)
            self.hexEntry.insert(0, self.brushColor)
            self.hexEntry.bind("<Return>", lambda e: self._setColor(self.hexEntry.get()))

            # swatches
            sw = tk.Frame(p, bg=C["panel"])
            sw.pack(fill="x", padx=12, pady=4)
            swatches = [
                "#1a1a1a","#444444","#777777","#aaaaaa","#ffffff",
                "#e53935","#fb8c00","#fdd835","#43a047","#1e88e5",
                "#8e24aa","#00897b","#ff4081","#ff6d00","#64ffda",
                "#5c6bc0","#26c6da","#ffca28","#ff7043","#a1887f",
            ]
            for i, color in enumerate(swatches):
                s = tk.Label(sw, bg=color, width=2, height=1, cursor="hand2",
                            bd=0, relief="flat",
                            highlightthickness=1, highlightbackground=C["border"])
                s.grid(row=i//8, column=i%8, padx=2, pady=2)
                s.bind("<Button-1>", lambda e, c=color: self._setColor(c))
                # Hover effect
                s.bind("<Enter>", lambda e, w=s: w.config(highlightbackground=C["accent"]))
                s.bind("<Leave>", lambda e, w=s: w.config(highlightbackground=C["border"]))

        def _buildLayerSection(self, p):
            sectionTitle(p, "LAYERS")

            # Tombol aksi layer termasuk Import Image
            btnRow = tk.Frame(p, bg=C["panel"])
            btnRow.pack(fill="x", padx=12, pady=4)

            for label, cmd, ic in [("+", self._addLayer, ""), 
                            ("−", self._delLayer, ""),
                            ("↑", lambda: self._moveLayer(-1), ""),
                            ("↓", lambda: self._moveLayer(1), ""),
                            ("📁", self._importImageToLayer, "")]:
                flatBtn(btnRow, ic + label if ic else label, cmd, padx=4, pady=5, font=FONT_SM).pack(side="left", padx=1, expand=True, fill="x")

            # Slider Opacity untuk layer aktif
            opacityRow = tk.Frame(p, bg=C["panel"])
            opacityRow.pack(fill="x", padx=12, pady=4)
            tk.Label(opacityRow, text="Layer Opacity", bg=C["panel"], fg=C["dim"], font=FONT_SM).pack(side="left", padx=(0, 6))
            self.layerOpacityVar = tk.IntVar(value=100)
            self.layerOpacityScale = tk.Scale(
                opacityRow, variable=self.layerOpacityVar, from_=0, to=100,
                orient="horizontal", showvalue=True, bg=C["panel"], fg=C["text"],
                troughcolor=C["card"], highlightthickness=0, bd=0, sliderlength=12,
                activebackground=C["accent"], font=FONT_SM,
                command=self._onLayerOpacityChange
            )
            self.layerOpacityScale.pack(side="left", fill="x", expand=True)

            # Layer panel dengan scrollbar
            layerContainer = tk.Frame(p, bg=C["panel"])
            layerContainer.pack(fill="both", expand=True, padx=12, pady=4)
            
            self.layerCanvas = tk.Canvas(layerContainer, bg=C["panel"], highlightthickness=0, height=150)
            scrollbar = tk.Scrollbar(layerContainer, orient="vertical", command=self.layerCanvas.yview)
            self.layerFrame = tk.Frame(self.layerCanvas, bg=C["panel"])
            
            self.layerFrame.bind(
                "<Configure>",
                lambda e: self.layerCanvas.configure(scrollregion=self.layerCanvas.bbox("all"))
            )
            
            self.layerWindow = self.layerCanvas.create_window((0, 0), window=self.layerFrame, anchor="nw")
            self.layerCanvas.configure(yscrollcommand=scrollbar.set)
            self.layerCanvas.bind('<Configure>', lambda e: self.layerCanvas.itemconfigure(self.layerWindow, width=e.width))
            self.layerCanvas.bind('<Enter>', lambda e: self.layerCanvas.focus_set())
            self.layerCanvas.bind('<Enter>', lambda e: self.layerCanvas.bind_all('<MouseWheel>', self._onLayerPanelMouseWheel))
            self.layerCanvas.bind('<Leave>', lambda e: self.layerCanvas.unbind_all('<MouseWheel>'))
            self.layerCanvas.bind('<MouseWheel>', self._onLayerPanelMouseWheel)
            self.layerCanvas.bind('<Button-4>', self._onLayerPanelMouseWheel)
            self.layerCanvas.bind('<Button-5>', self._onLayerPanelMouseWheel)
            self.layerFrame.bind('<MouseWheel>', self._onLayerPanelMouseWheel)
            self.layerFrame.bind('<Button-4>', self._onLayerPanelMouseWheel)
            self.layerFrame.bind('<Button-5>', self._onLayerPanelMouseWheel)
            layerContainer.bind('<MouseWheel>', self._onLayerPanelMouseWheel)
            layerContainer.bind('<Button-4>', self._onLayerPanelMouseWheel)
            layerContainer.bind('<Button-5>', self._onLayerPanelMouseWheel)
            
            self.layerCanvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            self._refreshLayerPanel()


        def _buildTimelapseSection(self, p):
            sectionTitle(p, "TIMELAPSE")

            self.playBtn = tk.Button(
                p, text="▶  Play Timelapse", command=self._startPlayback,
                bg=C["accent"], fg="#fff", bd=0, relief="flat",
                font=("Segoe UI", 10, "bold"), cursor="hand2", pady=12,
                activebackground=C["accent2"], activeforeground="#fff"
            )
            self.playBtn.pack(fill="x", padx=12, pady=(4, 2))
            self.playBtn.bind("<Enter>", lambda e: self.playBtn.config(bg=C["accent2"]))
            self.playBtn.bind("<Leave>", lambda e: self.playBtn.config(bg=C["accent"]))

            flatBtn(p, "■  Stop", self._stopPlayback, padx=0, pady=7).pack(
                fill="x", padx=12, pady=2)

            self.speedVar = tk.DoubleVar(value=2.0)
            self._sliderRow(p, "Speed ×", self.speedVar, 0.1, 20,
                            lambda v: setattr(self, "playSpeed", float(v)), res=0.1)

            self.strokeLbl = tk.Label(p, text="Strokes: 0", bg=C["panel"],
                                    fg=C["dim"], font=FONT_SM)
            self.strokeLbl.pack(anchor="w", padx=14, pady=2)

            self.progressVar = tk.DoubleVar(value=0)
            style = ttk.Style()
            style.configure("D.Horizontal.TProgressbar",
                            background=C["accent"], troughcolor=C["card"],
                            bordercolor=C["panel"], lightcolor=C["accent"],
                            darkcolor=C["accent"])
            self.progressBar = ttk.Progressbar(p, variable=self.progressVar,
                                                maximum=100, style="D.Horizontal.TProgressbar")
            self.progressBar.pack(fill="x", padx=12, pady=4)

            sep(p, pad=(8, 0))

            infoRow = tk.Frame(p, bg=C["panel"])
            infoRow.pack(fill="x", padx=12, pady=6)
            flatBtn(infoRow, "Reset Zoom", self._resetZoom, pady=4, padx=8).pack(
                side="left", padx=2)
            flatBtn(infoRow, "Clear", self._clearCanvas, pady=4, padx=8,
                    bg="#3a1818", fg=C["danger"]).pack(side="left", padx=2)

        # ──────── HELPERS ────────
        def _sliderRow(self, parent, label, var, lo, hi, cmd, res=1):
            row = tk.Frame(parent, bg=C["panel"])
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=label, bg=C["panel"], fg=C["dim"],
                    font=FONT_SM, width=9, anchor="w").pack(side="left")
            s = tk.Scale(row, from_=lo, to=hi, orient="horizontal", variable=var,
                        command=cmd, bg=C["panel"], fg=C["text"],
                        troughcolor=C["card"], highlightthickness=0,
                        bd=0, resolution=res, showvalue=True,
                        font=FONT_SM, length=100,
                        activebackground=C["accent"])
            s.pack(side="left", fill="x", expand=True)

        def _makeTooltip(self, widget, text):
            def show(e):
                tip = tk.Toplevel(widget)
                tip.wm_overrideredirect(True)
                tip.geometry(f"+{e.x_root+14}+{e.y_root+2}")
                tk.Label(tip, text=text, bg=C["card"], fg=C["text"],
                        font=FONT_SM, bd=0, padx=8, pady=4).pack()
                widget._tip = tip
            def hide(e):
                if hasattr(widget, "_tip"):
                    try: widget._tip.destroy()
                    except Exception: pass
            widget.bind("<Enter>", show)
            widget.bind("<Leave>", hide)

        # ──────── TOOLS ────────
        def _pickColor(self):
            c = colorchooser.askcolor(color=self.brushColor, title="Color Picker")
            if c and c[1]:
                self._setColor(c[1])

        def _setColor(self, hex_):
            hex_ = hex_.strip()
            if not hex_.startswith("#"):
                hex_ = "#" + hex_
            try:
                self.root.winfo_rgb(hex_)
            except Exception:
                return
            self.brushColor = hex_
            self.colorPreview.config(bg=hex_)
            self.colorDot.config(bg=hex_)
            self.hexEntry.delete(0, "end")
            self.hexEntry.insert(0, hex_)

        def _toggleSym(self):
            self.symmetry = not self.symmetry
            self.symBtn.config(fg=C["accent"] if self.symmetry else C["dim"])
            self._scheduleRender()

        def _changeBrushSize(self, d):
            self.brushSize = max(1, min(200, self.brushSize + d))
            self.brushSizeVar.set(self.brushSize)

        # * Parameter transformasi image↔screen (normal vs crop viewport saat zoom tinggi)
        def _viewParams(self):
            w = self.tkCanvas.winfo_width() or 800
            h = self.tkCanvas.winfo_height() or 600
            sw = max(1, int(self.CW * self.zoom))
            sh = max(1, int(self.CH * self.zoom))
            ox = self.offsetX if self.offsetX is not None else (w - sw) // 2
            oy = self.offsetY if self.offsetY is not None else (h - sh) // 2

            if sw > w * 2 or sh > h * 2:
                vx1 = max(0, -ox / self.zoom)
                vy1 = max(0, -oy / self.zoom)
                vx2 = min(self.CW, (-ox + w) / self.zoom)
                vy2 = min(self.CH, (-oy + h) / self.zoom)
                # Preserve the real zoom ratio at canvas edges.  The render origin
                # is the clipped crop origin, so image/screen conversion stays
                # stable at high zoom instead of adding vx1 twice.
                render_ox = max(0, ox + vx1 * self.zoom)
                render_oy = max(0, oy + vy1 * self.zoom)
                return render_ox, render_oy, vx1, vy1, self.zoom, self.zoom, True
            return ox, oy, 0.0, 0.0, self.zoom, self.zoom, False

        def _toScreen(self, ix, iy):
            ox, oy, vx1, vy1, sx, sy, _ = self._viewParams()
            return ox + (ix - vx1) * sx, oy + (iy - vy1) * sy

        # * Mengubah koordinat layar canvas menjadi koordinat piksel gambar asli
        def _toImg(self, cx, cy):
            w = self.tkCanvas.winfo_width() or 800
            h = self.tkCanvas.winfo_height() or 600
            ox, oy, vx1, vy1, sx, sy, cropped = self._viewParams()

            if cropped:
                return vx1 + (cx - ox) / sx, vy1 + (cy - oy) / sy
            return (cx - ox) / sx, (cy - oy) / sy

        # * Auto-fit zoom dan posisi canvas agar seluruh canvas terlihat penuh di viewport
        def _centerCanvas(self):
            w = self.tkCanvas.winfo_width()
            h = self.tkCanvas.winfo_height()
            if w < 10 or h < 10:
                self.root.after(80, self._centerCanvas)
                return
            pad = 24
            zoomW = (w - pad * 2) / self.CW
            zoomH = (h - pad * 2) / self.CH
            self.zoom = round(min(zoomW, zoomH, 1.0), 4)
            sw = int(self.CW * self.zoom)
            sh = int(self.CH * self.zoom)
            self.offsetX = (w - sw) // 2
            self.offsetY = (h - sh) // 2
            if self.zoomLbl:
                self.zoomLbl.config(text=f"{int(self.zoom * 100)}%")
            self._scheduleRender(fast=False)

        # * Menempelkan koordinat gambar ke garis penggaris jika penggaris aktif
        def _snapToRuler(self, x, y):
            if not self.rulerActive:
                return x, y
            rad = math.radians(self.rulerAngle)
            dx = math.cos(rad)
            dy = math.sin(rad)
            vx = x - self.rulerX
            vy = y - self.rulerY
            proj = vx * dx + vy * dy
            rx = self.rulerX + proj * dx
            ry = self.rulerY + proj * dy
            return rx, ry

        # ──────── MOUSE ────────
        # * Mengubah nilai stabilizer melalui slider
        def _setStabilizerVal(self, val):
            self.stabilizerVal = int(float(val))
            # Clear buffer on value change
            self._smoothBufX.clear()
            self._smoothBufY.clear()

        # * Smoothing buffer untuk Real-time stabilizer
        def _smoothPoint(self, x, y):
            val = self.stabilizerVal
            if val <= 0:
                return x, y
            # Skala window ditingkatkan (misal skala 1 = 3 pt, skala 10 = 30 pt)
            window_limit = val * 3
            self._smoothBufX.append(x)
            self._smoothBufY.append(y)
            while len(self._smoothBufX) > window_limit + 1:
                self._smoothBufX.pop(0)
                self._smoothBufY.pop(0)
            # Dynamic weighting berdasarkan nilai stabilizer
            sx = sy = wsum = 0.0
            n = len(self._smoothBufX)
            for i in range(n):
                w = math.pow((i + 1) / n, 0.5 + (10 - val) * 0.15)
                sx += self._smoothBufX[i] * w
                sy += self._smoothBufY[i] * w
                wsum += w
            return sx / wsum, sy / wsum

        def _handleDrop(self, event):
            """Handle file drop (drag & drop image onto canvas)."""
            raw = event.data
            if not raw:
                return
            path = raw.strip('{}').strip()
            # Handle file:// URI prefix (from browsers, etc.)
            if path.startswith('file:///'):
                path = path[8:]
                if os.name == 'nt' and path.startswith('/'):
                    path = path[1:]
            elif path.startswith('file://'):
                path = path[7:]
            ext = os.path.splitext(path)[1].lower()
            if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff', '.tif'):
                self._importImageToLayer(path)

        def _findStrokeAt(self, x, y):
            """Return the topmost recorded stroke near an image-space point."""
            for index in range(len(self.strokeHistory) - 1, -1, -1):
                stroke = self.strokeHistory[index]
                if not stroke or not isinstance(stroke[0], dict):
                    continue
                if stroke[0].get("layer", self.activeIdx) != self.activeIdx:
                    continue
                threshold = max(8, stroke[0].get("size", self.brushSize) / 2 + 4)
                for point in stroke:
                    if "x" in point and "y" in point and math.hypot(x - point["x"], y - point["y"]) <= threshold:
                        pts = [(p["x"], p["y"]) for p in stroke if "x" in p and "y" in p]
                        if pts:
                            pad = threshold
                            return index, (min(px for px, _ in pts) - pad, min(py for _, py in pts) - pad,
                                        max(px for px, _ in pts) + pad, max(py for _, py in pts) + pad)
            return None, None
        
        # ──────── MOUSE ────────
        def _onDown(self, event):
            if self.isPlaying: return
            
            if self.rulerActive:
                cx, cy = self._toImg(event.x, event.y)
                dist = math.hypot(cx - self.rulerX, cy - self.rulerY)
                if dist < 30 / self.zoom:
                    self.rulerIsDragging = True
                    self._px = cx
                    self._py = cy
                    return

            x, y = self._toImg(event.x, event.y)
            x, y = self._snapToRuler(x, y)
            x = max(0, min(x, self.CW - 1))
            y = max(0, min(y, self.CH - 1))
            self.lastX, self.lastY = x, y
            self.currentStroke = []
            self._smoothBufX.clear()
            self._smoothBufY.clear()

            # Jangan save undo di sini
            # Save undo di _onUp untuk semua mode
            # DEBUG: detail koordinat
            w_canvas = self.tkCanvas.winfo_width() or 800
            h_canvas = self.tkCanvas.winfo_height() or 600
            sw_ = int(self.CW * self.zoom)
            sh_ = int(self.CH * self.zoom)
            ox_ = self.offsetX if self.offsetX is not None else (w_canvas - sw_) // 2
            oy_ = self.offsetY if self.offsetY is not None else (h_canvas - sh_) // 2

            if self.tool == "eyedrop":
                self._eyedrop(x, y); return
            if self.tool == "fill":
                self._fill(int(x), int(y)); return
            if self.tool == "select":
                # Check handle interactions (moving vs scaling with corner handles)
                if self.selectionRect:
                    x1, y1, x2, y2 = self.selectionRect
                    left, right = min(x1, x2), max(x1, x2)
                    top, bottom = min(y1, y2), max(y1, y2)
                    tol = 12 / max(self.zoom, 0.01)

                    handle = None
                    if math.hypot(x - left, y - top) <= tol:
                        handle = "nw"
                    elif math.hypot(x - right, y - top) <= tol:
                        handle = "ne"
                    elif math.hypot(x - left, y - bottom) <= tol:
                        handle = "sw"
                    elif math.hypot(x - right, y - bottom) <= tol:
                        handle = "se"
                    elif left <= x <= right and top <= y <= bottom:
                        handle = "move"

                    if handle is not None:
                        if self._selectionPayload is None:
                            ix1, iy1 = max(0, int(left)), max(0, int(top))
                            ix2, iy2 = min(self.CW, int(math.ceil(right))), min(self.CH, int(math.ceil(bottom)))
                            if ix2 > ix1 and iy2 > iy1:
                                self._saveUndo()
                                layer = self.layers[self.activeIdx]
                                self._selectionPayload = layer.image.crop((ix1, iy1, ix2, iy2))
                                layer.image.paste((0, 0, 0, 0), (ix1, iy1, ix2, iy2))
                                layer.draw = ImageDraw.Draw(layer.image)
                                self._cacheDirty = True
                                self._selectionOriginRect = (ix1, iy1, ix2, iy2)
                                self.selectionRect = (ix1, iy1, ix2, iy2)
                        self.activeHandle = handle
                        self._selectionDragStart = (x, y)
                        if self._selectionOriginRect is None:
                            self._selectionOriginRect = (left, top, right, bottom)
                        self._scheduleRender(fast=True)
                        return

                if self._selectionPayload is not None and self.selectionRect:
                    x1, y1, x2, y2 = self.selectionRect
                    left, right = min(x1, x2), max(x1, x2)
                    top, bottom = min(y1, y2), max(y1, y2)
                    targetW = max(1, int(round(right - left)))
                    targetH = max(1, int(round(bottom - top)))
                    destX = max(0, min(self.CW - 1, int(round(left))))
                    destY = max(0, min(self.CH - 1, int(round(top))))
                    scaledPayload = self._selectionPayload.resize((targetW, targetH), Image.LANCZOS)
                    layer = self.layers[self.activeIdx]
                    layer.image.alpha_composite(scaledPayload, (destX, destY))
                    layer.draw = ImageDraw.Draw(layer.image)
                    self._cacheDirty = True

                self._selectionPayload = None
                self._selectionOriginRect = None
                self._selectionDragStart = None
                self.activeHandle = None
                self.selectionStart = (x, y)
                self.selectionRect = (x, y, x, y)
                self.selectedStrokeIndex = None
                self._scheduleRender(fast=True)
                return

            if self.tool == "shape":
                if self.shapeMode == "bezier":
                    # Click an existing anchor to reposition it instead of adding
                    # another point.
                    for index, (px, py) in enumerate(self.bezierAnchorPoints):
                        if math.hypot(x - px, y - py) <= 12 / max(self.zoom, 0.1):
                            self.dragSplinePoint = index
                            return
                    if self.bezierAnchorPoints == [] and self.shapeStartTime == 0.0:
                        self.shapeStartTime = time.time()
                    self.bezierAnchorPoints.append((x, y))
                    self.previewX, self.previewY = x, y
                    self._scheduleRender(fast=True)
                    return
                elif self.shapeMode == "polyline":
                    for index, (px, py) in enumerate(self.polylinePoints):
                        if math.hypot(x - px, y - py) <= 12 / max(self.zoom, 0.1):
                            self.dragSplinePoint = index
                            return
                    if not self.polylinePoints and self.shapeStartTime == 0.0:
                        self.shapeStartTime = time.time()
                    self.polylinePoints.append((x, y))
                    self.previewX, self.previewY = x, y
                    self._scheduleRender(fast=True)
                    return
                else:
                    if self.shapeStartPoint is None and self.shapeStartTime == 0.0:
                        self.shapeStartTime = time.time()
                    self.shapeStartPoint = (x, y)
                    self.previewX, self.previewY = x, y
                    return

            if self._usingVectorRenderer() and self.stabilizerVal > 0:
                x, y = self._smoothPoint(x, y)
                self.lastX, self.lastY = x, y
            self.currentStroke.append(self._pt(x, y))
            
            if self.stabilizerMethod == "Real-time" and not self._usingVectorRenderer():
                self._saveUndo()
                # The live preview is intentionally incremental.  Keep the clean
                # layer so the completed stroke can be painted in one pass on
                # mouse-up instead of retaining seams between mouse events.
                self._strokeBaseImage = self.layers[self.activeIdx].image.copy()
                self._applyPoint(x, y)
            elif self._usingVectorRenderer():
                self._saveUndo()

            self._scheduleRender(fast=True)

        def _onMove(self, event):
            if self.isPlaying: return
            
            if self.rulerIsDragging:
                cx, cy = self._toImg(event.x, event.y)
                self.rulerX = cx
                self.rulerY = cy
                self._scheduleRender(fast=True)
                return

            x, y = self._toImg(event.x, event.y)
            self.coordLbl.config(text=f"{int(x)}, {int(y)}")

            if self.tool in ("eyedrop", "fill"): return
            if self.tool == "select":
                if self._selectionPayload is not None and self._selectionDragStart and self._selectionOriginRect and self.activeHandle:
                    ox1, oy1, ox2, oy2 = self._selectionOriginRect
                    dx = x - self._selectionDragStart[0]
                    dy = y - self._selectionDragStart[1]
                    if self.activeHandle == "move":
                        self.selectionRect = (ox1 + dx, oy1 + dy, ox2 + dx, oy2 + dy)
                    elif self.activeHandle == "se":
                        self.selectionRect = (ox1, oy1, max(ox1 + 5, ox2 + dx), max(oy1 + 5, oy2 + dy))
                    elif self.activeHandle == "nw":
                        self.selectionRect = (min(ox2 - 5, ox1 + dx), min(oy2 - 5, oy1 + dy), ox2, oy2)
                    elif self.activeHandle == "ne":
                        self.selectionRect = (ox1, min(oy2 - 5, oy1 + dy), max(ox1 + 5, ox2 + dx), oy2)
                    elif self.activeHandle == "sw":
                        self.selectionRect = (min(ox2 - 5, ox1 + dx), oy1, ox2, max(oy1 + 5, oy2 + dy))
                    self._scheduleRender(fast=True)
                    return
                if self.selectionStart:
                    sx, sy = self.selectionStart
                    self.selectionRect = (sx, sy, x, y)
                    self._scheduleRender(fast=True)
                return

            if self.tool == "shape":
                x, y = self._snapToRuler(x, y)
                if self.dragSplinePoint is not None:
                    if self.shapeMode == "bezier" and self.dragSplinePoint < len(self.bezierAnchorPoints):
                        self.bezierAnchorPoints[self.dragSplinePoint] = (x, y)
                    elif self.shapeMode == "polyline" and self.dragSplinePoint < len(self.polylinePoints):
                        self.polylinePoints[self.dragSplinePoint] = (x, y)
                    self.previewX, self.previewY = x, y
                    self._scheduleRender(fast=True)
                    return
                self.previewX, self.previewY = x, y
                self._scheduleRender(fast=True)
                return

            if self.lastX is None:
                self.lastX, self.lastY = x, y
                return

            x_raw, y_raw = self._snapToRuler(x, y)
            x_raw = max(0, min(x_raw, self.CW - 1))
            y_raw = max(0, min(y_raw, self.CH - 1))

            # Vector Pen records the stabilized path itself, so its high-zoom
            # renderer receives exactly the same smoothing as a normal brush.
            if self._usingVectorRenderer() and self.stabilizerVal > 0:
                sx, sy = self._smoothPoint(x_raw, y_raw)
                self.currentStroke.append(self._pt(sx, sy))
            else:
                sx, sy = x_raw, y_raw
                self.currentStroke.append(self._pt(x_raw, y_raw))
            
            # Real-time: draw ke layer langsung
            if self.stabilizerMethod == "Real-time" and not self._usingVectorRenderer():
                # Apply stabilizer smoothing jika aktif
                if self.stabilizerVal > 0:
                    sx, sy = self._smoothPoint(x_raw, y_raw)
                else:
                    sx, sy = x_raw, y_raw
                self._applyLine(self.lastX, self.lastY, sx, sy)
                self._scheduleRender(fast=True)
                self._scheduleQualityRender()
            elif self._usingVectorRenderer():
                self._scheduleRender(fast=True)
                self._scheduleQualityRender()
            else:
                # Before-After: cuma render untuk preview, clear smooth buffer
                self._smoothBufX.clear()
                self._smoothBufY.clear()
                if len(self.currentStroke) % 2 == 0:
                    self._scheduleRender(fast=True)
                    self._scheduleQualityRender()

            self.lastX, self.lastY = (sx, sy) if ((self.stabilizerMethod == "Real-time" or self._usingVectorRenderer()) and self.stabilizerVal > 0) else (x_raw, y_raw)

        def _onUp(self, event):
            if self.isPlaying: return
            
            if self.rulerIsDragging:
                self.rulerIsDragging = False
                return

            if self.tool == "select":
                if self._selectionPayload is not None and self.selectionRect:
                    x1, y1, x2, y2 = self.selectionRect
                    left, right = min(x1, x2), max(x1, x2)
                    top, bottom = min(y1, y2), max(y1, y2)
                    targetW = max(1, int(round(right - left)))
                    targetH = max(1, int(round(bottom - top)))
                    destX = max(0, min(self.CW - 1, int(round(left))))
                    destY = max(0, min(self.CH - 1, int(round(top))))
                    scaledPayload = self._selectionPayload.resize((targetW, targetH), Image.LANCZOS)
                    layer = self.layers[self.activeIdx]
                    layer.image.alpha_composite(scaledPayload, (destX, destY))
                    layer.draw = ImageDraw.Draw(layer.image)
                    self.selectionRect = (destX, destY, destX + targetW, destY + targetH)
                    self._selectionPayload = None
                    self._selectionOriginRect = None
                    self._selectionDragStart = None
                    self.activeHandle = None
                    self._cacheDirty = True
                    self._scheduleRender(fast=False)
                    return
                if self.selectionStart:
                    sx, sy = self.selectionStart
                    ex, ey = self._toImg(event.x, event.y)
                    if math.hypot(ex - sx, ey - sy) < 5:
                        self.selectedStrokeIndex, self.selectionRect = self._findStrokeAt(sx, sy)
                    else:
                        self.selectionRect = (sx, sy, ex, ey)
                        self.selectedStrokeIndex = None
                self.selectionStart = None
                self.activeHandle = None
                self._scheduleRender(fast=False)
                return

            if self.tool == "shape":
                if self.shapeMode in ("bezier", "polyline"):
                    if self.dragSplinePoint is not None:
                        self.dragSplinePoint = None
                        self._scheduleRender(fast=False)
                    return
                    
                if self.shapeStartPoint and self.previewX is not None:
                    self._saveUndo()
                    p0 = self.shapeStartPoint
                    p1 = (self.previewX, self.previewY)
                    
                    if self.startTime == 0.0:
                        self.startTime = time.time()
                    
                    use_vector = self._usingVectorRenderer() or self.renderQuality in ("high", "ultra")
                    if use_vector:
                        points = self._shapeVectorPoints(self.shapeMode, p0, p1)
                        self.strokeHistory.append([
                            {"x": x, "y": y, "color": self.brushColor,
                            "size": self.brushSize, "opacity": self.brushOpacity,
                            "mode": "vector_pen", "layer": self.activeIdx,
                            "layer_name": self.layers[self.activeIdx].name,
                            "t": time.time() - self.startTime}
                            for x, y in points
                        ])
                    else:
                        self._drawShapeToLayer(self.shapeMode, p0[0], p0[1], p1[0], p1[1])
                        self.strokeHistory.append([
                            {"x": p0[0], "y": p0[1], "color": self.brushColor, "size": self.brushSize, "opacity": self.brushOpacity, "mode": f"shape_{self.shapeMode}", "layer": self.activeIdx, "t": time.time() - self.startTime, "ex": p1[0], "ey": p1[1]}
                        ])
                    if self.strokeLbl: self.strokeLbl.config(text=f"Strokes: {len(self.strokeHistory)}")
                    
                self.shapeStartPoint = None
                self.previewX = self.previewY = None
                self._scheduleRender(fast=False)
                return

            # Button release often arrives after the last B1-Motion event when
            # drawing quickly.  Capture that final coordinate so the stroke is
            # always connected all the way to the cursor.
            if self.currentStroke and self.lastX is not None:
                end_x, end_y = self._toImg(event.x, event.y)
                end_x, end_y = self._snapToRuler(end_x, end_y)
                end_x = max(0, min(end_x, self.CW - 1))
                end_y = max(0, min(end_y, self.CH - 1))
                if math.hypot(end_x - self.lastX, end_y - self.lastY) > 0.25:
                    if self._usingVectorRenderer() and self.stabilizerVal > 0:
                        end_x, end_y = self._smoothPoint(end_x, end_y)
                    self.currentStroke.append(self._pt(end_x, end_y))
                    if self.stabilizerMethod == "Real-time" and not self._usingVectorRenderer():
                        self._applyLine(self.lastX, self.lastY, end_x, end_y)
                    self.lastX, self.lastY = end_x, end_y

            if self.currentStroke:
                finalStroke = self._applyFadeToStroke(self.currentStroke)
                if self._usingVectorRenderer():
                    finalStroke = self._vectorizeStroke(finalStroke)
                    self.strokeHistory.append(finalStroke[:])
                    self._cacheDirty = True
                elif self.stabilizerMethod == "Before-After":
                    self._cacheDirty = True
                    self._saveUndo()
                    self._applyStrokeToLayer(finalStroke)
                    self.strokeHistory.append(finalStroke[:])
                else:
                    layer = self.layers[self.activeIdx]
                    if self._strokeBaseImage is not None:
                        layer.image = self._strokeBaseImage.copy()
                        layer.draw = ImageDraw.Draw(layer.image)
                    if finalStroke:
                        self._applyStrokeToLayer(finalStroke)
                    self._strokeBaseImage = None
                    self._cacheDirty = True
                    self.strokeHistory.append(finalStroke[:])
                if self.strokeLbl: self.strokeLbl.config(text=f"Strokes: {len(self.strokeHistory)}")

            self.currentStroke = []
            self.lastX = None
            self.startTime = 0.0
            self._scheduleRender(fast=False)
            # Force canvas update untuk pastiin tampilan ke-refresh
            try:
                self.root.update_idletasks()
            except Exception:
                pass


        # * Menyelesaikan pembuatan kurva Bezier atau Polyline dan menggambarnya ke layer aktif
        def _finishShape(self):
            if self.tool != "shape": return
            
            if self.shapeMode == "bezier" and len(self.bezierAnchorPoints) >= 2:
                self._saveUndo()
                
                if self.shapeStartTime == 0.0:
                    self.shapeStartTime = time.time()

                use_vector = self._usingVectorRenderer() or self.renderQuality in ("high", "ultra")
                if use_vector:
                    curve = self._catmull_rom(self.bezierAnchorPoints, num_segments=24)
                    shape_dur = max(0.02, time.time() - self.shapeStartTime)
                    total = len(curve)
                    self.strokeHistory.append([
                        {"x": x, "y": y, "color": self.brushColor, "size": self.brushSize,
                        "opacity": self.brushOpacity, "mode": "vector_pen", "layer": self.activeIdx,
                        "layer_name": self.layers[self.activeIdx].name,
                        "t": (i / max(1, total - 1)) * shape_dur}
                        for i, (x, y) in enumerate(curve)
                    ])
                else:
                    self._drawSplineToLayer(self.bezierAnchorPoints)
                    shape_dur = max(0.02, time.time() - self.shapeStartTime)
                    total = len(self.bezierAnchorPoints)
                    strokeData = []
                    for i, pt in enumerate(self.bezierAnchorPoints):
                        strokeData.append({
                            "x": pt[0], "y": pt[1], "color": self.brushColor, "size": self.brushSize,
                            "opacity": self.brushOpacity, "mode": "bezier_path", "layer": self.activeIdx,
                            "t": (i / max(1, total - 1)) * shape_dur, "idx": i, "total": total
                        })
                    self.strokeHistory.append(strokeData)
                if self.strokeLbl: self.strokeLbl.config(text=f"Strokes: {len(self.strokeHistory)}")
                self.bezierAnchorPoints.clear()
                self.dragSplinePoint = None
                self.shapeStartTime = 0.0
                self._cacheDirty = True
                self._scheduleRender(fast=False)
                
            elif self.shapeMode == "polyline" and len(self.polylinePoints) >= 2:
                self._saveUndo()
                
                if self.shapeStartTime == 0.0:
                    self.shapeStartTime = time.time()

                use_vector = self._usingVectorRenderer() or self.renderQuality in ("high", "ultra")
                curve = self._catmull_rom(self.polylinePoints, num_segments=24)
                if use_vector:
                    shape_dur = max(0.02, time.time() - self.shapeStartTime)
                    total = len(curve)
                    self.strokeHistory.append([
                        {"x": x, "y": y, "color": self.brushColor, "size": self.brushSize,
                        "opacity": self.brushOpacity, "mode": "vector_pen", "layer": self.activeIdx,
                        "layer_name": self.layers[self.activeIdx].name,
                        "t": (i / max(1, total - 1)) * shape_dur}
                        for i, (x, y) in enumerate(curve)
                    ])
                else:
                    self._drawSplineToLayer(self.polylinePoints)
                    shape_dur = max(0.02, time.time() - self.shapeStartTime)
                    total = len(self.polylinePoints)
                    strokeData = []
                    for i, pt in enumerate(self.polylinePoints):
                        strokeData.append({
                            "x": pt[0], "y": pt[1], "color": self.brushColor, "size": self.brushSize,
                            "opacity": self.brushOpacity, "mode": "polyline", "layer": self.activeIdx,
                            "t": (i / max(1, total - 1)) * shape_dur, "idx": i, "total": total
                        })
                    self.strokeHistory.append(strokeData)
                if self.strokeLbl: self.strokeLbl.config(text=f"Strokes: {len(self.strokeHistory)}")
                self.polylinePoints.clear()
                self.shapeStartTime = 0.0
                self._scheduleRender(fast=False)

        def _shapeVectorPoints(self, mode, p0, p1):
            """Convert a two-point shape to a scalable Vector Pen path."""
            x1, y1 = p0
            x2, y2 = p1
            if mode == "line":
                return [p0, p1]
            if mode in ("rect", "rounded_rect", "bubble"):
                return [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
            if mode in ("oval", "circle"):
                if mode == "circle":
                    cx, cy = (x1+x2)/2, (y1+y2)/2
                    radius = math.hypot(x2-x1, y2-y1)/2
                    rx = ry = radius
                else:
                    cx, cy = (x1+x2)/2, (y1+y2)/2
                    rx, ry = abs(x2-x1)/2, abs(y2-y1)/2
                return [(cx + rx*math.cos(math.tau*i/48), cy + ry*math.sin(math.tau*i/48))
                        for i in range(49)]
            if mode == "hexagon":
                cx, cy = (x1+x2)/2, (y1+y2)/2
                radius = math.hypot(x2-x1, y2-y1)/2
                points = [(cx + radius*math.cos(math.pi/3*i-math.pi/2),
                        cy + radius*math.sin(math.pi/3*i-math.pi/2)) for i in range(6)]
                return points + [points[0]]
            if mode == "arrow":
                angle = math.atan2(y2-y1, x2-x1)
                head = max(12, min(40, math.hypot(x2-x1, y2-y1)*0.25))
                a1 = (x2-head*math.cos(angle-math.pi/6), y2-head*math.sin(angle-math.pi/6))
                a2 = (x2-head*math.cos(angle+math.pi/6), y2-head*math.sin(angle+math.pi/6))
                return [p0, p1, a1, p1, a2]
            return [p0, p1]

        # * Menggambar bentuk tertentu secara permanen ke layer aktif
        def _drawShapeToLayer(self, mode, x1, y1, x2, y2):
            if mode == "line":
                self._drawLineToLayer(x1, y1, x2, y2)
            elif mode == "rect":
                self._drawLineToLayer(x1, y1, x2, y1)
                self._drawLineToLayer(x2, y1, x2, y2)
                self._drawLineToLayer(x2, y2, x1, y2)
                self._drawLineToLayer(x1, y2, x1, y1)
            elif mode == "circle":
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                r = math.hypot(x2 - x1, y2 - y1) / 2
                self._drawOvalToLayer(cx - r, cy - r, cx + r, cy + r)
            elif mode == "hexagon":
                self._drawHexagonToLayer(x1, y1, x2, y2)
            elif mode == "arrow":
                self._drawArrowToLayer(x1, y1, x2, y2)
            elif mode == "oval":
                self._drawOvalToLayer(x1, y1, x2, y2)
            elif mode == "rounded_rect":
                self._drawRoundedRectToLayer(x1, y1, x2, y2, radius=12)
            elif mode == "bubble":
                self._drawBubbleToLayer(x1, y1, x2, y2)

        # * Menggambar garis lurus di layer aktif
        def _drawLineToLayer(self, x1, y1, x2, y2):
            layer = self.layers[self.activeIdx]
            if layer.locked:
                return
            self._cacheDirty = True
            color = self._rgba(self.brushColor, self.brushOpacity)
            self._drawLineOnLayer(layer, [(x1, y1), (x2, y2)], color, max(1, self.brushSize))
            if self.symmetry:
                self._drawLineOnLayer(layer, [(self.CW-x1, y1), (self.CW-x2, y2)], color, max(1, self.brushSize))
                self._drawLineOnLayer(layer, [(x1, self.CH-y1), (x2, self.CH-y2)], color, max(1, self.brushSize))
                self._drawLineOnLayer(layer, [(self.CW-x1, self.CH-y1), (self.CW-x2, self.CH-y2)], color, max(1, self.brushSize))
                    
        # * Menggambar kurva Bezier kuadratik di layer aktif
        def _drawBezierToLayer(self, p0, p1, p2):
            layer = self.layers[self.activeIdx]
            if layer.locked:
                return
            color = self._rgba(self.brushColor, self.brushOpacity)
            points = []
            for i in range(101):
                t = i / 100
                mt = 1 - t
                xi = mt*mt*p0[0] + 2*mt*t*p1[0] + t*t*p2[0]
                yi = mt*mt*p0[1] + 2*mt*t*p1[1] + t*t*p2[1]
                points.append((xi, yi))
            self._drawLineOnLayer(layer, points, color, max(1, self.brushSize))

        # * Menggambar spline kontinu di layer aktif (Catmull-Rom)
        def _drawSplineToLayer(self, points):
            if len(points) < 2: return
            self._cacheDirty = True
            if len(points) == 2:
                self._drawLineToLayer(points[0][0], points[0][1], points[1][0], points[1][1])
                return

            layer = self.layers[self.activeIdx]
            if layer.locked:
                return
            curve = self._catmull_rom(points, num_segments=24)
            color = self._rgba(self.brushColor, self.brushOpacity)
            self._drawLineOnLayer(layer, curve, color, max(1, self.brushSize))
            if self.symmetry:
                for mirrored in (
                    [(self.CW - x, y) for x, y in curve],
                    [(x, self.CH - y) for x, y in curve],
                    [(self.CW - x, self.CH - y) for x, y in curve],
                ):
                    self._drawLineOnLayer(layer, mirrored, color, max(1, self.brushSize))
            layer.draw = ImageDraw.Draw(layer.image)
            self._cacheDirty = True

        # * Menghaluskan sudut belokan polyline dengan kurva quadratic bezier
        def _smoothPolylineCorners(self, pts, maxRadius=20):
            if len(pts) < 3:
                return pts
            smoothed = [pts[0]]
            for i in range(1, len(pts) - 1):
                prevP = pts[i - 1]
                currP = pts[i]
                nextP = pts[i + 1]
                
                d1 = math.hypot(currP[0] - prevP[0], currP[1] - prevP[1])
                d2 = math.hypot(nextP[0] - currP[0], nextP[1] - currP[1])
                r = min(maxRadius, d1 * 0.4, d2 * 0.4)
                if r < 1:
                    smoothed.append(currP)
                    continue
                    
                q1x = currP[0] + (prevP[0] - currP[0]) * (r / d1)
                q1y = currP[1] + (prevP[1] - currP[1]) * (r / d1)
                
                q2x = currP[0] + (nextP[0] - currP[0]) * (r / d2)
                q2y = currP[1] + (nextP[1] - currP[1]) * (r / d2)
                
                for step in range(1, 9):
                    t = step / 8.0
                    mt = 1.0 - t
                    bx = mt * mt * q1x + 2 * mt * t * currP[0] + t * t * q2x
                    by = mt * mt * q1y + 2 * mt * t * currP[1] + t * t * q2y
                    smoothed.append((bx, by))
            smoothed.append(pts[-1])
            return smoothed

        # * Menggambar polyline di layer aktif
        def _drawPolylineToLayer(self, points):
            if len(points) < 2: return
            layer = self.layers[self.activeIdx]
            if layer.locked: return
            color = self._rgba(self.brushColor, self.brushOpacity)
            smooth_points = self._smoothPolylineCorners(points)
            self._drawLineOnLayer(layer, smooth_points, color, max(1, self.brushSize))
            if self.symmetry:
                self._drawLineOnLayer(layer, [(self.CW - x, y) for x, y in smooth_points], color, max(1, self.brushSize))
                self._drawLineOnLayer(layer, [(x, self.CH - y) for x, y in smooth_points], color, max(1, self.brushSize))
                self._drawLineOnLayer(layer, [(self.CW - x, self.CH - y) for x, y in smooth_points], color, max(1, self.brushSize))
            self._cacheDirty = True

        # * Menggambar bubble chat di layer aktif
        def _drawBubbleToLayer(self, x1, y1, x2, y2):
            layer = self.layers[self.activeIdx]
            if layer.locked: return
            rx1, ry1 = min(x1, x2), min(y1, y2)
            rx2, ry2 = max(x1, x2), max(y1, y2)
            self._drawRoundedRectToLayer(rx1, ry1, rx2, ry2, radius=12)
            tx1 = rx1 + (rx2 - rx1) * 0.2
            ty1 = ry2
            tx2 = rx1 + (rx2 - rx1) * 0.3
            ty2 = ry2
            tx3 = rx1 + (rx2 - rx1) * 0.15
            ty3 = ry2 + (ry2 - ry1) * 0.25
            self._drawLineToLayer(tx1, ty1, tx3, ty3)
            self._drawLineToLayer(tx2, ty2, tx3, ty3)

        # * Menggambar oval di layer aktif
        def _drawOvalToLayer(self, x1, y1, x2, y2):
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            rx = abs(x2 - x1) / 2
            ry = abs(y2 - y1) / 2
            steps = 100
            prevX, prevY = cx + rx, cy
            for i in range(1, steps + 1):
                t = 2 * math.pi * i / steps
                xi = cx + rx * math.cos(t)
                yi = cy + ry * math.sin(t)
                self._drawLineToLayer(prevX, prevY, xi, yi)
                prevX, prevY = xi, yi

        # * Menggambar hexagon di layer aktif
        def _drawHexagonToLayer(self, x1, y1, x2, y2):
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            rx = abs(x2 - x1) / 2
            ry = abs(y2 - y1) / 2
            pts = []
            for i in range(6):
                t = 2 * math.pi * i / 6
                pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
            for i in range(6):
                p1 = pts[i]
                p2 = pts[(i+1)%6]
                self._drawLineToLayer(p1[0], p1[1], p2[0], p2[1])

        # * Menggambar panah di layer aktif
        def _drawArrowToLayer(self, x1, y1, x2, y2):
            self._drawLineToLayer(x1, y1, x2, y2)
            angle = math.atan2(y2 - y1, x2 - x1)
            head_len = 20
            ax1 = x2 - head_len * math.cos(angle - math.pi/6)
            ay1 = y2 - head_len * math.sin(angle - math.pi/6)
            ax2 = x2 - head_len * math.cos(angle + math.pi/6)
            ay2 = y2 - head_len * math.sin(angle + math.pi/6)
            self._drawLineToLayer(x2, y2, ax1, ay1)
            self._drawLineToLayer(x2, y2, ax2, ay2)

        # * Menggambar rounded rect di layer aktif
        def _drawRoundedRectToLayer(self, x1, y1, x2, y2, radius=12):
            rx1, ry1 = min(x1, x2), min(y1, y2)
            rx2, ry2 = max(x1, x2), max(y1, y2)
            self._drawLineToLayer(rx1 + radius, ry1, rx2 - radius, ry1)
            self._drawLineToLayer(rx2, ry1 + radius, rx2, ry2 - radius)
            self._drawLineToLayer(rx2 - radius, ry2, rx1 + radius, ry2)
            self._drawLineToLayer(rx1, ry2 - radius, rx1, ry1 + radius)
            self._drawArcToLayer(rx2 - radius, ry1 + radius, radius, -math.pi/2, 0)
            self._drawArcToLayer(rx2 - radius, ry2 - radius, radius, 0, math.pi/2)
            self._drawArcToLayer(rx1 + radius, ry2 - radius, radius, math.pi/2, math.pi)
            self._drawArcToLayer(rx1 + radius, ry1 + radius, radius, math.pi, 1.5*math.pi)

        # * Menggambar arc di layer aktif
        def _drawArcToLayer(self, cx, cy, r, start_rad, end_rad):
            steps = 15
            prevX = cx + r * math.cos(start_rad)
            prevY = cy + r * math.sin(start_rad)
            for i in range(1, steps + 1):
                t = start_rad + (end_rad - start_rad) * i / steps
                xi = cx + r * math.cos(t)
                yi = cy + r * math.sin(t)
                self._drawLineToLayer(prevX, prevY, xi, yi)
                prevX, prevY = xi, yi

        # * Mengaplikasikan stroke lengkap ke layer aktif
        def _applyStrokeToLayer(self, stroke):
            if not stroke:
                return
            layerIdx = stroke[0].get("layer", self.activeIdx)
            layerIdx = min(max(0, layerIdx), len(self.layers) - 1)
            layer = self.layers[layerIdx]
            if layer.locked:
                return

            if self.stabilizerVal > 0:
                smoothed = []
                window_size = min(self.stabilizerVal * 3, len(stroke))
                for i, pt in enumerate(stroke):
                    start = max(0, i - window_size + 1)
                    window = stroke[start:i+1]
                    sum_x = sum_y = total_weight = 0
                    n_w = len(window)
                    for j, w_pt in enumerate(window):
                        weight = math.pow((j + 1) / n_w, 0.5 + (10 - self.stabilizerVal) * 0.15)
                        sum_x += w_pt["x"] * weight
                        sum_y += w_pt["y"] * weight
                        total_weight += weight
                    new_pt = pt.copy()
                    new_pt["x"] = sum_x / total_weight
                    new_pt["y"] = sum_y / total_weight
                    smoothed.append(new_pt)
                stroke = smoothed

            # The common brush case is rendered as one supersampled path.  Besides
            # producing cleaner edges, this avoids the dark, striped seams caused
            # by alpha-compositing one tiny buffer for every mouse event.
            if self._drawUniformStrokeOnLayer(layer, stroke):
                self._cacheDirty = True
                return

            prevX, prevY = None, None
            hardness = self.brushHardness
            for pt in stroke:
                x, y = pt["x"], pt["y"]
                radius = max(1, pt["size"] // 2)
                erase_width = max(1, pt["size"])
                color = self._rgba(pt["color"], pt["opacity"])
                is_eraser = (pt["mode"] == "eraser")

                if is_eraser:
                    fill_clr = (0,0,0,0)
                else:
                    fill_clr = color

                if prevX is not None:
                    dist = math.hypot(x - prevX, y - prevY)
                    steps = max(int(dist * 2), 2)
                    if hardness < 100 and not is_eraser:
                        for i in range(steps + 1):
                            t = i / steps
                            xi = prevX + (x - prevX) * t
                            yi = prevY + (y - prevY) * t
                            self._paintSoft(layer, xi, yi, radius, fill_clr, hardness)
                            if self.symmetry:
                                self._paintSoft(layer, self.CW - xi, yi, radius, color, hardness)
                                self._paintSoft(layer, xi, self.CH - yi, radius, color, hardness)
                                self._paintSoft(layer, self.CW - xi, self.CH - yi, radius, color, hardness)
                    else:
                        seg_pts = []
                        for i in range(steps + 1):
                            t = i / steps
                            xi = prevX + (x - prevX) * t
                            yi = prevY + (y - prevY) * t
                            seg_pts.append((xi, yi))
                        if is_eraser:
                            self._eraseLine(layer, seg_pts, erase_width)
                        else:
                            self._drawLineOnLayer(layer, seg_pts, fill_clr, erase_width)
                        if self.symmetry:
                            mx_pts = [(self.CW - xi, yi) for xi, yi in seg_pts]
                            my_pts = [(xi, self.CH - yi) for xi, yi in seg_pts]
                            mxy_pts = [(self.CW - xi, self.CH - yi) for xi, yi in seg_pts]
                            for sym_pts in (mx_pts, my_pts, mxy_pts):
                                if is_eraser:
                                    self._eraseLine(layer, sym_pts, erase_width)
                                else:
                                    self._drawLineOnLayer(layer, sym_pts, color, erase_width)
                else:
                    if hardness < 100 and not is_eraser:
                        self._paintSoft(layer, x, y, radius, fill_clr, hardness)
                    else:
                        if is_eraser:
                            self._eraseCircle(layer, x, y, radius, hardness)
                        else:
                            layer.draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=fill_clr)
                    if self.symmetry:
                        if hardness < 100 and not is_eraser:
                            self._paintSoft(layer, self.CW - x, y, radius, color, hardness)
                            self._paintSoft(layer, x, self.CH - y, radius, color, hardness)
                            self._paintSoft(layer, self.CW - x, self.CH - y, radius, color, hardness)
                        else:
                            if is_eraser:
                                self._eraseCircle(layer, self.CW - x, y, radius, hardness)
                                self._eraseCircle(layer, x, self.CH - y, radius, hardness)
                                self._eraseCircle(layer, self.CW - x, self.CH - y, radius, hardness)
                            else:
                                self._paintSym(layer, x, y, radius, color)
                prevX, prevY = x, y

            layer.draw = ImageDraw.Draw(layer.image)
            self._cacheDirty = True

        def _drawUniformStrokeOnLayer(self, layer, stroke):
            """Draw a normal hard brush stroke in one composite pass.

            Returns ``True`` only when all points share the same brush settings;
            specialised tools and variable-width/faded strokes retain their
            existing rendering path below.
            """
            if not stroke or self.brushHardness < 100:
                return False
            first = stroke[0]
            if first.get("mode") not in ("brush", "pencil"):
                return False
            settings = (first.get("mode"), first.get("color"), first.get("size"),
                        first.get("opacity"))
            if any((pt.get("mode"), pt.get("color"), pt.get("size"), pt.get("opacity"))
                != settings for pt in stroke):
                return False

            mode, hex_color, size, opacity = settings
            width = max(1, int(size))
            if mode == "pencil":
                width = max(1, width // 2)
            color = self._rgba(hex_color, opacity)
            points = [(float(pt["x"]), float(pt["y"])) for pt in stroke]
            # A 1 px brush is a pixel-art tool.  Supersampling then downscaling a
            # single-pixel path creates grey/blurred pixels, so keep it snapped to
            # the native canvas grid while still drawing one continuous line.
            if width <= 1:
                snapped = [(round(x), round(y)) for x, y in points]
                if len(snapped) == 1:
                    layer.draw.point(snapped[0], fill=color)
                else:
                    layer.draw.line(snapped, fill=color, width=1, joint="curve")
                layer.draw = ImageDraw.Draw(layer.image)
                return True

            ss = max(2, min(24, self.drawQuality * 2))
            radius = width / 2
            pad = int(math.ceil(radius)) + 3
            x0 = max(0, int(math.floor(min(x for x, _ in points) - pad)))
            y0 = max(0, int(math.floor(min(y for _, y in points) - pad)))
            x1 = min(self.CW, int(math.ceil(max(x for x, _ in points) + pad)))
            y1 = min(self.CH, int(math.ceil(max(y for _, y in points) + pad)))
            if x1 <= x0 or y1 <= y0:
                return False

            buf = Image.new("RGBA", ((x1-x0) * ss, (y1-y0) * ss), (0, 0, 0, 0))
            draw = ImageDraw.Draw(buf)
            path = [((x-x0) * ss, (y-y0) * ss) for x, y in points]
            ss_width = max(1, int(round(width * ss)))
            if len(path) > 1:
                draw.line(path, fill=color, width=ss_width, joint="curve")
            cap = ss_width / 2
            for x, y in (path[0], path[-1]):
                draw.ellipse((x-cap, y-cap, x+cap, y+cap), fill=color)
            layer.image.alpha_composite(buf.resize((x1-x0, y1-y0), Image.LANCZOS),
                                        (x0, y0))
            layer.draw = ImageDraw.Draw(layer.image)
            return True

        def _applyFadeToStroke(self, stroke):
            if (not self.fadeEnabled and not self.forceFade) or not stroke:
                return stroke
            N = len(stroke)
            if N < 4: return stroke
            
            startLimit = int(N * self.fadeStartPercent / 100)
            endLimit   = int(N * self.fadeEndPercent / 100)
            
            newStroke = []
            for i, pt in enumerate(stroke):
                ptCopy = pt.copy()
                factor = 1.0
                
                if startLimit > 0 and i < startLimit:
                    factor = i / startLimit
                    if self.fadeShape == "Halus agak lancip":
                        factor = math.sin(factor * math.pi / 2)
                elif endLimit > 0 and i > N - endLimit:
                    factor = (N - i) / endLimit
                    if self.fadeShape == "Halus agak lancip":
                        factor = math.sin(factor * math.pi / 2)
                        
                ptCopy["size"] = max(1, int(ptCopy["size"] * factor))
                ptCopy["opacity"] = int(ptCopy["opacity"] * factor)
                newStroke.append(ptCopy)
                
            return newStroke

        # * Redraw stroke as ONE smooth polyline to fix jagged segment joins (Real-time mode)
        def _redrawStrokeSmooth(self, stroke):
            if not stroke or len(stroke) < 2:
                return
            layer = self.layers[self.activeIdx]
            if layer.locked:
                return
            has_eraser = any(pt.get("mode") == "eraser" for pt in stroke)
            if has_eraser:
                return  # Can't easily polyline eraser strokes
            
            # Collect all points
            pts = [(pt["x"], pt["y"]) for pt in stroke]
            # Use middle point's opacity/size (fade makes first/last points near-invisible)
            mid_idx = len(stroke) // 2
            mid_pt = stroke[mid_idx]
            color = self._rgba(mid_pt["color"], mid_pt["opacity"])
            size = mid_pt["size"]
            
            # Redraw as one smooth polyline with join fill
            smooth_pts = self._catmull_rom(pts, num_segments=12)
            layer.draw.line(smooth_pts, fill=color, width=size, joint='curve')
            
            # Handle symmetry for the polyline
            if self.symmetry:
                mx_pts = [(self.CW - x, y) for x, y in pts]
                my_pts = [(x, self.CH - y) for x, y in pts]
                mxy_pts = [(self.CW - x, self.CH - y) for x, y in pts]
                smx = self._catmull_rom(mx_pts, num_segments=12)
                smy = self._catmull_rom(my_pts, num_segments=12)
                smxy = self._catmull_rom(mxy_pts, num_segments=12)
                layer.draw.line(smx, fill=color, width=size, joint='curve')
                layer.draw.line(smy, fill=color, width=size, joint='curve')
                layer.draw.line(smxy, fill=color, width=size, joint='curve')

        # * Menginisialisasi titik awal geser (pan) canvas menggunakan mouse
        def _panStart(self, event):
            if self.rulerActive:
                cx, cy = self._toImg(event.x, event.y)
                dist = math.hypot(cx - self.rulerX, cy - self.rulerY)
                if dist < 30 / self.zoom:
                    self.rulerIsDragging = True
                    self._px = cx
                    self._py = cy
                    return
            
            w  = self.tkCanvas.winfo_width()
            h  = self.tkCanvas.winfo_height()
            sw = int(self.CW * self.zoom)
            sh = int(self.CH * self.zoom)
            ox = self.offsetX if self.offsetX is not None else (w - sw) // 2
            oy = self.offsetY if self.offsetY is not None else (h - sh) // 2
            self._px = event.x - ox
            self._py = event.y - oy

        # * Menggeser posisi canvas sesuai pergerakan mouse drag
        def _panMove(self, event):
            if self.rulerIsDragging:
                cx, cy = self._toImg(event.x, event.y)
                self.rulerX = cx
                self.rulerY = cy
                self._scheduleRender(fast=True)
                return

            self.offsetX = event.x - self._px
            self.offsetY = event.y - self._py
            self._scheduleRender(fast=True)

        # * Mengatur tingkat perbesaran (zoom) canvas menggunakan scroll wheel
        def _onScroll(self, event):
            f = 1.12 if event.delta > 0 else 1/1.12
            new_zoom = max(0.05, min(12.0, self.zoom * f))
            
            # Init offset jika masih None (pertama kali zoom)
            if self.offsetX is None:
                w_init = self.tkCanvas.winfo_width() or 800
                h_init = self.tkCanvas.winfo_height() or 600
                sw_init = max(1, int(self.CW * self.zoom))
                sh_init = max(1, int(self.CH * self.zoom))
                self.offsetX = (w_init - sw_init) // 2
                self.offsetY = (h_init - sh_init) // 2
            
            # Zoom toward cursor position (keep same image point under mouse)
            w = self.tkCanvas.winfo_width() or 800
            h = self.tkCanvas.winfo_height() or 600
            sw = max(1, int(self.CW * self.zoom))
            sh = max(1, int(self.CH * self.zoom))
            ox = self.offsetX
            oy = self.offsetY
            
            # Image coords under mouse before zoom
            img_x = (event.x - ox) / self.zoom
            img_y = (event.y - oy) / self.zoom
            
            self.zoom = new_zoom
            
            # New offset to keep same image pos under mouse
            nsw = max(1, int(self.CW * self.zoom))
            nsh = max(1, int(self.CH * self.zoom))
            self.offsetX = event.x - img_x * self.zoom
            self.offsetY = event.y - img_y * self.zoom
            
            # Clamp offset to prevent excessive pan beyond canvas
            margin = 0.15
            if nsw > w:
                min_ox = -(nsw - w) - int(w * margin)
                max_ox = int(w * margin)
            else:
                min_ox = -(int(nsw * margin))
                max_ox = w - nsw + int(nsw * margin)
            if nsh > h:
                min_oy = -(nsh - h) - int(h * margin)
                max_oy = int(h * margin)
            else:
                min_oy = -(int(nsh * margin))
                max_oy = h - nsh + int(nsh * margin)
            self.offsetX = max(min_ox, min(max_ox, self.offsetX))
            self.offsetY = max(min_oy, min(max_oy, self.offsetY))
            
            if self.zoomLbl:
                self.zoomLbl.config(text=f"{int(self.zoom * 100)}%")
            self._scheduleRender(fast=True)

        def _onHover(self, event):
            x, y = self._toImg(event.x, event.y)
            self.coordLbl.config(text=f"{int(x)}, {int(y)}")

        def _pt(self, x, y):
            if self.startTime == 0.0:
                self.startTime = time.time()
            return {"x": x, "y": y, "color": self.brushColor,
                    "size": self.brushSize, "opacity": self.brushOpacity,
                    "mode": self.tool, "layer": self.activeIdx,
                    "layer_name": self.layers[self.activeIdx].name,
                    "t": time.time() - self.startTime}

        # ──────── DRAWING ────────
        def _applyPoint(self, x, y):
            layer = self.layers[self.activeIdx]
            if layer.locked: return
            r = max(1, self.brushSize // 2)
            color = self._rgba(self.brushColor, self.brushOpacity)
            if self.brushHardness < 100 and self.tool != 'eraser':
                self._paintSoft(layer, x, y, r, color, self.brushHardness)
            else:
                self._paint(layer, x, y, r, color)
            if self.symmetry:
                self._paintSym(layer, x, y, r, color)
            self._cacheDirty = True

        def _drawLineOnLayer(self, layer, pts, color, width):
            """Paint an anti-aliased, round-capped stroke onto ``layer``.

            Pillow's normal line primitive leaves square caps and hard pixel edges.
            Drawing the whole segment into a local high-resolution buffer, then
            downsampling once, keeps both the edge and every join smooth.
            """
            if len(pts) < 2:
                return
            if width <= 1:
                # Crisp 1 px geometry: anti-aliasing would turn black into grey.
                layer.draw.line([(round(x), round(y)) for x, y in pts], fill=color,
                                width=1, joint='curve')
                layer.draw = ImageDraw.Draw(layer.image)
                return
            if len(color) == 4 and color[3] == 0:
                layer.draw.line(pts, fill=color, width=width, joint='curve')
                layer.draw = ImageDraw.Draw(layer.image)
                return

            SS = max(2, min(24, self.drawQuality * 2))
            if self.drawQuality <= 1:
                layer.draw.line(pts, fill=color, width=width, joint='curve')
                layer.draw = ImageDraw.Draw(layer.image)
                return

            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            radius = max(0.5, width / 2)
            pad = int(math.ceil(radius)) + 3
            x0 = max(0, int(math.floor(min(xs) - pad)))
            y0 = max(0, int(math.floor(min(ys) - pad)))
            x1 = min(self.CW, int(math.ceil(max(xs) + pad)))
            y1 = min(self.CH, int(math.ceil(max(ys) + pad)))
            bw, bh = x1 - x0, y1 - y0
            if bw <= 0 or bh <= 0:
                return

            buf = Image.new("RGBA", (bw * SS, bh * SS), (0, 0, 0, 0))
            draw = ImageDraw.Draw(buf)
            ss_pts = [((px - x0) * SS, (py - y0) * SS) for px, py in pts]
            ss_width = max(1, int(round(width * SS)))
            draw.line(ss_pts, fill=color, width=ss_width, joint='curve')
            # PIL's line ends are square.  Explicit caps also hide tiny seams when
            # consecutive pointer events are rendered as separate segments.
            cap_radius = ss_width / 2
            for px, py in ss_pts:
                draw.ellipse((px-cap_radius, py-cap_radius,
                            px+cap_radius, py+cap_radius), fill=color)
            stamp = buf.resize((bw, bh), Image.LANCZOS)
            layer.image.alpha_composite(stamp, (x0, y0))
            layer.draw = ImageDraw.Draw(layer.image)

        def _eraseMask(self, layer, mask, box=None):
            # Gunakan Image.composite agar lebih reliable daripada paste
            # Pastikan mask dalam mode 'L'
            if mask.mode != 'L':
                mask = mask.convert('L')
            if box is None:
                # Full-canvas path (kept for compatibility with any external callers)
                transparent = Image.new("RGBA", layer.image.size, (0, 0, 0, 0))
                layer.image = Image.composite(transparent, layer.image, mask)
            else:
                # Region path: only the bounding box around the eraser is touched.
                # The old full-canvas mask (one allocation per mouse event) made
                # erasing on large canvases crawl; this keeps it near-instant.
                x0, y0, x1, y1 = box
                if x1 <= x0 or y1 <= y0:
                    return
                region = layer.image.crop((x0, y0, x1, y1))
                transparent = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
                region = Image.composite(transparent, region, mask)
                layer.image.paste(region, (x0, y0))
            layer.draw = ImageDraw.Draw(layer.image)
            self._cacheDirty = True

        def _eraseCircle(self, layer, x, y, r, hardness=100):
            pad = int(math.ceil(r)) + 1
            x0 = max(0, int(round(x - r)) - pad)
            y0 = max(0, int(round(y - r)) - pad)
            x1 = min(layer.image.width,  int(round(x + r)) + pad)
            y1 = min(layer.image.height, int(round(y + r)) + pad)
            if x1 <= x0 or y1 <= y0:
                return
            mask = Image.new("L", (x1 - x0, y1 - y0), 0)
            draw = ImageDraw.Draw(mask)
            ox = x - x0
            oy = y - y0
            if hardness >= 100:
                draw.ellipse([int(round(ox - r)), int(round(oy - r)),
                              int(round(ox + r)), int(round(oy + r))], fill=255)
            else:
                softness = (100 - hardness) / 100.0
                inner_r = max(1, int(r * (1 - softness * 0.6)))
                for ring_r in range(int(round(r)), inner_r - 1, -1):
                    frac = (ring_r - inner_r) / max(1, int(round(r)) - inner_r)
                    alpha = int(255 * (1 - frac * 0.5))
                    draw.ellipse([int(round(ox - ring_r)), int(round(oy - ring_r)),
                                  int(round(ox + ring_r)), int(round(oy + ring_r))], fill=alpha)
            self._eraseMask(layer, mask, (x0, y0, x1, y1))

        def _eraseLine(self, layer, pts, width):
            w = max(1, int(round(width)))
            if not pts:
                return
            pad = int(math.ceil(w / 2.0)) + 2
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            x0 = max(0, int(math.floor(min(xs))) - pad)
            y0 = max(0, int(math.floor(min(ys))) - pad)
            x1 = min(layer.image.width,  int(math.ceil(max(xs))) + pad)
            y1 = min(layer.image.height, int(math.ceil(max(ys))) + pad)
            if x1 <= x0 or y1 <= y0:
                return
            mask = Image.new("L", (x1 - x0, y1 - y0), 0)
            draw = ImageDraw.Draw(mask)
            if len(pts) == 1:
                x, y = pts[0]
                radius = w / 2
                draw.ellipse([int(round(x - x0 - radius)), int(round(y - y0 - radius)),
                              int(round(x - x0 + radius)), int(round(y - y0 + radius))], fill=255)
            else:
                int_pts = [(int(round(px - x0)), int(round(py - y0))) for px, py in pts]
                draw.line(int_pts, fill=255, width=w)
                if len(int_pts) >= 2:
                    cap = w / 2
                    xa, ya = int_pts[0]
                    xb, yb = int_pts[-1]
                    draw.ellipse([int(round(xa - cap)), int(round(ya - cap)),
                                  int(round(xa + cap)), int(round(ya + cap))], fill=255)
                    draw.ellipse([int(round(xb - cap)), int(round(yb - cap)),
                                  int(round(xb + cap)), int(round(yb + cap))], fill=255)
            self._eraseMask(layer, mask, (x0, y0, x1, y1))

        def _applyLine(self, x1, y1, x2, y2):
            layer = self.layers[self.activeIdx]
            if layer.locked: return
            self._cacheDirty = True
            color = (0,0,0,0) if self.tool == "eraser" else self._rgba(self.brushColor, self.brushOpacity)

            # The live path must stay cheap: it is only a preview and gets
            # replaced by the full supersampled stroke on mouse-up.  Performing a
            # 4–8x resize on every pointer event can starve Tk's input loop.
            if self.stabilizerMethod == "Real-time":
                width = max(1, self.brushSize)
                if self.tool == "eraser":
                    def paint_segment(a1, b1, a2, b2):
                        self._eraseLine(layer, [(a1, b1), (a2, b2)], width)
                else:
                    radius = width / 2
                    def paint_segment(a1, b1, a2, b2):
                        if width == 1:
                            layer.draw.line((round(a1), round(b1), round(a2), round(b2)),
                                            fill=color, width=1)
                            return
                        layer.draw.line((a1, b1, a2, b2), fill=color, width=width, joint="curve")
                        layer.draw.ellipse((a1-radius, b1-radius, a1+radius, b1+radius), fill=color)
                        layer.draw.ellipse((a2-radius, b2-radius, a2+radius, b2+radius), fill=color)
                paint_segment(x1, y1, x2, y2)
                if self.symmetry:
                    paint_segment(self.CW-x1, y1, self.CW-x2, y2)
                    paint_segment(x1, self.CH-y1, x2, self.CH-y2)
                    paint_segment(self.CW-x1, self.CH-y1, self.CW-x2, self.CH-y2)
                if self.tool != "eraser":
                    layer.draw = ImageDraw.Draw(layer.image)
                return
            
            dist = math.hypot(x2 - x1, y2 - y1)
            sub_segments = max(16, int(dist * 1.5))
            dx = (x2 - x1) / sub_segments
            dy = (y2 - y1) / sub_segments
            
            pts = [(x1 + dx * i, y1 + dy * i) for i in range(sub_segments + 1)]
            if self.tool == "eraser":
                self._eraseLine(layer, pts, self.brushSize)
            else:
                self._drawLineOnLayer(layer, pts, color, self.brushSize)
            
            if self.symmetry:
                mx1, my1 = self.CW - x1, self.CH - y1
                mx2, my2 = self.CW - x2, self.CH - y2
                dx_m = (mx2 - mx1) / sub_segments
                dy_m = (my2 - my1) / sub_segments
                mpts = [(mx1 + dx_m * i, my1 + dy_m * i) for i in range(sub_segments + 1)]
                if self.tool == "eraser":
                    self._eraseLine(layer, mpts, self.brushSize)
                else:
                    self._drawLineOnLayer(layer, mpts, color, self.brushSize)
                
                xpts = [(self.CW - (x1 + dx * i), y1 + dy * i) for i in range(sub_segments + 1)]
                if self.tool == "eraser":
                    self._eraseLine(layer, xpts, self.brushSize)
                else:
                    self._drawLineOnLayer(layer, xpts, color, self.brushSize)
                
                ypts = [(x1 + dx * i, self.CH - (y1 + dy * i)) for i in range(sub_segments + 1)]
                if self.tool == "eraser":
                    self._eraseLine(layer, ypts, self.brushSize)
                else:
                    self._drawLineOnLayer(layer, ypts, color, self.brushSize)
            if self.tool != "eraser":
                layer.draw = ImageDraw.Draw(layer.image)

        def _paint(self, layer, x, y, r, color):
            if self.tool == "eraser":
                self._eraseCircle(layer, x, y, r, self.brushHardness)
            elif self.tool == "smudge":
                self._smudge(layer, int(x), int(y), r)
            elif self.tool == "pencil":
                # Pencil: thinner, sharper, slight jitter for natural look
                pr = max(1, r // 2)
                layer.draw.ellipse([x-pr, y-pr, x+pr, y+pr], fill=(color[0], color[1], color[2], min(255, color[3] + 20)))
            else:
                layer.draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

    # === Catmull-Rom spline interpolation for smooth curves ===
        def _catmull_rom(self, pts, num_segments=24):
            if not pts or len(pts) < 2:
                return pts
            if len(pts) == 2:
                result = []
                for i in range(num_segments + 1):
                    t = i / num_segments
                    x = pts[0][0] + (pts[1][0] - pts[0][0]) * t
                    y = pts[0][1] + (pts[1][1] - pts[0][1]) * t
                    result.append((x, y))
                return result
            result = []
            n = len(pts)
            for i in range(n - 1):
                p0 = pts[max(0, i - 1)]
                p1 = pts[i]
                p2 = pts[i + 1]
                p3 = pts[min(n - 1, i + 2)]
                for j in range(num_segments):
                    t = j / num_segments
                    t2 = t * t
                    t3 = t2 * t
                    x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                            (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                            (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                    y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                            (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                            (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                    result.append((x, y))
            result.append(pts[-1])
            return result

        # === Painter: Soft brush (hardness < 100) ===
            # Draw a soft-edged brush using filled ellipses at graduated alpha
            if r <= 1:
                layer.draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
                return
            softness = (100 - hardness) / 100.0
            inner_r = max(1, int(r * (1 - softness * 0.6)))
            # Draw from outermost ring inward so inner rings paint on top
            for ring_r in range(r, inner_r - 1, -1):
                frac = (ring_r - inner_r) / max(1, r - inner_r)
                alpha = int(color[3] * (1 - frac * 0.5))
                clr = (color[0], color[1], color[2], alpha)
                layer.draw.ellipse([x-ring_r, y-ring_r, x+ring_r, y+ring_r], fill=clr)
            # Core: full opacity
            if inner_r > 0:
                layer.draw.ellipse([x-inner_r, y-inner_r, x+inner_r, y+inner_r], fill=color)

        def _paintSoft(self, layer, x, y, r, color, hardness):
            # Draw a soft-edged brush using filled ellipses at graduated alpha
            if r <= 1:
                layer.draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
                return
            softness = (100 - hardness) / 100.0
            inner_r = max(1, int(r * (1 - softness * 0.6)))
            # Draw from outermost ring inward so inner rings paint on top
            for ring_r in range(r, inner_r - 1, -1):
                frac = (ring_r - inner_r) / max(1, r - inner_r)
                alpha = int(color[3] * (1 - frac * 0.5))
                clr = (color[0], color[1], color[2], alpha)
                layer.draw.ellipse([x-ring_r, y-ring_r, x+ring_r, y+ring_r], fill=clr)
            # Core: full opacity
            if inner_r > 0:
                layer.draw.ellipse([x-inner_r, y-inner_r, x+inner_r, y+inner_r], fill=color)

        def _floodFill(self, image, x, y, target, replacement, thresh=30):
            if target == replacement:
                return
            width, height = image.size
            data = image.load()
            sq_thresh = thresh * thresh
            def similar(a, b):
                return ((a[0]-b[0])**2 + (a[1]-b[1])**2 +
                        (a[2]-b[2])**2 + (a[3]-b[3])**2) <= sq_thresh

            seen = bytearray(width * height)
            stack = [(x, y)]
            while stack:
                px, py = stack.pop()
                idx = px + py * width
                if seen[idx]:
                    continue
                seen[idx] = 1
                current = data[px, py]
                if not similar(current, target):
                    continue
                data[px, py] = replacement
                if px > 0:
                    stack.append((px - 1, py))
                if px + 1 < width:
                    stack.append((px + 1, py))
                if py > 0:
                    stack.append((px, py - 1))
                if py + 1 < height:
                    stack.append((px, py + 1))

        def _paintSoftSS(self, draw, x2, y2, r2, color, hardness):
            """Super-sampled soft brush: paint on 2x temp draw buffer."""
            if r2 <= 1:
                draw.ellipse([x2-r2, y2-r2, x2+r2, y2+r2], fill=color)
                return
            softness = (100 - hardness) / 100.0
            inner_r2 = max(1, int(r2 * (1 - softness * 0.6)))
            for ring_r in range(r2, inner_r2 - 1, -1):
                frac = (ring_r - inner_r2) / max(1, r2 - inner_r2)
                alpha = int(color[3] * (1 - frac * 0.5))
                clr = (color[0], color[1], color[2], alpha)
                draw.ellipse([x2-ring_r, y2-ring_r, x2+ring_r, y2+ring_r], fill=clr)
            if inner_r2 > 0:
                draw.ellipse([x2-inner_r2, y2-inner_r2, x2+inner_r2, y2+inner_r2], fill=color)

        def _paintSym(self, layer, x, y, r, color):
            mx, my = self.CW - x, self.CH - y
            self._paint(layer, mx, y,  r, color)
            self._paint(layer, x,  my, r, color)
            self._paint(layer, mx, my, r, color)

        def _smudge(self, layer, x, y, r):
            box = (max(0,x-r), max(0,y-r),
                min(layer.image.width,x+r), min(layer.image.height,y+r))
            crop    = layer.image.crop(box)
            blurred = crop.filter(ImageFilter.BLUR)
            layer.image.paste(blurred, box)
            layer.draw = ImageDraw.Draw(layer.image)

        def _eyedrop(self, x, y):
            img = self._composite()
            px  = max(0, min(int(x), self.CW-1))
            py  = max(0, min(int(y), self.CH-1))
            r, g, b = img.getpixel((px, py))
            self._setColor("#{:02x}{:02x}{:02x}".format(r, g, b))
            self.tool = "brush"; self.toolVar.set("brush")

        def _fill(self, x, y):
            layer = self.layers[self.activeIdx]
            if layer.locked: return
            if not (0 <= x < self.CW and 0 <= y < self.CH):
                return
            replacement = self._rgba(self.brushColor, self.brushOpacity)
            target = layer.image.getpixel((x, y))
            if target == replacement:
                return
            self._floodFill(layer.image, x, y, target, replacement, thresh=30)
            layer.draw = ImageDraw.Draw(layer.image)
            self._cacheDirty = True
            self._scheduleRender(fast=False)

        def _rgba(self, hex_, alpha=255):
            h = hex_.lstrip("#")
            return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), alpha)

        # ──────── RENDER (optimized) ────────
        def _composite(self, include_vectors=False):
            # Timelapse never touches the live artwork.  During playback we only
            # composite its separate, temporary layer set.
            layers = self._playbackLayers if self._playbackLayers is not None else self.layers
            if self._playbackLayers is not None:
                base = Image.new("RGBA", (self.CW, self.CH), (255, 255, 255, 255))
                for layer in reversed(layers):
                    if not layer.visible:
                        continue
                    img = layer.image
                    if layer.opacity < 255:
                        img = img.copy()
                        alpha = img.getchannel("A").point(lambda p: int(p * layer.opacity / 255))
                        img.putalpha(alpha)
                    base = Image.alpha_composite(base, img)
                return base.convert("RGB")

            # Kembalikan cache jika masih valid (zoom/pan tidak butuh recomposite)
            if not include_vectors and not self._cacheDirty and self._cachedComposite is not None:
                return self._cachedComposite
            
            # Background putih di RGBA
            base = Image.new("RGBA", (self.CW, self.CH), (255, 255, 255, 255))
            
            # Composite semua layer
            # Index 0 is visually highest, matching the layer panel order.
            for layer in reversed(self.layers):
                if not layer.visible: continue
                img = layer.image
                if layer.opacity < 255:
                    img = img.copy()
                    r, g, b, a = img.split()
                    a = a.point(lambda p: int(p * layer.opacity / 255))
                    img.putalpha(a)
                base = Image.alpha_composite(base, img)

            if include_vectors:
                self._rasterizeVectorStrokes(base)
            
            rgb = base.convert("RGB")
            if not include_vectors:
                self._cachedComposite = rgb
                self._cacheDirty = False
            return rgb

        def _isVectorStroke(self, stroke):
            return bool(stroke and (stroke[0].get("mode") == "vector_pen" or stroke[0].get("vector", False)))

        def _isStrokeLayerVisible(self, stroke):
            if not stroke:
                return False
            layer_idx = stroke[0].get("layer")
            layer_name = stroke[0].get("layer_name")
            layers = self._playbackLayers if self._playbackLayers is not None else self.layers
            if isinstance(layer_idx, int) and 0 <= layer_idx < len(layers):
                if layers[layer_idx].name == layer_name:
                    return layers[layer_idx].visible
            for layer in layers:
                if layer.name == layer_name:
                    return layer.visible
            return True

        def _computeVectorSegments(self):
            """One pass over strokeHistory producing per-index segment lists for
            every vector stroke, masked by eraser strokes drawn before it (and by
            the eraser stroke currently in progress).  Uses an EraseGrid so the
            pass stays fast even with hundreds of strokes.
            """
            grids = {}
            segments = {}
            # The live eraser stroke (mouse still down) is the newest stroke, so
            # it covers every committed vector stroke (drawn before it).
            if (self.tool == "eraser" and self.currentStroke
                    and self.currentStroke[0].get("mode") == "eraser"):
                lyr = self.currentStroke[0].get("layer", 0)
                grid = grids.setdefault(lyr, EraseGrid())
                r = max(1.0, self.currentStroke[0].get("size", self.brushSize) / 2.0)
                for p in self.currentStroke:
                    grid.add(p["x"], p["y"], r)
            # Walk history backwards: by the time we reach a vector stroke, the
            # grids hold every eraser stroke drawn *after* it, which is exactly
            # the coverage that should mask it.
            for idx in range(len(self.strokeHistory) - 1, -1, -1):
                stroke = self.strokeHistory[idx]
                if not stroke:
                    continue
                if stroke[0].get("mode") == "eraser":
                    lyr = stroke[0].get("layer", 0)
                    grid = grids.setdefault(lyr, EraseGrid())
                    r = max(1.0, stroke[0].get("size", self.brushSize) / 2.0)
                    for p in stroke:
                        grid.add(p["x"], p["y"], r)
                    continue
                if not self._isVectorStroke(stroke):
                    continue
                lyr = stroke[0].get("layer", 0)
                grid = grids.get(lyr)
                raw = [(p["x"], p["y"]) for p in stroke]
                if grid is None:
                    # No eraser coverage: smooth the whole stroke in one pass.
                    # Cache it since vector strokes are immutable once recorded.
                    key = id(stroke)
                    cached = self._smoothCache.get(key)
                    if cached is None:
                        cached = self._catmull_rom(raw, 6) if len(raw) > 2 else raw
                        self._smoothCache[key] = cached
                    segments[idx] = [cached]
                    continue
                half = max(0.5, max((p.get("size", 1) for p in stroke),
                                    default=1) / 2.0)
                # Mask using the raw points (already dense from mouse input);
                # smoothing is applied per surviving segment afterwards.
                out = []
                current = []
                for (x, y) in raw:
                    if grid.query(x, y, half):
                        if len(current) >= 2:
                            out.append(current)
                        current = []
                    else:
                        current.append((x, y))
                if len(current) >= 2:
                    out.append(current)
                smoothed = []
                for seg in out:
                    if len(seg) > 2:
                        smoothed.append(self._catmull_rom(seg, 6))
                    else:
                        smoothed.append(seg)
                segments[idx] = smoothed
            return segments

        def _rasterizeVectorStrokes(self, image):
            """Raster fallback used only for PNG export and project previews."""
            draw = ImageDraw.Draw(image)
            segs = self._computeVectorSegments()
            for idx, stroke in enumerate(self.strokeHistory):
                if idx not in segs:
                    continue
                if not self._isStrokeLayerVisible(stroke):
                    continue
                first = stroke[0]
                color = self._rgba(first.get("color", "#000000"), first.get("opacity", 255))
                width = max(1, int(first.get("size", 1)))
                for seg in segs[idx]:
                    if len(seg) == 1:
                        x, y = seg[0]
                        draw.ellipse((x - width / 2, y - width / 2,
                                      x + width / 2, y + width / 2), fill=color)
                    elif len(seg) > 1:
                        draw.line(seg, fill=color, width=width, joint="curve")

        def _drawVectorOverlay(self, view=None):
            """Screen-space vector rendering: stays smooth at any canvas zoom."""
            if self.isPlaying:
                return
            segs = self._computeVectorSegments()
            if not segs:
                return
            if view is not None:
                ox, oy, vx1, vy1, sx, sy, _ = view
                def to_screen(x, y):
                    return ox + (x - vx1) * sx, oy + (y - vy1) * sy
            else:
                to_screen = self._toScreen
            for idx, stroke in enumerate(self.strokeHistory):
                if idx not in segs:
                    continue
                if not self._isStrokeLayerVisible(stroke):
                    continue
                first = stroke[0]
                width = max(1.0, first.get("size", 1) * self.zoom)
                for seg in segs[idx]:
                    pts = [to_screen(x, y) for x, y in seg]
                    flat_pts = []
                    for px, py in pts:
                        if width <= 1.0:
                            flat_pts.extend((round(px), round(py)))
                        else:
                            flat_pts.extend((px, py))
                    if len(flat_pts) == 2:
                        px, py = flat_pts[0], flat_pts[1]
                        r = max(1.0, width / 2.0)
                        self.tkCanvas.create_oval(px - r, py - r, px + r, py + r,
                                                fill=first.get("color", "#000000"), outline="")
                        continue
                    if len(flat_pts) < 4:
                        continue
                    if width <= 1.0:
                        self.tkCanvas.create_line(*flat_pts,
                                                fill=first.get("color", "#000000"),
                                                width=1, capstyle="round", joinstyle="round",
                                                smooth=False)
                    else:
                        self.tkCanvas.create_line(*flat_pts,
                                                fill=first.get("color", "#000000"),
                                                width=width, capstyle="round", joinstyle="round",
                                                smooth=True, splinesteps=24)

        def _scheduleRender(self, fast=True):
            self._nextRenderFast = fast
            if self._renderPending and hasattr(self, '_pendingAfterId'):
                try:
                    self.root.after_cancel(self._pendingAfterId)
                except Exception:
                    pass
            self._renderPending = True
            self._pendingAfterId = self.root.after(2, self._doRender)

        def _scheduleQualityRender(self, delay=120):
            """Debounce: upgrade ke LANCZOS setelah brush berhenti bergerak sebentar."""
            if self.renderQuality != "balanced":
                return
            if self._qualityAfterId is not None:
                try:
                    self.root.after_cancel(self._qualityAfterId)
                except Exception:
                    pass
            self._qualityAfterId = self.root.after(delay, self._doQualityRender)

        def _doQualityRender(self):
            self._qualityAfterId = None
            self._scheduleRender(fast=False)

        # * Melakukan rendering gabungan semua layer gambar ke widget canvas
        def _doRender(self):
            self._renderPending = False
            self._lastRender = time.time()
            w  = self.tkCanvas.winfo_width()  or 800
            h  = self.tkCanvas.winfo_height() or 600
            ox, oy, vx1, vy1, sx, sy, cropped = self._viewParams()
            sw = max(1, int(self.CW * self.zoom))
            sh = max(1, int(self.CH * self.zoom))

            composite = self._composite()
            image_ox, image_oy = ox, oy
            
            # High zoom: render only visible portion at viewport resolution (INSTANT)
            if cropped:
                vx2 = min(self.CW, vx1 + w / sx)
                vy2 = min(self.CH, vy1 + h / sy)
                crop = composite.crop((int(vx1), int(vy1), int(vx2), int(vy2)))
                filt = self._renderFilter(self._nextRenderFast)
                rw = max(1, int(round((vx2 - vx1) * sx)))
                rh = max(1, int(round((vy2 - vy1) * sy)))
                resized = crop.resize((rw, rh), filt)
                image_ox = int(round(ox))
                image_oy = int(round(oy))
            elif sw == self.CW and sh == self.CH:
                resized = composite
            else:
                filt = self._renderFilter(self._nextRenderFast)
                resized = composite.resize((sw, sh), filt)
            self.tkPhoto = ImageTk.PhotoImage(resized)

            self.tkCanvas.delete("all")
            self.tkCanvas.config(bg="#ffffff")
            
            # Gambar image
            self.tkCanvas.create_image(image_ox, image_oy, anchor="nw", image=self.tkPhoto)
            self._drawVectorOverlay((ox, oy, vx1, vy1, sx, sy, cropped))
            
            # Border with shadow effect (double border)
            self.tkCanvas.create_rectangle(ox+2, oy+2, ox+sw+2, oy+sh+2,
                                            outline="#000000", width=1, stipple="gray25")
            self.tkCanvas.create_rectangle(ox-1, oy-1, ox+sw+1, oy+sh+1,
                                            outline="#666666", width=1)
            self.tkCanvas.create_rectangle(ox, oy, ox+sw, oy+sh,
                                            outline=C["card"], width=1)

            if self.symmetry:
                cx = ox + sw//2
                cy = oy + sh//2
                self.tkCanvas.create_line(cx, oy, cx, oy+sh,
                                        fill=C["accent"], width=1, dash=(6,4))
                self.tkCanvas.create_line(ox, cy, ox+sw, cy,
                                        fill=C["accent"], width=1, dash=(6,4))

            # Decorative frame overlay
            self._drawFrame(self.tkCanvas, ox, oy, sw, sh)

            # Selection is a non-destructive overlay: click selects a recorded
            # stroke, while dragging creates a free rectangular area.
            if self.selectionRect:
                x1, y1, x2, y2 = self.selectionRect
                sx1, sy1 = self._toScreen(x1, y1)
                sx2, sy2 = self._toScreen(x2, y2)
                if self._selectionPayload is not None:
                    pw = max(1, int(abs(sx2 - sx1)))
                    ph = max(1, int(abs(sy2 - sy1)))
                    preview = self._selectionPayload.resize((pw, ph), Image.LANCZOS)
                    self.selectionPhoto = ImageTk.PhotoImage(preview)
                    self.tkCanvas.create_image(min(sx1, sx2), min(sy1, sy2), anchor="nw",
                                            image=self.selectionPhoto)
                self.tkCanvas.create_rectangle(sx1, sy1, sx2, sy2, outline=C["accent"],
                                            width=2, dash=(6, 3))
                self.tkCanvas.create_rectangle(sx1 + 2, sy1 + 2, sx2 - 2, sy2 - 2,
                                            outline="#ffffff", width=1, dash=(6, 3))
                hs = 4
                for hx, hy in [(sx1, sy1), (sx2, sy1), (sx1, sy2), (sx2, sy2)]:
                    self.tkCanvas.create_rectangle(hx - hs, hy - hs, hx + hs, hy + hs,
                                                fill=C["accent"], outline="#ffffff", width=1)

            # Ruler visual guide
            if self.rulerActive:
                rad = math.radians(self.rulerAngle)
                dx = math.cos(rad)
                dy = math.sin(rad)
                length = max(self.CW, self.CH) * 2
                rx1 = self.rulerX - dx * length
                ry1 = self.rulerY - dy * length
                rx2 = self.rulerX + dx * length
                ry2 = self.rulerY + dy * length
                
                vx1, vy1 = self._toScreen(rx1, ry1)
                vx2, vy2 = self._toScreen(rx2, ry2)
                
                self.tkCanvas.create_line(vx1, vy1, vx2, vy2, fill="#ff3333", width=1, dash=(6,4))
                
                vcx, vcy = self._toScreen(self.rulerX, self.rulerY)
                self.tkCanvas.create_oval(vcx-6, vcy-6, vcx+6, vcy+6, fill="#ff3333", outline="#ffffff", width=1)

            # Preview current stroke cuma untuk Before-After mode
            # Real-time mode langsung draw ke layer, jadi nggak perlu preview
            if self.stabilizerMethod == "Before-After" and self.currentStroke:
                pts = [self._toScreen(pt["x"], pt["y"]) for pt in self.currentStroke]
                if len(pts) >= 2:
                    self.tkCanvas.create_line(pts, fill=self.brushColor, width=max(1.0, self.brushSize * sx), capstyle="round", joinstyle="round")

            if self._usingVectorRenderer() and self.currentStroke:
                pts = []
                for point in self.currentStroke:
                    px, py = self._toScreen(point["x"], point["y"])
                    pts.extend((px, py))
                if len(pts) >= 4:
                    self.tkCanvas.create_line(*pts, fill=self.brushColor,
                                            width=max(1.0, self.brushSize * self.zoom),
                                            capstyle="round", joinstyle="round",
                                            smooth=True, splinesteps=24)

            # Preview Shape Tool (2-Point Shapes)
            if self.tool == "shape" and self.shapeStartPoint and self.previewX is not None:
                vx1, vy1 = self._toScreen(self.shapeStartPoint[0], self.shapeStartPoint[1])
                vx2, vy2 = self._toScreen(self.previewX, self.previewY)
                w_line = max(1.0, self.brushSize * sx)
                
                if self.shapeMode == "line":
                    self.tkCanvas.create_line(vx1, vy1, vx2, vy2, fill=self.brushColor, width=w_line)
                elif self.shapeMode == "rect":
                    self.tkCanvas.create_rectangle(vx1, vy1, vx2, vy2, outline=self.brushColor, width=int(w_line))
                elif self.shapeMode == "circle":
                    r = math.hypot(vx2 - vx1, vy2 - vy1)
                    self.tkCanvas.create_oval(vx1 - r, vy1 - r, vx1 + r, vy1 + r, outline=self.brushColor, width=int(w_line))
                elif self.shapeMode == "hexagon":
                    cx, cy = (vx1 + vx2)/2, (vy1 + vy2)/2
                    rx, ry = abs(vx2 - vx1)/2, abs(vy2 - vy1)/2
                    hex_pts = []
                    for i in range(6):
                        t = 2 * math.pi * i / 6
                        hex_pts.append(cx + rx * math.cos(t))
                        hex_pts.append(cy + ry * math.sin(t))
                    self.tkCanvas.create_polygon(hex_pts, outline=self.brushColor, fill="", width=int(w_line))
                elif self.shapeMode == "arrow":
                    self.tkCanvas.create_line(vx1, vy1, vx2, vy2, fill=self.brushColor, width=w_line)
                    angle = math.atan2(vy2 - vy1, vx2 - vx1)
                    head_len = max(8.0, 15.0 * sx)
                    ax1 = vx2 - head_len * math.cos(angle - math.pi/6)
                    ay1 = vy2 - head_len * math.sin(angle - math.pi/6)
                    ax2 = vx2 - head_len * math.cos(angle + math.pi/6)
                    ay2 = vy2 - head_len * math.sin(angle + math.pi/6)
                    self.tkCanvas.create_line(vx2, vy2, ax1, ay1, fill=self.brushColor, width=w_line)
                    self.tkCanvas.create_line(vx2, vy2, ax2, ay2, fill=self.brushColor, width=w_line)
                elif self.shapeMode == "oval":
                    self.tkCanvas.create_oval(vx1, vy1, vx2, vy2, outline=self.brushColor, width=int(w_line))
                elif self.shapeMode == "rounded_rect":
                    self.tkCanvas.create_rectangle(vx1, vy1, vx2, vy2, outline=self.brushColor, width=int(w_line))
                elif self.shapeMode == "bubble":
                    self.tkCanvas.create_rectangle(vx1, vy1, vx2, vy2, outline=self.brushColor, width=int(w_line))

            # Preview Bezier Path (Pen Tool)
            if self.tool == "shape" and self.shapeMode == "bezier" and self.bezierAnchorPoints:
                if len(self.bezierAnchorPoints) >= 2:
                    pts = []
                    temp_pts = [self.bezierAnchorPoints[0]] + self.bezierAnchorPoints + [self.bezierAnchorPoints[-1]]
                    steps = 20
                    for i in range(1, len(temp_pts) - 2):
                        p0, p1, p2, p3 = temp_pts[i-1], temp_pts[i], temp_pts[i+1], temp_pts[i+2]
                        for step in range(steps + 1):
                            t = step / steps
                            t2 = t * t
                            t3 = t2 * t
                            f0 = -0.5*t3 + t2 - 0.5*t
                            f1 = 1.5*t3 - 2.5*t2 + 1.0
                            f2 = -1.5*t3 + 2.0*t2 + 0.5*t
                            f3 = 0.5*t3 - 0.5*t2
                            xi = p0[0]*f0 + p1[0]*f1 + p2[0]*f2 + p3[0]*f3
                            yi = p0[1]*f0 + p1[1]*f1 + p2[1]*f2 + p3[1]*f3
                            pts.append(self._toScreen(xi, yi))
                    if pts:
                        self.tkCanvas.create_line(pts, fill=self.brushColor, width=max(1.0, self.brushSize * sx))

                if self.previewX is not None:
                    last_pt = self.bezierAnchorPoints[-1]
                    vpx1, vpy1 = self._toScreen(last_pt[0], last_pt[1])
                    vpx2, vpy2 = self._toScreen(self.previewX, self.previewY)
                    self.tkCanvas.create_line(vpx1, vpy1, vpx2, vpy2, fill=self.brushColor, width=1, dash=(2,2))

                anchor_offset = 6
                for i, pt in enumerate(self.bezierAnchorPoints):
                    vpx, vpy = self._toScreen(pt[0], pt[1])
                    marker_y = vpy - anchor_offset
                    if i > 0:
                        prev_vpx, prev_vpy = self._toScreen(self.bezierAnchorPoints[i-1][0], self.bezierAnchorPoints[i-1][1])
                        self.tkCanvas.create_line(prev_vpx, prev_vpy, vpx, vpy, fill="#777777", width=1, dash=(4,4))
                    self.tkCanvas.create_oval(vpx - 4, marker_y - 4, vpx + 4, marker_y + 4, fill=C["accent"], outline="#ffffff")

            # Preview Polyline Path
            if self.tool == "shape" and self.shapeMode == "polyline" and self.polylinePoints:
                pts = []
                for pt in self.polylinePoints:
                    vpx, vpy = self._toScreen(pt[0], pt[1])
                    pts.append((vpx, vpy))
                    self.tkCanvas.create_oval(vpx - 4, vpy - 4, vpx + 4, vpy + 4, fill=C["accent"], outline="#ffffff")
                if len(pts) >= 2:
                    smooth_pts = self._smoothPolylineCorners(pts)
                    self.tkCanvas.create_line(smooth_pts, fill=self.brushColor, width=max(1.0, self.brushSize * sx), capstyle="round", joinstyle="round", smooth=True)
                
                if self.previewX is not None:
                    last_pt = self.polylinePoints[-1]
                    vpx1, vpy1 = self._toScreen(last_pt[0], last_pt[1])
                    vpx2, vpy2 = self._toScreen(self.previewX, self.previewY)
                    self.tkCanvas.create_line(vpx1, vpy1, vpx2, vpy2, fill=self.brushColor, width=1, dash=(2,2))

            if self.zoomLbl:
                self.zoomLbl.config(text=f"{int(self.zoom*100)}%")
            self._nextRenderFast = True

        # ──────── UNDO/REDO ────────
        def _saveUndo(self):
            snaps = [l.snapshot() for l in self.layers]
            history = list(self.strokeHistory)
            self.undoStack.append((snaps, history))
            if len(self.undoStack) > 256: self.undoStack.pop(0)
            self._queueUndoCache(snaps, history)
            self.redoStack.clear()

        def _queueUndoCache(self, snaps, history):
            """Write disk recovery data off the Tk input thread."""
            slot = self._undoCacheSlot
            self._undoCacheSlot = (slot + 1) % 256
            threading.Thread(target=self._writeUndoCache, args=(snaps, history, slot),
                            daemon=True).start()

        def _writeUndoCache(self, snaps, history, slot=None):
            """Persist one rotating undo snapshot in cache/<project> (256 slots)."""
            if slot is None:
                slot = self._undoCacheSlot
                self._undoCacheSlot = (slot + 1) % 256
            target = os.path.join(self.undoCacheDir, f"undo_{slot:03d}.json.gz")
            temp = target + ".tmp"
            payload = {
                "createdAt": datetime.now().isoformat(),
                "layers": [base64.b64encode(snapshot).decode("ascii") for snapshot in snaps],
                "strokeHistory": history,
            }
            try:
                with gzip.open(temp, "wt", encoding="utf-8") as cache_file:
                    json.dump(payload, cache_file, separators=(",", ":"))
                os.replace(temp, target)
            except OSError as exc:
                # Undo in memory must keep working even if a disk is unavailable.
                print(f"[WARN] Undo cache could not be written: {exc}")
                try:
                    if os.path.exists(temp):
                        os.remove(temp)
                except OSError:
                    pass

        def _restoreUndoCache(self):
            """Restore the last persisted Undo states for this project session."""
            entries = []
            try:
                for filename in os.listdir(self.undoCacheDir):
                    if not (filename.startswith("undo_") and filename.endswith(".json.gz")):
                        continue
                    path = os.path.join(self.undoCacheDir, filename)
                    with gzip.open(path, "rt", encoding="utf-8") as cache_file:
                        payload = json.load(cache_file)
                    layers = [base64.b64decode(item) for item in payload.get("layers", [])]
                    if layers:
                        entries.append((payload.get("createdAt", ""), filename,
                                        layers, payload.get("strokeHistory", [])))
            except (OSError, ValueError, gzip.BadGzipFile) as exc:
                print(f"[WARN] Undo cache could not be restored: {exc}")

            entries.sort(key=lambda item: item[0])
            self.undoStack = [(layers, history) for _, _, layers, history in entries[-256:]]
            if entries:
                latest_name = entries[-1][1]
                try:
                    self._undoCacheSlot = (int(latest_name[5:8]) + 1) % 256
                except ValueError:
                    self._undoCacheSlot = len(entries) % 256

        def _undo(self):
            if not self.undoStack: return
            self._cacheDirty = True
            self.redoStack.append(([l.snapshot() for l in self.layers], list(self.strokeHistory)))
            snaps, history = self.undoStack[-1]
            for i, l in enumerate(self.layers):
                if i < len(snaps): l.restore(snaps[i])
            self.strokeHistory = list(history)
            self.undoStack.pop()
            self._smoothCache.clear()
            if self.strokeLbl: self.strokeLbl.config(text=f"Strokes: {len(self.strokeHistory)}")
            self._scheduleRender(fast=False)

        def _redo(self):
            if not self.redoStack: return
            self._cacheDirty = True
            snaps_now = [l.snapshot() for l in self.layers]
            history_now = list(self.strokeHistory)
            self.undoStack.append((snaps_now, history_now))
            if len(self.undoStack) > 256: self.undoStack.pop(0)
            self._queueUndoCache(snaps_now, history_now)
            snaps, history = self.redoStack[-1]
            for i, l in enumerate(self.layers):
                if i < len(snaps): l.restore(snaps[i])
            self.strokeHistory = list(history)
            self.redoStack.pop()
            self._smoothCache.clear()
            if self.strokeLbl: self.strokeLbl.config(text=f"Strokes: {len(self.strokeHistory)}")
            self._scheduleRender(fast=False)

        # ──────── LAYERS ────────
        def _addLayer(self):
            self._cacheDirty = True
            name = simpledialog.askstring("Layer", "Layer name:",
                                        initialvalue=f"Layer {len(self.layers)+1}")
            if name:
                self._shiftTimelapseIndicesOnInsert(0)
                self.layers.insert(0, Layer(name, self.CW, self.CH))
                self.activeIdx   = 0
                self._refreshLayerPanel()
                self._scheduleRender(fast=False)

        def _delLayer(self):
            if len(self.layers) <= 1: return
            self._cacheDirty = True
            deleted_name = self.layers[self.activeIdx].name
            self.timelapseDisabledLayerNames.discard(deleted_name)
            self._shiftTimelapseIndicesOnDelete(self.activeIdx)

            # Hapus semua coretan/stroke yang pernah digambar pada layer ini dari strokeHistory
            target_idx = self.activeIdx
            self.strokeHistory = [
                st for st in self.strokeHistory
                if st and st[0].get("layer_name") != deleted_name and st[0].get("layer") != target_idx
            ]

            self.layers.pop(self.activeIdx)
            self.activeIdx   = min(self.activeIdx, len(self.layers)-1)
            self._refreshLayerPanel()
            if self.strokeLbl: self.strokeLbl.config(text=f"Strokes: {len(self.strokeHistory)}")
            self._scheduleRender(fast=False)

        def _moveLayer(self, d):
            self._cacheDirty = True
            i = self.activeIdx
            j = i + d
            if 0 <= j < len(self.layers):
                self.layers[i], self.layers[j] = self.layers[j], self.layers[i]
                self._swapTimelapseIndices(i, j)
                self.activeIdx   = j
                self._refreshLayerPanel()
                self._scheduleRender(fast=False)

        # * Mengimpor gambar eksternal ke dalam layer baru
        def _importImageToLayer(self, filePath=None):
            self._cacheDirty = True
            if filePath is None:
                filePath = filedialog.askopenfilename(
                    title="Import Image to Layer",
                    filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All Files", "*.*")]
                )
                if not filePath:
                    return
            
            try:
                importedImg = Image.open(filePath).convert("RGBA")
                fit = messagebox.askyesno("Import Options", "Fit image to canvas size?")
                
                self._saveUndo()
                layerName = f"Imported_{os.path.basename(filePath)[:12]}"
                newLayer = Layer(layerName, self.CW, self.CH)
                
                if fit:
                    importedImg.thumbnail((self.CW, self.CH), Image.Resampling.LANCZOS)
                    x = (self.CW - importedImg.width) // 2
                    y = (self.CH - importedImg.height) // 2
                    newLayer.image.paste(importedImg, (x, y), importedImg)
                else:
                    newLayer.image.paste(importedImg, (0, 0))
                
                newLayer.draw = ImageDraw.Draw(newLayer.image)
                self._shiftTimelapseIndicesOnInsert(self.activeIdx)
                self.layers.insert(self.activeIdx, newLayer)

                # Rekam peristiwa import ke strokeHistory agar muncul di timelapse
                if self.startTime == 0.0:
                    self.startTime = time.time()
                
                buf = io.BytesIO()
                newLayer.image.save(buf, format="PNG")
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                self.strokeHistory.append([{
                    "mode": "import_image",
                    "img": img_b64,
                    "layer_name": layerName,
                    "layer_idx": self.activeIdx,
                    "t": time.time() - self.startTime
                }])
                if self.strokeLbl: self.strokeLbl.config(text=f"Strokes: {len(self.strokeHistory)}")
                self._refreshLayerPanel()
                self._scheduleRender(fast=False)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import image: {str(e)}")

        # * Menangani perubahan opacity layer secara interaktif
        def _onLayerOpacityChange(self, val):
            self._cacheDirty = True
            opacityVal = int(float(val) * 2.55)
            self.layers[self.activeIdx].opacity = opacityVal
            self._scheduleRender(fast=True)
            self._updateLayerPercentLabel(self.activeIdx, int(float(val)))

        # * Memperbarui label teks persentase opacity secara efisien saat digeser
        def _updateLayerPercentLabel(self, idx, percent):
            if hasattr(self, "layerPercentLabels") and idx in self.layerPercentLabels:
                try:
                    self.layerPercentLabels[idx].config(text=f"{percent}%")
                except Exception:
                    pass

        def _refreshLayerPanel(self):
            for w in self.layerFrame.winfo_children():
                w.destroy()

            self.layerPercentLabels = {}
            self.layerThumbs = {}  # prevent PhotoImage GC
            for i, layer in enumerate(self.layers):
                isActive = (i == self.activeIdx)
                bg   = C["card"] if isActive else C["panel"]
                bdr  = C["accent"] if isActive else C["border"]

                row = tk.Frame(self.layerFrame, bg=bg, cursor="hand2",
                            highlightbackground=bdr, highlightthickness=1)
                row.pack(fill="x", pady=2)

                # Generate thumbnail preview
                thumb_size = 40
                try:
                    # Scale layer image down to thumbnail
                    img_w, img_h = layer.image.size
                    if img_w > 0 and img_h > 0 and (img_w > thumb_size or img_h > thumb_size):
                        ratio = min(thumb_size / img_w, thumb_size / img_h)
                        tw, th = max(1, int(img_w * ratio)), max(1, int(img_h * ratio))
                        thumb_img = layer.image.resize((tw, th), Image.LANCZOS)
                    else:
                        # Create empty thumbnail
                        thumb_img = Image.new("RGBA", (thumb_size, thumb_size), (0, 0, 0, 0))
                    
                    # Composite onto a dark base so transparent areas are visible
                    base = Image.new("RGBA", (thumb_size, thumb_size), (255, 255, 255, 255))
                    # Center the thumbnail on the base
                    tx = (thumb_size - thumb_img.width) // 2
                    ty = (thumb_size - thumb_img.height) // 2
                    base.paste(thumb_img, (tx, ty), thumb_img)
                    self.layerThumbs[i] = ImageTk.PhotoImage(base)
                except Exception:
                    dummy = Image.new("RGBA", (thumb_size, thumb_size), (255, 255, 255, 255))
                    self.layerThumbs[i] = ImageTk.PhotoImage(dummy)

                # Thumbnail label
                thumbLbl = tk.Label(row, image=self.layerThumbs[i], bg=bg,
                                    width=thumb_size, height=thumb_size, cursor="hand2")
                thumbLbl.pack(side="left", padx=(4, 6), pady=4)
                # Dim thumbnail when layer is hidden
                if not layer.visible:
                    thumbLbl.config(bg=C["canvas_bg"])

                # Visibility indicator
                vis = tk.Label(row, text="●" if layer.visible else "○",
                            bg=bg, fg=C["success"] if layer.visible else C["dim"],
                            font=("Segoe UI", 9), cursor="hand2", width=2, padx=0)
                vis.pack(side="left", pady=6, padx=(0, 2))
                vis.bind("<Button-1>", lambda e, idx=i: self._toggleVis(idx))

                # Layer name + opacity in a vertical stack
                infoFrame = tk.Frame(row, bg=bg)
                infoFrame.pack(side="left", fill="x", expand=True, pady=4)

                tk.Label(infoFrame, text=layer.name, bg=bg, fg=C["text"],
                        font=FONT, anchor="w").pack(fill="x")

                if i in self.timelapseDisabledLayers or layer.name in self.timelapseDisabledLayerNames:
                    tk.Label(infoFrame, text="TIMELAPSE OFF", bg=bg, fg=C["danger"],
                            font=FONT_XS, anchor="w").pack(fill="x")

                tk.Label(infoFrame, text=f"{int(layer.opacity/2.55)}%",
                        bg=bg, fg=C["dim"], font=FONT_SM, anchor="w").pack(fill="x")

                # Bind all descendants recursively so clicking anywhere selects the layer
                def _bind_select_all(w, idx=i):
                    try:
                        w.bind("<Button-1>", lambda e, idx=idx: self._selectLayer(idx))
                    except Exception:
                        pass
                    for c in w.winfo_children():
                        _bind_select_all(c, idx)
                _bind_select_all(row, i)
                # Only the compact visibility icon disables a layer.
                vis.bind("<Button-1>", lambda e, idx=i: self._toggleVis(idx))

        def _selectLayer(self, idx):
            self.activeIdx = idx
            opacityPercent = int(self.layers[idx].opacity / 2.55)
            self.layerOpacityVar.set(opacityPercent)
            self._refreshLayerPanel()

        def _onLayerPanelMouseWheel(self, event):
            delta = 0
            if event.num == 5 or event.delta < 0:
                delta = 1
            elif event.num == 4 or event.delta > 0:
                delta = -1
            self.layerCanvas.yview_scroll(delta, "units")
            return "break"

        def _shiftTimelapseIndicesOnInsert(self, idx):
            self.timelapseDisabledLayers = {i + 1 if i >= idx else i for i in self.timelapseDisabledLayers}

        def _shiftTimelapseIndicesOnDelete(self, idx):
            new_set = set()
            for i in self.timelapseDisabledLayers:
                if i == idx:
                    continue
                new_set.add(i - 1 if i > idx else i)
            self.timelapseDisabledLayers = new_set

        def _swapTimelapseIndices(self, a, b):
            new_set = set()
            for i in self.timelapseDisabledLayers:
                if i == a:
                    new_set.add(b)
                elif i == b:
                    new_set.add(a)
                else:
                    new_set.add(i)
            self.timelapseDisabledLayers = new_set

        def _armTimelapseLayerDisable(self, event=None):
            self._timelapseDisableArmed = True
            self.root.after(3000, lambda: setattr(self, "_timelapseDisableArmed", False))
            return "break"

        def _handleTimelapseToggleShortcut(self, event=None):
            # Same treatment for X: use the modifier state instead of depending on
            # Tk's inconsistent lowercase/uppercase key symbol on Windows.
            if event is not None and (event.state & 0x0001):
                return self._toggleTimelapseLayerSecret(event)
            return None

        def _toggleTimelapseLayerSecret(self, event=None):
            if not self._timelapseDisableArmed:
                messagebox.showinfo("Timelapse Layer", "Shortcut belum siap. Pilih layer, tekan Ctrl+Shift+Z, lalu Ctrl+Shift+X.")
                return
            self._timelapseDisableArmed = False
            layer_name = self.layers[self.activeIdx].name
            if (self.activeIdx in self.timelapseDisabledLayers
                    or layer_name in self.timelapseDisabledLayerNames):
                self.timelapseDisabledLayers.remove(self.activeIdx)
                self.timelapseDisabledLayerNames.discard(layer_name)
                note = f"'{layer_name}' AKTIF di timelapse."
            else:
                self.timelapseDisabledLayers.add(self.activeIdx)
                self.timelapseDisabledLayerNames.add(layer_name)
                note = f"'{layer_name}' TIDAK akan tampil di timelapse."
            self._refreshLayerPanel()
            self._save(showPopup=False)
            messagebox.showinfo("Timelapse Layer", note)
            return "break"

        def _toggleVis(self, idx):
            self._cacheDirty = True
            self.layers[idx].visible = not self.layers[idx].visible
            self._refreshLayerPanel()
            self._scheduleRender(fast=False)

        def _clearCanvas(self):
            if messagebox.askyesno("Clear", "Clear all layers?"):
                self._cacheDirty = True
                self._saveUndo()
                for l in self.layers:
                    l.image = Image.new("RGBA", (self.CW, self.CH), (0,0,0,0))
                    l.draw  = ImageDraw.Draw(l.image)
                self.strokeHistory.clear()
                self._smoothCache.clear()
                if self.strokeLbl: self.strokeLbl.config(text="Strokes: 0")
                self._scheduleRender(fast=False)

        # ──────── TIMELAPSE ────────
        def _startPlayback(self):
            if not self.strokeHistory:
                messagebox.showinfo("Timelapse", "Belum ada stroke yang direkam.")
                return
            if self.isPlaying: return
            self.isPlaying = True
            self.playBtn.config(text="▶  Playing...", state="disabled")
            threading.Thread(target=self._runPlayback, daemon=True).start()

        # * Menggambar garis lurus di layer aktif
        def _drawLineToLayer(self, x1, y1, x2, y2):
            layer = self.layers[self.activeIdx]
            if layer.locked: return
            self._cacheDirty = True
            color = self._rgba(self.brushColor, self.brushOpacity)
            self._drawLineOnLayer(layer, [(x1, y1), (x2, y2)], color, max(1, self.brushSize))
            if self.symmetry:
                self._drawLineOnLayer(layer, [(self.CW-x1, y1), (self.CW-x2, y2)], color, max(1, self.brushSize))
                self._drawLineOnLayer(layer, [(x1, self.CH-y1), (x2, self.CH-y2)], color, max(1, self.brushSize))
                self._drawLineOnLayer(layer, [(self.CW-x1, self.CH-y1), (self.CW-x2, self.CH-y2)], color, max(1, self.brushSize))
                    
        # * Menggambar kurva Bezier kuadratik di layer aktif
        def _drawBezierToLayer(self, p0, p1, p2):
            layer = self.layers[self.activeIdx]
            if layer.locked: return
            color = self._rgba(self.brushColor, self.brushOpacity)
            points = []
            for i in range(101):
                t = i / 100
                mt = 1 - t
                xi = mt*mt*p0[0] + 2*mt*t*p1[0] + t*t*p2[0]
                yi = mt*mt*p0[1] + 2*mt*t*p1[1] + t*t*p2[1]
                points.append((xi, yi))
            self._drawLineOnLayer(layer, points, color, max(1, self.brushSize))

        def _runPlayback(self):
            oldIdx = self.activeIdx
            self._playbackLayers = []
            for source_idx, source in enumerate(self.layers):
                temp = Layer(source.name, self.CW, self.CH)
                is_disabled = (source_idx in self.timelapseDisabledLayers
                            or source.name in self.timelapseDisabledLayerNames)
                temp.visible = not is_disabled
                temp.opacity = source.opacity
                self._playbackLayers.append(temp)
            self._cacheDirty = True
            self.root.after(0, lambda: self._scheduleRender(fast=False))

            try:
                total = len(self.strokeHistory)
                for si, stroke in enumerate(self.strokeHistory):
                    if not self.isPlaying:
                        break
                    self.root.after(0, lambda p=(si / total) * 100: self.progressVar.set(p))
                    if not stroke:
                        continue

                    mode = stroke[0].get("mode", "brush")
                    # Imported images record their destination as layer_idx rather
                    # than layer.  Using that same index for the skip check is what
                    # makes the secret timelapse disable work for reference layers.
                    recorded_idx = (stroke[0].get("layer_idx", 0)
                                    if mode == "import_image"
                                    else stroke[0].get("layer", 0))
                    recorded_name = stroke[0].get("layer_name")
                    if recorded_name:
                        for idx, candidate in enumerate(self._playbackLayers):
                            if candidate.name == recorded_name:
                                recorded_idx = idx
                                break
                    lIdx = min(max(0, recorded_idx), len(self._playbackLayers) - 1)
                    if (lIdx in self.timelapseDisabledLayers
                            or self._playbackLayers[lIdx].name in self.timelapseDisabledLayerNames):
                        continue
                    layer = self._playbackLayers[lIdx]
                    dur = max((stroke[-1].get("t", 0) - stroke[0].get("t", 0)), 0.02)

                    strokeDelay = min(0.05, max(0.005, dur / max(0.1, self.playSpeed * 5.0)))
                    if mode == "import_image":
                        try:
                            p0 = stroke[0]
                            target = min(max(0, p0.get("layer_idx", lIdx)), len(self._playbackLayers) - 1)
                            decoded = Image.open(io.BytesIO(base64.b64decode(p0["img"]))).convert("RGBA")
                            self._playbackLayers[target].image.alpha_composite(decoded, (0, 0))
                            self._playbackLayers[target].draw = ImageDraw.Draw(self._playbackLayers[target].image)
                        except Exception:
                            pass
                        self.root.after(0, lambda: self._scheduleRender(fast=True))
                        time.sleep(strokeDelay)
                    elif mode == "line":
                        p0 = stroke[0]
                        p1 = stroke[1] if len(stroke) > 1 else p0
                        self._drawPlaybackLine(layer, p0["x"], p0["y"], p1["x"], p1["y"], p0)
                        layer.draw = ImageDraw.Draw(layer.image)
                        self.root.after(0, lambda: self._scheduleRender(fast=True))
                        time.sleep(strokeDelay)
                    elif mode == "bezier":
                        p = stroke[0]
                        self._drawPlaybackBezier(layer, (p["x"], p["y"]), (p.get("cx"), p.get("cy")), (p.get("ex"), p.get("ey")), p, duration=dur)
                        layer.draw = ImageDraw.Draw(layer.image)
                    elif mode.startswith("shape_"):
                        p = stroke[0]
                        self._drawPlaybackShape(layer, mode.split("_", 1)[1], p["x"], p["y"], p.get("ex"), p.get("ey"), p, duration=dur)
                        layer.draw = ImageDraw.Draw(layer.image)
                    elif mode == "bezier_path":
                        self._drawPlaybackPath(layer, [(p["x"], p["y"]) for p in stroke], stroke[0], smooth=True, animate=False)
                        layer.draw = ImageDraw.Draw(layer.image)
                        self.root.after(0, lambda: self._scheduleRender(fast=True))
                        time.sleep(strokeDelay)
                    elif mode == "polyline":
                        self._drawPlaybackPath(layer, [(p["x"], p["y"]) for p in stroke], stroke[0], smooth=False, animate=False)
                        layer.draw = ImageDraw.Draw(layer.image)
                        self.root.after(0, lambda: self._scheduleRender(fast=True))
                        time.sleep(strokeDelay)
                    elif mode == "vector_pen" or self._isVectorStroke(stroke):
                        self._drawPlaybackPath(layer, [(p["x"], p["y"]) for p in stroke], stroke[0], smooth=True, animate=False)
                        layer.draw = ImageDraw.Draw(layer.image)
                        self.root.after(0, lambda: self._scheduleRender(fast=True))
                        time.sleep(strokeDelay)
                    else:
                        self._drawPlaybackStroke(layer, stroke, dur)
                if self.isPlaying:
                    self.root.after(0, lambda: self.progressVar.set(100))
            finally:
                self.isPlaying = False
                self.activeIdx = oldIdx
                self._playbackLayers = None
                self._cacheDirty = True
                self.root.after(0, lambda: self.playBtn.config(text="▶  Play Timelapse", state="normal"))
                self.root.after(0, lambda: self._scheduleRender(fast=False))

        def _drawPlaybackStroke(self, layer, stroke, duration):
            previous = None
            for pt in stroke:
                if not self.isPlaying:
                    break
                x, y = pt["x"], pt["y"]
                size = max(1, pt.get("size", self.brushSize))
                radius = size // 2
                if pt.get("mode") == "eraser":
                    if previous is None:
                        self._eraseCircle(layer, x, y, radius, hardness=100)
                    else:
                        self._eraseLine(layer, [previous, (x, y)], size)
                else:
                    color = self._rgba(pt.get("color", self.brushColor), pt.get("opacity", self.brushOpacity))
                    if previous is None:
                        radius = size // 2
                        layer.draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
                    else:
                        layer.draw.line((previous[0], previous[1], x, y), fill=color, width=max(1, size), joint="curve")
                        radius = size // 2
                        layer.draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
                layer.draw = ImageDraw.Draw(layer.image)
                previous = (x, y)
                self.root.after(0, lambda: self._scheduleRender(fast=True))
                time.sleep(max(0.001, duration / max(1, len(stroke)) / self.playSpeed))

        def _drawPlaybackLine(self, layer, x1, y1, x2, y2, style):
            width = max(1, int(style.get("size", self.brushSize)))
            color = self._rgba(style.get("color", self.brushColor), style.get("opacity", self.brushOpacity))
            layer.draw.line((x1, y1, x2, y2), fill=color, width=width)
            radius = width / 2
            layer.draw.ellipse((x1-radius, y1-radius, x1+radius, y1+radius), fill=color)
            layer.draw.ellipse((x2-radius, y2-radius, x2+radius, y2+radius), fill=color)

        def _drawPlaybackBezier(self, layer, p0, p1, p2, style, duration=0.0):
            if None in (*p1, *p2):
                return
            points = []
            for i in range(41):
                t = i / 40
                mt = 1 - t
                points.append((mt*mt*p0[0] + 2*mt*t*p1[0] + t*t*p2[0], mt*mt*p0[1] + 2*mt*t*p1[1] + t*t*p2[1]))
            self._drawPlaybackPath(layer, points, style, smooth=False, animate=True, duration=duration)

        def _drawPlaybackPath(self, layer, points, style, smooth=False, animate=False, duration=0.0):
            if len(points) < 2:
                return
            if smooth and len(points) > 2:
                points = self._catmull_rom(points, num_segments=24)
            width = max(1, int(style.get("size", self.brushSize)))
            color = self._rgba(style.get("color", self.brushColor), style.get("opacity", self.brushOpacity))
            if animate:
                step_delay = max(0.005, duration / max(1, len(points) - 1) / self.playSpeed)
                previous = points[0]
                radius = width / 2
                layer.draw.ellipse((previous[0]-radius, previous[1]-radius,
                                    previous[0]+radius, previous[1]+radius), fill=color)
                self.root.after(0, lambda: self._scheduleRender(fast=True))
                time.sleep(step_delay)
                for point in points[1:]:
                    if not self.isPlaying:
                        break
                    layer.draw.line((previous[0], previous[1], point[0], point[1]),
                                    fill=color, width=width, joint="curve")
                    layer.draw.ellipse((point[0]-radius, point[1]-radius,
                                        point[0]+radius, point[1]+radius), fill=color)
                    previous = point
                    self.root.after(0, lambda: self._scheduleRender(fast=True))
                    time.sleep(step_delay)
                return
            layer.draw.line(points, fill=color, width=width, joint="curve")

        def _drawPlaybackShape(self, layer, shape, x1, y1, x2, y2, style, duration=0.0):
            if x2 is None or y2 is None:
                return
            width = max(1, int(style.get("size", self.brushSize)))
            color = self._rgba(style.get("color", self.brushColor), style.get("opacity", self.brushOpacity))
            box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            if shape == "line":
                if duration > 0.0:
                    steps = max(2, int(duration * 60 / max(0.1, self.playSpeed)))
                    dx = (x2 - x1) / steps
                    dy = (y2 - y1) / steps
                    px, py = x1, y1
                    for i in range(1, steps + 1):
                        nx, ny = x1 + dx * i, y1 + dy * i
                        layer.draw.line((px, py, nx, ny), fill=color, width=width, joint="curve")
                        px, py = nx, ny
                        self.root.after(0, lambda: self._scheduleRender(fast=True))
                        time.sleep(max(0.005, duration / steps / self.playSpeed))
                    return
                self._drawPlaybackLine(layer, x1, y1, x2, y2, style)
            elif shape in ("oval", "circle"):
                layer.draw.ellipse(box, outline=color, width=width)
                if duration > 0.0:
                    self.root.after(0, lambda: self._scheduleRender(fast=True))
                    time.sleep(max(0.005, duration / self.playSpeed))
            elif shape == "rounded_rect":
                layer.draw.rounded_rectangle(box, radius=min(abs(x2-x1), abs(y2-y1)) / 6, outline=color, width=width)
                if duration > 0.0:
                    self.root.after(0, lambda: self._scheduleRender(fast=True))
                    time.sleep(max(0.005, duration / self.playSpeed))
            elif shape == "hexagon":
                cx, cy = (x1+x2)/2, (y1+y2)/2
                r = math.hypot(x2-x1, y2-y1) / 2
                pts = [(cx + r*math.cos(math.pi/3*i-math.pi/2), cy + r*math.sin(math.pi/3*i-math.pi/2)) for i in range(6)]
                layer.draw.line(pts + [pts[0]], fill=color, width=width, joint="curve")
                if duration > 0.0:
                    self.root.after(0, lambda: self._scheduleRender(fast=True))
                    time.sleep(max(0.005, duration / self.playSpeed))
            else:
                layer.draw.rectangle(box, outline=color, width=width)
                if duration > 0.0:
                    self.root.after(0, lambda: self._scheduleRender(fast=True))
                    time.sleep(max(0.005, duration / self.playSpeed))

        def _stopPlayback(self):
            self.isPlaying = False
            self.playBtn.config(text="▶  Play Timelapse", state="normal")

        # ──────── ZOOM ────────
        def _resetZoom(self):
            self.zoom    = 1.0
            self.offsetX = self.offsetY = 0
            self._scheduleRender(fast=False)

        # ──────── PROJECT ────────
        # * Menyimpan seluruh data proyek, layer, dan riwayat stroke ke dalam file JSON
        def _save(self, showPopup=True):
            data = {
                "name": self.projectName, "canvasWidth": self.CW, "canvasHeight": self.CH,
                "savedAt": datetime.now().isoformat(),
                "layers": [l.toDict() for l in self.layers],
                "strokeHistory": self.strokeHistory,
                "activeLayerIdx": self.activeIdx,
                "drawQuality": self.drawQuality,
                "renderQuality": self.renderQuality,
                "onePixelMode": self.onePixelMode,
                "stabilizerVal": self.stabilizerVal,
                "stabilizerMethod": self.stabilizerMethod,
                "fadeEnabled": self.fadeEnabled,
                "forceFade": self.forceFade,
                "fadeStartPercent": self.fadeStartPercent,
                "fadeEndPercent": self.fadeEndPercent,
                "fadeShape": self.fadeShape,
                "customBrushes": self.customBrushes,
                "timelapseDisabledLayers": sorted(self.timelapseDisabledLayers),
                "timelapseDisabledLayerNames": sorted(self.timelapseDisabledLayerNames),
            }
            with open(os.path.join(self.projectPath, "projectData.json"), "w") as f:
                json.dump(data, f)
            self._composite(include_vectors=True).save(os.path.join(self.projectPath, "preview.png"))
            if showPopup:
                messagebox.showinfo("Saved", f"'{self.projectName}' saved.")

        def _exportPNG(self):
            p = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG","*.png"),("JPEG","*.jpg")],
                initialdir=self.projectPath, title="Export Image"
            )
            if p:
                self._composite(include_vectors=True).save(p)
                messagebox.showinfo("Exported", f"Saved to:\n{p}")

        def _goHome(self):
            self._save(showPopup=False)
            for w in self.root.winfo_children():
                w.destroy()
            self.root.geometry("1060x680")
            self.root.state("zoomed")
            LaunchScreen(self.root)

        def _deleteProject(self):
            if not messagebox.askyesno("Delete Project",
                    f"Delete project '{self.projectName}' and all its files? This cannot be undone."):
                return
            try:
                import shutil
                if os.path.isdir(self.projectPath):
                    shutil.rmtree(self.projectPath)
                self._goHome()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
        root = TkinterDnD.Tk()
        root.title("2D Draw Studio")
        # Start maximized while retaining the normal Windows title-bar controls
        # (minimize, restore, and close).
        root.after(0, lambda: root.state("zoomed"))
        style = ttk.Style()
        style.theme_use("clam")
        LaunchScreen(root)
        root.mainloop()


if __name__ == "__main__":
    main()
