import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import json, os, io, time, threading, math, base64, gzip, re
from datetime import datetime
from PIL import Image, ImageDraw, ImageTk, ImageFilter

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
    {"label": "Portrait 9:16","ratio": "9:16", "w": 1080, "h": 1920},
    {"label": "4:3",          "ratio": "4:3",  "w": 1600, "h": 1200},
    {"label": "A4 Portrait",  "ratio": "A4",   "w": 2480, "h": 3508},
    {"label": "A4 Landscape", "ratio": "A4L",  "w": 3508, "h": 2480},
    {"label": "Instagram",    "ratio": "1:1",  "w": 1080, "h": 1080},
    {"label": "Custom",       "ratio": "?",    "w": None, "h": None},
]

# Built-in brush library.
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
    line = tk.Frame(f, bg=C["border"], height=1)
    line.pack(side="left", fill="x", expand=True, padx=(10, 0))
    dot = tk.Frame(f, bg=C["accent"], width=4, height=4)
    dot.pack(side="right", padx=(6, 0))
    dot.update()
    try:
        dot.config(highlightthickness=0)
    except:
        pass


def sep(parent, pad=(0, 0)):
    container = tk.Frame(parent, bg=C["panel"])
    container.pack(fill="x", padx=12, pady=pad)
    tk.Frame(container, bg=C["border"], height=1).pack(fill="x")
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
        layer.image   = Image.open(io.BytesIO(base64.b64decode(d["img"]))).convert("RGBA")
        layer.draw    = ImageDraw.Draw(layer.image)
        return layer


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

        logoFrame = tk.Frame(logoArea, bg=C["panel"])
        logoFrame.pack(anchor="w")
        tk.Label(logoFrame, text="2D", bg=C["panel"], fg=C["accent"],
                 font=("Segoe UI", 30, "bold")).pack(side="left")
        tk.Label(logoFrame, text="Draw", bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 30, "bold")).pack(side="left")
        tk.Label(logoArea, text="Studio", bg=C["panel"], fg=C["dim"],
                 font=("Segoe UI", 12)).pack(anchor="w", padx=(2, 0))
        underline = tk.Frame(logoArea, bg=C["accent"], height=2)
        underline.pack(fill="x", pady=(4, 0))

        sep(side, pad=(20, 0))

        # action buttons
        btnArea = tk.Frame(side, bg=C["panel"])
        btnArea.pack(fill="x", padx=16, pady=16)

        newBtn = tk.Button(btnArea, text="  \u2726  New Project",
                           command=self._openNewPanel,
                           bg=C["accent"], fg="#fff", bd=0, relief="flat",
                           font=("Segoe UI", 10, "bold"), cursor="hand2", pady=12, padx=0,
                           activebackground=C["accent2"], activeforeground="#fff")
        newBtn.pack(fill="x", pady=(0, 8))
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
        tk.Frame(bottom, bg=C["border"], height=1).pack(fill="x")

        self.selectedLbl = tk.Label(bottom, text="Select a canvas preset",
                                    bg=C["panel"], fg=C["dim"], font=("Segoe UI", 10))
        self.selectedLbl.pack(side="left", padx=24, pady=24)

        self.createBtn = tk.Button(
            bottom, text="  Create Project  \u2192", command=self._create,
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

        borderFrame = tk.Frame(card, bg=C["accent"] if selected else C["border"], bd=0, highlightthickness=0)
        borderFrame.pack(fill="both", expand=True, padx=0, pady=0)
        
        innerCard = tk.Frame(borderFrame, bg=bg, bd=0, highlightthickness=0)
        innerCard.pack(fill="both", expand=True, padx=1, pady=1)

        ic = tk.Canvas(innerCard, bg=bg, highlightthickness=0, width=100, height=68)
        ic.pack(pady=(16, 8))
        self._drawRatioIcon(ic, preset, "#fff" if selected else C["text"])

        tk.Label(innerCard, text=preset["label"], bg=bg, fg="#fff" if selected else C["text"],
                 font=("Segoe UI", 11, "bold") if selected else ("Segoe UI", 10, "bold")).pack()
        tk.Label(innerCard, text=preset["ratio"], bg=bg, fg="#ddd" if selected else C["dim"],
                 font=FONT_SM).pack()

        if preset["w"]:
            tk.Label(innerCard, text=f"{preset['w']} \u00d7 {preset['h']}",
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
                text=f"{preset['label']}  |  {preset['w']} \u00d7 {preset['h']} px",
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
        tk.Label(dlg, text="Enter dimensions in pixels (100 \u2013 8000)",
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
                self.selectedLbl.config(text=f"Custom  |  {w} \u00d7 {h} px",
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
        tk.Label(info, text=f"{w} \u00d7 {h}   {date}", bg=C["panel"],
                 fg=C["dim"], font=("Consolas", 7), anchor="w").pack(anchor="w")

        def openIt(e=None):
            try:
                with open(dp) as f:
                    data = json.load(f)
                self._launch(data.get("name", name), path,
                             data["canvasWidth"], data["canvasHeight"], loadData=data)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        for w_ in [card] + card.winfo_children() + info.winfo_children():
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
    def __init__(self, root, name, path, cw, ch, loadData=None):
        self.root        = root
        self.projectName = name
        self.projectPath = path
        self.CW, self.CH = cw, ch

        # Undo cache directory
        cache_name = re.sub(r'[^A-Za-z0-9._-]+', '_', os.path.basename(path) or name).strip('._') or "project"
        self.undoCacheDir = os.path.join(CACHE_DIR, cache_name)
        os.makedirs(self.undoCacheDir, exist_ok=True)
        self._undoCacheSlot = 0

        # Background layer (transparent for compositing on white)
        bgLayer = Layer("Background", cw, ch)
        bgLayer.image = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        bgLayer.draw = ImageDraw.Draw(bgLayer.image)
        self.layers = [bgLayer]
        self.activeIdx = 0
        self.timelapseDisabledLayers = set()
        self._timelapseDisableArmed = False
        self.strokeHistory  = []
        self.currentStroke  = []
        self.startTime      = 0.0

        self.brushColor   = "#1a1a1a"
        self.brushSize    = 12
        self.brushOpacity = 255
        self.brushHardness = 100
        self.tool         = "brush"
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
        self.autoSaveId = None
        self.zoomLbl = None
        self.coordLbl = None

        self.stabilizerVal = 0
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

        # throttle rendering
        self._renderPending = False
        self._qualityAfterId = None
        self._lastRender    = 0

        # draw & render quality
        self.drawQuality = 4
        self.renderQuality = "high"
        self._cacheDirty       = True
        self._cachedComposite  = None
        self._playbackImages   = None  # temp layer images during timelapse

        if loadData:
            self._loadData(loadData)
            self._makeBackgroundWhiteTransparent()

        self._buildUI()
        self.root.protocol("WM_DELETE_WINDOW", self._closeProjectWindow)
        self.root.after(120, self._centerCanvas)
        self._save(showPopup=False)

    def _loadData(self, d):
        self.layers        = [Layer.fromDict(ld, self.CW, self.CH) for ld in d["layers"]]
        self.strokeHistory = d.get("strokeHistory", [])
        self.activeIdx     = d.get("activeLayerIdx", 0)
        self.timelapseDisabledLayers = set(d.get("timelapseDisabledLayers", []))
        self.drawQuality   = max(1, min(8, d.get("drawQuality", 4)))
        self.renderQuality = d.get("renderQuality", "high")
        if self.renderQuality not in ("fast", "balanced", "high"):
            self.renderQuality = "high"
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
        self.root.title(f"2D Draw Studio  \u00b7  {self.projectName}")
        self.root.configure(bg=C["bg"])
        
        # Menubar: packed at top
        self._buildMenubar()
        
        # Content container
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
    
    # * Menu bar
    def _buildMenubar(self):
        self._menu_dds = []
        mb = tk.Frame(self.root, bg=C["panel"], height=28)
        mb.pack(side="top", fill="x")
        mb.pack_propagate(False)
        
        def make_menu(text, items_fn):
            btn = tk.Label(mb, text=text + "  \u25bc", bg=C["panel"], fg=C["text"],
                          font=("Segoe UI", 9), cursor="hand2", padx=10, pady=2)
            btn.pack(side="left")
            
            dd = tk.Frame(self.root, bg=C["card"], bd=0,
                         highlightbackground=C["border"], highlightthickness=1)
            self._menu_dds.append(dd)
            
            def rebuild_and_show():
                for w in dd.winfo_children():
                    w.destroy()
                
                items = items_fn()
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
                
                x = btn.winfo_rootx() - self.root.winfo_rootx()
                y = btn.winfo_rooty() - self.root.winfo_rooty() + btn.winfo_height()
                dd.place(x=x, y=y, width=210)
                dd.lift()
            
            btn.bind("<Enter>", lambda e: btn.config(bg=C["hover"]))
            btn.bind("<Leave>", lambda e: btn.config(bg=C["panel"]))
            btn.bind("<Button-1>", lambda e: self.root.after_idle(rebuild_and_show))
            
            return btn
        
        # FILE
        make_menu("File", lambda: [
            ("New Project", self._goHome, True),
            ("---", None, True),
            ("Save", self._save, True),
            ("Export PNG", self._exportPNG, True),
            ("Import Image", self._importImageToLayer, True),
            ("---", None, True),
            ("Exit", self.root.quit, True),
        ])
        
        # EDIT
        make_menu("Edit", lambda: [
            ("Undo", self._undo, len(self.undoStack) > 0),
            ("Redo", self._redo, len(self.redoStack) > 0),
            ("---", None, True),
            ("Clear Canvas", self._clearCanvas, True),
        ])
        
        # VIEW
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
            (f"Canvas  {self.CW} \u00d7 {self.CH}", self._showResolutionDialog, True),
            ("Resolution Settings...", self._showResolutionDialog, True),
            ("---", None, True),
            (f"Draw Quality: 1x{'  \u2713' if self.drawQuality == 1 else ''}",
             lambda: self._setDrawQuality(1), True),
            (f"Draw Quality: 2x{'  \u2713' if self.drawQuality == 2 else ''}",
             lambda: self._setDrawQuality(2), True),
            (f"Draw Quality: 4x{'  \u2713' if self.drawQuality == 4 else ''}",
             lambda: self._setDrawQuality(4), True),
            (f"Draw Quality: 8x Max{'  \u2713' if self.drawQuality == 8 else ''}",
             lambda: self._setDrawQuality(8), True),
            ("---", None, True),
            (f"Render: Fast{'  \u2713' if self.renderQuality == 'fast' else ''}",
             lambda: self._setRenderQuality("fast"), True),
            (f"Render: Balanced{'  \u2713' if self.renderQuality == 'balanced' else ''}",
             lambda: self._setRenderQuality("balanced"), True),
            (f"Render: High{'  \u2713' if self.renderQuality == 'high' else ''}",
             lambda: self._setRenderQuality("high"), True),
        ])
        
        # TOOLS
        make_menu("Tools", lambda: [
            ("Brush",     lambda: self._setTool("brush"), self.tool != "brush"),
            ("Pencil",    lambda: self._setTool("pencil"), self.tool != "pencil"),
            ("Eraser",    lambda: self._setTool("eraser"), self.tool != "eraser"),
            ("Fill",      lambda: self._setTool("fill"), self.tool != "fill"),
            ("Eyedrop",   lambda: self._setTool("eyedrop"), self.tool != "eyedrop"),
            ("Smudge",    lambda: self._setTool("smudge"), self.tool != "smudge"),
        ])
        
        # HELP
        make_menu("Help", lambda: [
            ("About 2D Draw Studio", self._showAbout, True),
        ])
        
        def close_menus(event):
            for dd in self._menu_dds:
                try:
                    dd.place_forget()
                except:
                    pass
        self.root.bind("<Button-1>", close_menus, "+")
        
        tk.Frame(mb, bg=C["accent"], height=1).pack(side="bottom", fill="x")
    
    def _showAbout(self):
        import tkinter.messagebox
        tkinter.messagebox.showinfo("About", "2D Draw Studio v1.0\nPython + Tkinter + PIL")

    def _setDrawQuality(self, level):
        self.drawQuality = max(1, min(8, level))
        self._scheduleRender(fast=False)

    def _setRenderQuality(self, mode):
        if mode in ("fast", "balanced", "high"):
            self.renderQuality = mode
            self._scheduleRender(fast=False)

    def _renderFilter(self, fast):
        # Respect render quality at ALL zoom levels.
        # NEAREST when zoomed in makes smooth lines look pixelated.
        if self.renderQuality == "high":
            return Image.LANCZOS
        if self.renderQuality == "fast":
            return Image.NEAREST
        # balanced: high-quality when idle, fast during drag
        return Image.LANCZOS if not fast else Image.BILINEAR

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
                label = f"{p['label']} ({p['w']}\u00d7{p['h']})"
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
        tk.Label(dlg, text="Supersampling saat brush \u2014 lebih tinggi = lebih halus",
                 bg=C["panel"], fg=C["dim"], font=FONT_XS).grid(row=5, column=0, columnspan=2, sticky="w", padx=16)

        drawVar = tk.IntVar(value=self.drawQuality)
        drawRow = tk.Frame(dlg, bg=C["panel"])
        drawRow.grid(row=6, column=0, columnspan=2, sticky="w", padx=16, pady=4)
        for val, lbl in [(1, "1x Fast"), (2, "2x Balanced"), (4, "4x High"),
                         (6, "6x Ultra"), (8, "8x Max")]:
            tk.Radiobutton(drawRow, text=lbl, variable=drawVar, value=val,
                           bg=C["panel"], fg=C["text"], selectcolor=C["card"],
                           activebackground=C["panel"], activeforeground=C["accent"],
                           font=FONT_SM).pack(side="left", padx=(0, 10))

        tk.Label(dlg, text="Render Quality", bg=C["panel"], fg=C["accent"],
                 font=FONT_BOLD).grid(row=7, column=0, columnspan=2, sticky="w", **pad)
        tk.Label(dlg, text="Filter saat zoom \u2014 High = paling tajam pas zoom 200%+",
                 bg=C["panel"], fg=C["dim"], font=FONT_XS).grid(row=8, column=0, columnspan=2, sticky="w", padx=16)

        renderVar = tk.StringVar(value=self.renderQuality)
        renderRow = tk.Frame(dlg, bg=C["panel"])
        renderRow.grid(row=9, column=0, columnspan=2, sticky="w", padx=16, pady=4)
        for val, lbl in [("fast", "Fast"), ("balanced", "Balanced"), ("high", "High")]:
            tk.Radiobutton(renderRow, text=lbl, variable=renderVar, value=val,
                           bg=C["panel"], fg=C["text"], selectcolor=C["card"],
                           activebackground=C["panel"], activeforeground=C["accent"],
                           font=FONT_SM).pack(side="left", padx=(0, 12))

        btnRow = tk.Frame(dlg, bg=C["panel"])
        btnRow.grid(row=10, column=0, columnspan=2, pady=16)
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
                    f"Ubah canvas dari {self.CW}\u00d7{self.CH} ke {nw}\u00d7{nh}?\n"
                    "Semua layer akan di-scale ke ukuran baru.",
                    parent=dlg,
                ):
                    return
                self._resizeCanvas(nw, nh)
            self.drawQuality = drawVar.get()
            self.renderQuality = renderVar.get()
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
        for layer in reversed(self.layers):
            layer.image = layer.image.resize((new_w, new_h), Image.LANCZOS)
            layer.draw = ImageDraw.Draw(layer.image)
            layer.w, layer.h = new_w, new_h
        self.CW, self.CH = new_w, new_h
        self.rulerX = min(self.rulerX, new_w - 1)
        self.rulerY = min(self.rulerY, new_h - 1)
        self._cacheDirty = True
        self.root.title(f"2D Draw Studio  \u00b7  {self.projectName}")
        self._scheduleRender(fast=False)
    
    def _zoom(self, factor):
        self.zoom = max(0.1, min(10, self.zoom * factor))
        if self.zoomLbl:
            self.zoomLbl.config(text=f"{int(self.zoom * 100)}%")
        self._scheduleRender(fast=False)
    
    def _resetZoom(self):
        self._centerCanvas()
    
    # * Toolbar
    def _buildToolbar(self):
        self._tbFrame = tk.Frame(self.contentFrame, bg=C["panel"], width=64)
        self._tbFrame.grid(row=0, column=0, sticky="nsew")
        self._tbFrame.grid_propagate(False)
        tb = self._tbFrame

        self.toolVar   = tk.StringVar(value="brush")
        self._popout   = None
        self._popoutId = None

        tools = [
            ("\u270f",  "brush",   "Brush"),
            ("\u2712",  "pencil",  "Pencil"),
            ("\u25cc",  "eraser",  "Eraser"),
            ("\u25a0",  "fill",    "Fill"),
            ("\u2299",  "eyedrop", "Eyedrop"),
            ("~",       "smudge",  "Smudge"),
        ]

        tk.Label(tb, text="TOOLS", bg=C["panel"], fg=C["dim"],
                 font=("Segoe UI", 7, "bold"), pady=8).pack(fill="x")
        tk.Frame(tb, bg=C["border"], height=1).pack(fill="x", padx=8, pady=(0, 5))
        for icon, mode, tip in tools:
            self._toolBtn(tb, icon, mode, tip)

        self._toolBtn(tb, "\u25a3", "select", "Select: click a stroke or drag an area")

        tk.Frame(tb, bg=C["border"], height=1).pack(fill="x", pady=(6, 2))

        # Shape popout toggle
        self.shapeTabBtn = tk.Label(tb, text="\u2a21", bg=C["panel"], fg=C["dim"],
                                    font=("Segoe UI Symbol", 13), cursor="hand2",
                                    pady=6, width=4)
        self.shapeTabBtn.pack(fill="x", pady=1)
        self.shapeTabBtn.bind("<Button-1>", lambda e: self._togglePopout("shape"))
        self._makeTooltip(self.shapeTabBtn, "Shapes")

        # Stabilizer popout toggle
        self.stabTabBtn = tk.Label(tb, text="\u224b", bg=C["panel"], fg=C["dim"],
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
        self.symBtn = tk.Label(tb, text="\u21c4", bg=C["panel"], fg=C["dim"],
                                font=("Segoe UI", 12), cursor="hand2", pady=4)
        self.symBtn.pack(fill="x", pady=(4,0))
        self.symBtn.bind("<Button-1>", lambda e: self._toggleSym())
        self._makeTooltip(self.symBtn, "Symmetry")

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

    def _openPopout(self, panelId):
        container = self.tkCanvas.master
        pop = tk.Frame(container, bg=C["panel"], width=200,
                       highlightthickness=1, highlightbackground=C["border"])
        pop.place(x=72, y=16, anchor="nw")
        pop.lift()
        self._popout = pop

        if panelId == "shape":
            self.shapeTabBtn.config(bg=C["accent"], fg="#fff")
            self._buildShapePopout(pop)
        elif panelId == "stab":
            self.stabTabBtn.config(bg=C["accent"], fg="#fff")
            self._buildStabPopout(pop)

        self.tkCanvas.bind("<Button-1>", self._onCanvasClickClosePopout, add="+")

    def _onCanvasClickClosePopout(self, event):
        self._closePopout()
        self._popoutOpen = False

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

        self.stabilizerVar = tk.IntVar(value=self.stabilizerVal)
        self._popoutSliderRow(p, "Stabilizer", self.stabilizerVar, 0, 10,
                              self._setStabilizerVal)

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

        # Fade choices
        chkRow = tk.Frame(p, bg=C["panel"])
        chkRow.pack(fill="x", padx=10, pady=2)
        self.fadeModeVar = tk.StringVar(value="force" if self.forceFade else "fade" if self.fadeEnabled else "off")
        for value, label in (("off", "Off"), ("fade", "Fade"), ("force", "Force")):
            tk.Radiobutton(chkRow, text=label, variable=self.fadeModeVar, value=value,
                           command=lambda v=value: self._setFadeMode(v), bg=C["panel"],
                           fg=C["text"], selectcolor=C["card"], activebackground=C["panel"],
                           activeforeground=C["accent"], font=FONT_SM).pack(side="left", padx=(0, 5))

        self.fadeStartVar = tk.IntVar(value=self.fadeStartPercent)
        self._popoutSliderRow(p, "Awal %", self.fadeStartVar, 0, 100,
                              lambda v: setattr(self, "fadeStartPercent", int(float(v))))

        self.fadeEndVar = tk.IntVar(value=self.fadeEndPercent)
        self._popoutSliderRow(p, "Akhir %", self.fadeEndVar, 0, 100,
                              lambda v: setattr(self, "fadeEndPercent", int(float(v))))

        fRow = tk.Frame(p, bg=C["panel"])
        fRow.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(fRow, text="Bentuk", bg=C["panel"], fg=C["dim"],
                 font=FONT_SM, width=8, anchor="w").pack(side="left")
        for value, icon in (("Lancip", "\u25e2"), ("Halus agak lancip", "\u25e3")):
            btn = tk.Button(fRow, text=icon, command=lambda v=value: self._setFadeShape(v),
                            bg=C["accent"] if self.fadeShape == value else C["card"],
                            fg="#fff" if self.fadeShape == value else C["text"], bd=0,
                            relief="flat", cursor="hand2", font=("Segoe UI Symbol", 14), width=4)
            btn.pack(side="left", padx=3)

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
            ("/ Line",    "line"),
            ("Rect",       "rect"),
            ("Circle",     "circle"),
            ("Hexagon",    "hexagon"),
            ("Arrow",      "arrow"),
            ("Oval",       "oval"),
            ("R-Rect",     "rounded_rect"),
            ("Bezier",     "bezier"),
            ("Polyline",   "polyline"),
            ("Bubble",     "bubble"),
        ]

        for i, (label, mode) in enumerate(shapes):
            bg = C["accent"] if self.shapeMode == mode else C["card"]
            btn = flatBtn(gridFrame, label, lambda m=mode: self._setShapeModePopout(m),
                          bg=bg, padx=4, pady=5, font=FONT_SM)
            btn.grid(row=i // 2, column=i % 2, padx=2, pady=2, sticky="ew")

        for c in range(2):
            gridFrame.grid_columnconfigure(c, weight=1)

    def _setShapeModePopout(self, mode):
        self.shapeMode = mode
        self.toolVar.set("shape")
        self.tool = "shape"
        self.polylinePoints.clear()
        self.bezierAnchorPoints.clear()
        self._closePopout()
        self._scheduleRender(fast=False)

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

    def _setFadeMode(self, mode):
        self.fadeEnabled = mode == "fade"
        self.forceFade = mode == "force"

    def _setFadeShape(self, shape):
        self.fadeShape = shape
        self._scheduleRender(fast=False)

    def _toolBtn(self, parent, icon, mode, tip):
        btn = tk.Radiobutton(
            parent, text=icon, variable=self.toolVar, value=mode,
            bg=C["panel"], fg=C["dim"],
            selectcolor=C["bg"],
            activebackground=C["panel"], activeforeground=C["text"],
            indicatoron=0, bd=0, width=4, height=2,
            font=("Segoe UI Symbol", 13), relief="flat", cursor="hand2",
            command=lambda m=mode: setattr(self, "tool", m)
        )
        btn.pack(pady=1, padx=2)
        btn.bind("<Enter>", lambda e, b=btn: b.config(fg=C["text"]))
        btn.bind("<Leave>", lambda e, b=btn: b.config(
            fg=C["accent"] if self.toolVar.get() == mode else C["dim"]))
        self._makeTooltip(btn, tip)

    def _setTool(self, tool):
        self.tool = tool
        self.toolVar.set(tool)
        self._scheduleRender(fast=False)

    # * Canvas
    def _buildCanvas(self):
        container = tk.Frame(self.contentFrame, bg=C["canvas_bg"])
        container.grid(row=0, column=1, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.tkCanvas = tk.Canvas(container, bg=C["canvas_bg"],
                                   cursor="crosshair", highlightthickness=0)
        self.tkCanvas.grid(row=0, column=0, sticky="nsew")

        # Floating Undo/Redo
        self.floatingUndoRedo = tk.Frame(container, bg=C["panel"], bd=0, highlightthickness=0)
        self.floatingUndoRedo.place(x=12, y=12, anchor="nw")
        
        undoBtn = flatBtn(self.floatingUndoRedo, "\u21b6", self._undo, padx=10, pady=6)
        undoBtn.configure(font=("Segoe UI Symbol", 10, "bold"))
        undoBtn.pack(side="left", padx=1)
        
        redoBtn = flatBtn(self.floatingUndoRedo, "\u21b7", self._redo, padx=10, pady=6)
        redoBtn.configure(font=("Segoe UI Symbol", 10, "bold"))
        redoBtn.pack(side="left", padx=1)

        # Info overlay
        self.floatingInfo = tk.Frame(container, bg=C["panel"], bd=0, highlightthickness=0)
        self.floatingInfo.place(relx=1.0, rely=1.0, x=-12, y=-12, anchor="se")
        
        self.zoomLbl = tk.Label(self.floatingInfo, text="100%", bg=C["panel"], fg=C["text"], font=FONT_SM, padx=6, pady=4)
        self.zoomLbl.pack(side="left")
        
        self.coordLbl = tk.Label(self.floatingInfo, text="0, 0", bg=C["panel"], fg=C["dim"], font=("Consolas", 8), padx=6, pady=4)
        self.coordLbl.pack(side="left")

        # bindings
        self.tkCanvas.bind("<ButtonPress-1>",   self._onDown)
        self.tkCanvas.bind("<B1-Motion>",        self._onMove)
        self.tkCanvas.bind("<ButtonRelease-1>",  self._onUp)
        self.tkCanvas.bind("<ButtonPress-2>",    self._panStart)
        self.tkCanvas.bind("<B2-Motion>",        self._panMove)
        self.tkCanvas.bind("<ButtonPress-3>",    self._panStart)
        self.tkCanvas.bind("<B3-Motion>",        self._panMove)
        self.tkCanvas.bind("<MouseWheel>",        self._onScroll)
        self.tkCanvas.bind("<Motion>",            self._onHover)
        self.tkCanvas.bind("<Configure>",
            lambda e: self._scheduleRender())

        self.root.bind("<Control-z>", lambda e: self._undo())
        self.root.bind("<Control-y>", lambda e: self._redo())
        self.root.bind("<Control-s>", lambda e: self._save())
        self.root.bind("<bracketleft>",  lambda e: self._changeBrushSize(-2))
        self.root.bind("<bracketright>", lambda e: self._changeBrushSize(2))
        self.root.bind("<Return>", lambda e: self._finishShape())
        self.tkCanvas.bind("<Double-Button-1>", lambda e: self._finishShape())

    # * Right Panel
    def _buildRightPanel(self):
        panel = tk.Frame(self.contentFrame, bg=C["panel"], width=230)
        panel.grid(row=0, column=2, sticky="nsew")
        panel.grid_propagate(False)

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
            lambda e: rCanvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # header nama project
        hdr = tk.Frame(inner, bg=C["panel"])
        hdr.pack(fill="x", padx=12, pady=(14, 2))
        tk.Label(hdr, text=self.projectName, bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 9, "bold"), anchor="w",
                 wraplength=180).pack(anchor="w")

        # Project Actions
        actionFrame = tk.Frame(inner, bg=C["panel"])
        actionFrame.pack(fill="x", padx=12, pady=(4, 2))

        homeBtn = flatBtn(actionFrame, "\u2190 Home", self._goHome, bg=C["card"], padx=10, pady=6)
        homeBtn.pack(side="left", padx=2)

        saveBtn = flatBtn(actionFrame, "Save", self._save, bg=C["accent"], fg="#fff", padx=10, pady=6)
        saveBtn.pack(side="right", padx=2)

        exportBtn = flatBtn(actionFrame, "Export", self._exportPNG, bg=C["card"], padx=10, pady=6)
        exportBtn.pack(side="right", padx=2)

        self._buildBrushSection(inner)
        self._buildRulerSection(inner)
        self._buildColorSection(inner)
        self._buildLayerSection(inner)
        self._buildFrameSection(inner)
        self._buildTimelapseSection(inner)

    def _buildBrushSection(self, p):
        sectionTitle(p, "BRUSH")
        self.brushSizeVar = tk.IntVar(value=self.brushSize)
        self._sliderRow(p, "Size",     self.brushSizeVar, 1, 200,
                        lambda v: setattr(self, "brushSize", int(float(v))))
        self.opacityVar = tk.IntVar(value=100)
        self._sliderRow(p, "Opacity",  self.opacityVar,   1, 100,
                        lambda v: setattr(self, "brushOpacity", int(float(v) * 2.55)))
        self.hardVar = tk.IntVar(value=self.brushHardness)
        self._sliderRow(p, "Hardness", self.hardVar,      1, 100,
                        lambda v: setattr(self, "brushHardness", int(float(v))))

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

    def _buildFrameSection(self, p):
        sectionTitle(p, "FRAME")
        row = tk.Frame(p, bg=C["panel"])
        row.pack(fill="x", padx=12, pady=4)
        self.frameBtn = flatBtn(row, "Frame: OFF", self._toggleFrame, padx=10, pady=6)
        self.frameBtn.pack(fill="x")

        self.frameSizeVar = tk.IntVar(value=self.frameSize)
        self._sliderRow(p, "Size", self.frameSizeVar, 10, 200,
                        lambda v: setattr(self, "frameSize", int(float(v))))

    def _toggleFrame(self):
        self.frameEnabled = not self.frameEnabled
        self.frameBtn.config(text=f"Frame: {'ON' if self.frameEnabled else 'OFF'}",
                             bg=C["accent"] if self.frameEnabled else C["card"])
        self._scheduleRender(fast=False)

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

        sw = tk.Frame(p, bg=C["panel"])
        sw.pack(fill="x", padx=12, pady=4)
        swatches = [
            "#1a1a1a","#444444","#888888","#cccccc","#ffffff",
            "#e53935","#fb8c00","#fdd835","#43a047","#1e88e5",
            "#8e24aa","#00897b","#ff4081","#ff6d00","#64ffda",
        ]
        for i, color in enumerate(swatches):
            s = tk.Label(sw, bg=color, width=2, height=1, cursor="hand2",
                         bd=0, relief="flat")
            s.grid(row=i//8, column=i%8, padx=2, pady=2)
            s.bind("<Button-1>", lambda e, c=color: self._setColor(c))

    def _buildLayerSection(self, p):
        sectionTitle(p, "LAYERS")
        btnRow = tk.Frame(p, bg=C["panel"])
        btnRow.pack(fill="x", padx=12, pady=4)
        for label, cmd in [("+ Add", self._addLayer), 
                           ("Del", self._delLayer),
                           ("\u2191", lambda: self._moveLayer(-1)),
                           ("\u2193", lambda: self._moveLayer(1)),
                           ("Import", self._importImageToLayer)]:
            flatBtn(btnRow, label, cmd, padx=6, pady=4, font=FONT_SM).pack(side="left", padx=1, expand=True, fill="x")

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

        self.layerFrame = tk.Frame(p, bg=C["panel"])
        self.layerFrame.pack(fill="x", padx=12, pady=4)
        self._refreshLayerPanel()

    def _buildTimelapseSection(self, p):
        sectionTitle(p, "TIMELAPSE")
        self.playBtn = tk.Button(
            p, text="\u25b6  Play Timelapse", command=self._startPlayback,
            bg=C["accent"], fg="#fff", bd=0, relief="flat",
            font=FONT_BOLD, cursor="hand2", pady=10,
            activebackground=C["accent2"], activeforeground="#fff"
        )
        self.playBtn.pack(fill="x", padx=12, pady=4)
        self.playBtn.bind("<Enter>", lambda e: self.playBtn.config(bg=C["accent2"]))
        self.playBtn.bind("<Leave>", lambda e: self.playBtn.config(bg=C["accent"]))

        flatBtn(p, "\u25a0  Stop", self._stopPlayback, padx=0, pady=7).pack(
            fill="x", padx=12, pady=2)

        self.speedVar = tk.DoubleVar(value=2.0)
        self._sliderRow(p, "Speed \u00d7", self.speedVar, 0.5, 20,
                        lambda v: setattr(self, "playSpeed", float(v)), res=0.5)

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

    def _toImg(self, cx, cy):
        w = self.tkCanvas.winfo_width()
        h = self.tkCanvas.winfo_height()
        sw = int(self.CW * self.zoom)
        sh = int(self.CH * self.zoom)
        ox = self.offsetX if self.offsetX is not None else (w - sw) // 2
        oy = self.offsetY if self.offsetY is not None else (h - sh) // 2
        return (cx - ox) / self.zoom, (cy - oy) / self.zoom

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

    def _setStabilizerVal(self, val):
        self.stabilizerVal = int(float(val))

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
        self.smoothX = x
        self.smoothY = y
        self.lastX, self.lastY = x, y
        self.currentStroke = []

        if self.tool == "eyedrop":
            self._eyedrop(x, y); return
        if self.tool == "fill":
            self._fill(int(x), int(y)); return

        if self.tool == "shape":
            if self.shapeMode == "bezier":
                self.bezierAnchorPoints.append((x, y))
                self.previewX, self.previewY = x, y
                self._scheduleRender(fast=True)
                return
            elif self.shapeMode == "polyline":
                self.polylinePoints.append((x, y))
                self.previewX, self.previewY = x, y
                self._scheduleRender(fast=True)
                return
            else:
                self.shapeStartPoint = (x, y)
                self.previewX, self.previewY = x, y
                return

        self.currentStroke.append(self._pt(x, y))
        
        if self.stabilizerMethod == "Real-time":
            self._saveUndo()
            self._applyPoint(x, y)
            
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

        if self.tool == "shape":
            x, y = self._snapToRuler(x, y)
            self.previewX, self.previewY = x, y
            self._scheduleRender(fast=True)
            return

        if self.lastX is None: return

        if self.stabilizerVal > 0:
            weight = 1.0 / (self.stabilizerVal + 1)
            self.smoothX += (x - self.smoothX) * weight
            self.smoothY += (y - self.smoothY) * weight
            x, y = self.smoothX, self.smoothY

        x, y = self._snapToRuler(x, y)

        dx, dy = abs(x - self.lastX), abs(y - self.lastY)
        if dx < 0.5 and dy < 0.5: return

        self.currentStroke.append(self._pt(x, y))
        
        if self.stabilizerMethod == "Real-time":
            self._applyLine(self.lastX, self.lastY, x, y)
            
        self._scheduleRender(fast=True)
        self.lastX, self.lastY = x, y

    def _onUp(self, event):
        if self.isPlaying: return
        
        if self.rulerIsDragging:
            self.rulerIsDragging = False
            return

        if self.tool == "shape":
            if self.shapeMode in ("bezier", "polyline"):
                return
                
            if self.shapeStartPoint and self.previewX is not None:
                self._saveUndo()
                p0 = self.shapeStartPoint
                p1 = (self.previewX, self.previewY)
                
                if self.startTime == 0.0:
                    self.startTime = time.time()
                
                self._drawShapeToLayer(self.shapeMode, p0[0], p0[1], p1[0], p1[1])
                stroke = [
                    self._pt(p0[0], p0[1], mode=f"shape_{self.shapeMode}", ex=p1[0], ey=p1[1]),
                ]
                self.strokeHistory.append(stroke)
                
                self.shapeStartPoint = None
                self.previewX = self.previewY = None
                
                self._scheduleRender(fast=False)
                self._updateStrokeLabel()
            return

        if not self.currentStroke or len(self.currentStroke) < 2:
            if self.currentStroke:
                self.currentStroke = []
            return

        if self.stabilizerMethod == "Real-time":
            self._redrawStrokeSmooth(self.currentStroke)
        else:
            self._saveUndo()
            self._applyStrokeToLayer(self.currentStroke)
        
        self.strokeHistory.append(self.currentStroke)
        self.currentStroke = []
        self._scheduleRender(fast=False)
        self._updateStrokeLabel()

    # ──────── SHAPES ────────
    def _finishShape(self):
        if self.tool != "shape":
            return
        if self.shapeMode == "bezier" and len(self.bezierAnchorPoints) >= 3:
            pts = self.bezierAnchorPoints
            self._saveUndo()
            self._drawBezierToLayer(pts[-3], pts[-2], pts[-1])
            stroke = []
            for p in pts:
                stroke.append(self._pt(p[0], p[1]))
            self.strokeHistory.append(stroke)
            self._scheduleRender(fast=False)
            self._updateStrokeLabel()
        elif self.shapeMode == "polyline" and len(self.polylinePoints) >= 2:
            pts = self.polylinePoints
            if self.startTime == 0.0:
                self.startTime = time.time()
            self._saveUndo()
            self._drawPolylineToLayer(pts)
            stroke = [self._pt(p[0], p[1]) for p in pts]
            self.strokeHistory.append(stroke)
            self._scheduleRender(fast=False)
            self._updateStrokeLabel()
        self.polylinePoints.clear()
        self.bezierAnchorPoints.clear()
        self.previewX = self.previewY = None

    # ──────── DRAWING ────────
    def _drawShapeToLayer(self, mode, x, y, ex, ey):
        layer = self.layers[self.activeIdx]
        if layer.locked: return
        color = self._rgba(self.brushColor, self.brushOpacity)
        r = max(1, self.brushSize // 2)
        if mode == "rect":
            layer.draw.rectangle([x, y, ex, ey], outline=color, width=r)
        elif mode == "oval":
            layer.draw.ellipse([x, y, ex, ey], outline=color, width=r)
        elif mode == "rounded_rect":
            corner = min(abs(ex-x), abs(ey-y)) // 4
            layer.draw.rounded_rectangle([x, y, ex, ey], radius=corner, outline=color, width=r)
        elif mode == "circle":
            cx, cy = (x+ex)//2, (y+ey)//2
            rad = max(1, int(math.hypot(ex-cx, ey-cy)))
            layer.draw.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], outline=color, width=r)
        elif mode == "hexagon":
            cx, cy = (x+ex)//2, (y+ey)//2
            rad = max(1, int(math.hypot(ex-cx, ey-cy)))
            pts = []
            for i in range(6):
                angle = math.pi/3 * i - math.pi/2
                pts.append((cx+rad*math.cos(angle), cy+rad*math.sin(angle)))
            layer.draw.polygon(pts, outline=color, width=r)
        elif mode == "arrow":
            layer.draw.line([x, y, ex, ey], fill=color, width=r)
            angle = math.atan2(ey-y, ex-x)
            head = 20
            ax1 = ex - head*math.cos(angle-0.5)
            ay1 = ey - head*math.sin(angle-0.5)
            ax2 = ex - head*math.cos(angle+0.5)
            ay2 = ey - head*math.sin(angle+0.5)
            layer.draw.polygon([(ex, ey), (ax1, ay1), (ax2, ay2)], fill=color)
        elif mode == "bubble":
            cx, cy = (x+ex)//2, (y+ey)//2
            rad = max(1, int(math.hypot(ex-cx, ey-cy)))
            layer.draw.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], outline=color, width=r)
        elif mode == "line":
            layer.draw.line([x, y, ex, ey], fill=color, width=r)
        layer.draw = ImageDraw.Draw(layer.image)
        self._cacheDirty = True

    def _drawLineToLayer(self, x1, y1, x2, y2):
        layer = self.layers[self.activeIdx]
        if layer.locked: return
        r = self.brushSize // 2
        color = self._rgba(self.brushColor, self.brushOpacity)
        dist = math.hypot(x2-x1, y2-y1)
        steps = max(int(dist * 2), 2)
        for i in range(steps + 1):
            t = i / steps
            xi = x1 + (x2-x1)*t
            yi = y1 + (y2-y1)*t
            layer.draw.ellipse([xi-r, yi-r, xi+r, yi+r], fill=color)
            if self.symmetry:
                self._paintSym(layer, xi, yi, r, color)
        layer.draw = ImageDraw.Draw(layer.image)
        self._cacheDirty = True

    def _drawBezierToLayer(self, p0, p1, p2):
        layer = self.layers[self.activeIdx]
        if layer.locked: return
        r = self.brushSize // 2
        color = self._rgba(self.brushColor, self.brushOpacity)
        steps = 100
        prevX, prevY = p0[0], p0[1]
        for i in range(1, steps + 1):
            t = i / steps
            mt = 1 - t
            xi = mt*mt*p0[0] + 2*mt*t*p1[0] + t*t*p2[0]
            yi = mt*mt*p0[1] + 2*mt*t*p1[1] + t*t*p2[1]
            dist = math.hypot(xi - prevX, yi - prevY)
            substeps = max(int(dist * 2), 2)
            for s in range(substeps + 1):
                st = s / substeps
                sxi = prevX + (xi - prevX) * st
                syi = prevY + (yi - prevY) * st
                layer.draw.ellipse([sxi-r, syi-r, sxi+r, syi+r], fill=color)
                if self.symmetry:
                    self._paintSym(layer, sxi, syi, r, color)
            prevX, prevY = xi, yi
        layer.draw = ImageDraw.Draw(layer.image)
        self._cacheDirty = True

    def _drawSplineToLayer(self, pts):
        layer = self.layers[self.activeIdx]
        if layer.locked: return
        color = self._rgba(self.brushColor, self.brushOpacity)
        r = self.brushSize
        if len(pts) == 2:
            layer.draw.line(pts, fill=color, width=r)
        else:
            smooth = self._catmull_rom(pts, num_segments=12)
            layer.draw.line(smooth, fill=color, width=r, joint='curve')
        if self.symmetry:
            mx = [(self.CW - x, y) for x, y in pts]
            my = [(x, self.CH - y) for x, y in pts]
            mxy = [(self.CW - x, self.CH - y) for x, y in pts]
            for sym_pts in (mx, my, mxy):
                if len(sym_pts) == 2:
                    layer.draw.line(sym_pts, fill=color, width=r)
                else:
                    layer.draw.line(self._catmull_rom(sym_pts), fill=color, width=r, joint='curve')
        self._cacheDirty = True

    def _drawPolylineToLayer(self, pts):
        layer = self.layers[self.activeIdx]
        if layer.locked: return
        color = self._rgba(self.brushColor, self.brushOpacity)
        r = self.brushSize
        layer.draw.line(pts, fill=color, width=r, joint='curve')
        if self.symmetry:
            mx = [(self.CW - x, y) for x, y in pts]
            my = [(x, self.CH - y) for x, y in pts]
            mxy = [(self.CW - x, self.CH - y) for x, y in pts]
            layer.draw.line(mx, fill=color, width=r, joint='curve')
            layer.draw.line(my, fill=color, width=r, joint='curve')
            layer.draw.line(mxy, fill=color, width=r, joint='curve')
        self._cacheDirty = True

    def _paintSym(self, layer, x, y, r, color):
        layer.draw.ellipse([self.CW-x-r, y-r, self.CW-x+r, y+r], fill=color)
        layer.draw.ellipse([x-r, self.CH-y-r, x+r, self.CH-y+r], fill=color)
        layer.draw.ellipse([self.CW-x-r, self.CH-y-r, self.CW-x+r, self.CH-y+r], fill=color)

    # * Apply stroke to layer (used in Before-After mode)
    def _applyStrokeToLayer(self, stroke):
        if not stroke:
            return
        layer = self.layers[self.activeIdx]
        if layer.locked:
            return

        # Stabilizer smoothing
        if self.stabilizerVal > 0 and self.stabilizerMethod == "Before-After" and len(stroke) > 3:
            smoothed = []
            window = min(self.stabilizerVal + 1, len(stroke))
            for i, pt in enumerate(stroke):
                start = max(0, i - window // 2)
                end = min(len(stroke), i + window // 2 + 1)
                seg = stroke[start:end]
                sum_x = sum(p["x"] for p in seg)
                sum_y = sum(p["y"] for p in seg)
                total_weight = len(seg)
                new_pt = pt.copy()
                new_pt["x"] = sum_x / total_weight
                new_pt["y"] = sum_y / total_weight
                smoothed.append(new_pt)
            stroke = smoothed

        prevX, prevY = None, None
        hardness = self.brushHardness
        for pt in stroke:
            x, y = pt["x"], pt["y"]
            r = pt["size"] // 2
            color = self._rgba(pt["color"], pt["opacity"])
            is_eraser = (pt["mode"] == "eraser")

            fill_clr = (0,0,0,0) if is_eraser else color

            if prevX is not None:
                dist = math.hypot(x - prevX, y - prevY)
                steps = max(int(dist * 2), 2)
                if hardness < 100 and not is_eraser:
                    for i in range(steps + 1):
                        t = i / steps
                        xi = prevX + (x - prevX) * t
                        yi = prevY + (y - prevY) * t
                        self._paintSoft(layer, xi, yi, r, fill_clr, hardness)
                        if self.symmetry:
                            self._paintSoft(layer, self.CW - xi, yi, r, color, hardness)
                            self._paintSoft(layer, xi, self.CH - yi, r, color, hardness)
                            self._paintSoft(layer, self.CW - xi, self.CH - yi, r, color, hardness)
                else:
                    seg_pts = []
                    for i in range(steps + 1):
                        t = i / steps
                        xi = prevX + (x - prevX) * t
                        yi = prevY + (y - prevY) * t
                        seg_pts.append((xi, yi))
                    if is_eraser:
                        layer.draw.line(seg_pts, fill=fill_clr, width=r*2, joint='curve')
                    else:
                        layer.draw.line(seg_pts, fill=fill_clr, width=r*2, joint='curve')
                    if self.symmetry:
                        mx_pts = [(self.CW - xi, yi) for xi, yi in seg_pts]
                        my_pts = [(xi, self.CH - yi) for xi, yi in seg_pts]
                        mxy_pts = [(self.CW - xi, self.CH - yi) for xi, yi in seg_pts]
                        for sym_pts in (mx_pts, my_pts, mxy_pts):
                            layer.draw.line(sym_pts, fill=color, width=r*2, joint='curve')
            else:
                if is_eraser:
                    layer.draw.ellipse([x-r, y-r, x+r, y+r], fill=(0,0,0,0))
                elif hardness < 100:
                    self._paintSoft(layer, x, y, r, fill_clr, hardness)
                else:
                    layer.draw.ellipse([x-r, y-r, x+r, y+r], fill=fill_clr)
                if self.symmetry:
                    self._paintSym(layer, x, y, r, color)
            prevX, prevY = x, y

        layer.draw = ImageDraw.Draw(layer.image)
        self._cacheDirty = True

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

    def _redrawStrokeSmooth(self, stroke):
        if not stroke or len(stroke) < 2:
            return
        layer = self.layers[self.activeIdx]
        if layer.locked:
            return
        has_eraser = any(pt.get("mode") == "eraser" for pt in stroke)
        if has_eraser:
            return
        
        pts = [(pt["x"], pt["y"]) for pt in stroke]
        mid_idx = len(stroke) // 2
        mid_pt = stroke[mid_idx]
        color = self._rgba(mid_pt["color"], mid_pt["opacity"])
        size = mid_pt["size"]
        
        smooth_pts = self._catmull_rom(pts, num_segments=12)
        layer.draw.line(smooth_pts, fill=color, width=size, joint='curve')
        
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

    # * Pan/zoom
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

    def _onScroll(self, event):
        f = 1.12 if event.delta > 0 else 1/1.12
        new_zoom = max(0.05, min(12.0, self.zoom * f))
        
        if self.offsetX is None:
            w_init = self.tkCanvas.winfo_width() or 800
            h_init = self.tkCanvas.winfo_height() or 600
            sw_init = int(self.CW * self.zoom)
            sh_init = int(self.CH * self.zoom)
            self.offsetX = (w_init - sw_init) // 2
            self.offsetY = (h_init - sh_init) // 2

        mx, my = event.x, event.y
        img_x = (mx - self.offsetX) / self.zoom
        img_y = (my - self.offsetY) / self.zoom
        self.zoom = new_zoom
        sw = int(self.CW * self.zoom)
        sh = int(self.CH * self.zoom)
        self.offsetX = mx - img_x * self.zoom
        self.offsetY = my - img_y * self.zoom
        
        if self.zoomLbl:
            self.zoomLbl.config(text=f"{int(self.zoom * 100)}%")
        self._scheduleRender(fast=True)

    def _onHover(self, event):
        x, y = self._toImg(event.x, event.y)
        self.coordLbl.config(text=f"{int(x)}, {int(y)}")

    def _pt(self, x, y, mode=None, **kw):
        pt = {
            "x": x, "y": y, "t": time.time() - self.startTime,
            "color": self.brushColor, "size": self.brushSize,
            "opacity": self.brushOpacity, "mode": mode or self.tool,
            "layer": self.activeIdx, "hardness": self.brushHardness,
        }
        pt.update(kw)
        return pt

    def _applyPoint(self, x, y):
        layer = self.layers[self.activeIdx]
        if layer.locked: return
        r = self.brushSize // 2
        color = self._rgba(self.brushColor, self.brushOpacity)
        is_eraser = (self.tool == "eraser")
        fill = (0,0,0,0) if is_eraser else color
        if self.brushHardness < 100 and not is_eraser:
            self._paintSoft(layer, x, y, r, fill, self.brushHardness)
        else:
            layer.draw.ellipse([x-r, y-r, x+r, y+r], fill=fill)
        if self.symmetry:
            self._paintSym(layer, x, y, r, color)
        self._cacheDirty = True

    def _applyLine(self, x1, y1, x2, y2):
        layer = self.layers[self.activeIdx]
        if layer.locked: return
        r = self.brushSize // 2
        color = self._rgba(self.brushColor, self.brushOpacity)
        is_eraser = (self.tool == "eraser")
        fill = (0,0,0,0) if is_eraser else color

        dist = math.hypot(x2-x1, y2-y1)
        steps = max(int(dist * 2), 2)

        if self.brushHardness < 100 and not is_eraser:
            for i in range(steps + 1):
                t = i / steps
                xi = x1 + (x2-x1)*t
                yi = y1 + (y2-y1)*t
                self._paintSoft(layer, xi, yi, r, fill, self.brushHardness)
        else:
            seg_pts = []
            for i in range(steps + 1):
                t = i / steps
                xi = x1 + (x2-x1)*t
                yi = y1 + (y2-y1)*t
                seg_pts.append((xi, yi))
            layer.draw.line(seg_pts, fill=fill, width=r*2, joint='curve')

        if self.symmetry:
            mx = [(self.CW - x, y) for x, y in seg_pts] if not (self.brushHardness < 100 and not is_eraser) else []
            for xi, yi in [(x1 + (x2-x1)*(i/steps), y1 + (y2-y1)*(i/steps)) for i in range(steps + 1)]:
                self._paintSym(layer, xi, yi, r, color)
        self._cacheDirty = True

    def _catmull_rom(self, points, num_segments=12):
        if len(points) < 2:
            return points
        if len(points) == 2:
            return points
        result = [points[0]]
        for i in range(1, len(points) - 1):
            p0 = points[i-1] if i > 0 else points[i]
            p1 = points[i]
            p2 = points[i+1]
            p3 = points[i+2] if i < len(points) - 2 else points[i+1]
            for t in range(1, num_segments + 1):
                t_norm = t / num_segments
                x = 0.5 * ((2*p1[0]) + (-p0[0] + p2[0])*t_norm + (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0])*t_norm**2 + (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0])*t_norm**3)
                y = 0.5 * ((2*p1[1]) + (-p0[1] + p2[1])*t_norm + (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1])*t_norm**2 + (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1])*t_norm**3)
                result.append((x, y))
        result.append(points[-1])
        return result

    def _paintSoft(self, layer, x, y, r, color, hardness):
        if hardness >= 100:
            layer.draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
            return
        steps = 20
        for i in range(steps):
            t = i / steps
            alpha = int((1 - (t ** (3 - 2 * hardness / 100))) * 255)
            cr = max(1, int(r * (1 - t)))
            clr = (color[0], color[1], color[2], alpha)
            layer.draw.ellipse([x-cr, y-cr, x+cr, y+cr], fill=clr)

    def _smudge(self, x, y):
        layer = self.layers[self.activeIdx]
        if layer.locked: return
        r = self.brushSize // 2
        crop = layer.image.crop((max(0,x-r*2), max(0,y-r*2), min(self.CW,x+r*2), min(self.CH,y+r*2)))
        blurred = crop.filter(ImageFilter.GaussianBlur(radius=r/4))
        layer.image.paste(blurred, (max(0,int(x-r*2)), max(0,int(y-r*2))))
        layer.draw = ImageDraw.Draw(layer.image)
        self._cacheDirty = True

    def _eyedrop(self, x, y):
        ix, iy = int(x), int(y)
        if 0 <= ix < self.CW and 0 <= iy < self.CH:
            for layer in reversed(self.layers):
                if not layer.visible: continue
                pixel = layer.image.getpixel((ix, iy))
                if pixel[3] > 0:
                    hex_color = f"#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"
                    self._setColor(hex_color)
                    self.tool = "brush"
                    self.toolVar.set("brush")
                    return
            self._setColor("#ffffff")

    def _fill(self, x, y):
        layer = self.layers[self.activeIdx]
        if layer.locked: return
        try:
            ImageDraw.floodfill(layer.image, (x, y),
                                self._rgba(self.brushColor, self.brushOpacity),
                                thresh=50)
            layer.draw = ImageDraw.Draw(layer.image)
            self._cacheDirty = True
            self._scheduleRender(fast=False)
        except Exception:
            pass

    def _rgba(self, hex_color, opacity=255):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (r, g, b, int(opacity))

    # * Render & Composite
    def _composite(self):
        # Timelapse playback: use temp images so live layers are never modified
        if self._playbackImages is not None:
            base = Image.new("RGBA", (self.CW, self.CH), (255, 255, 255, 255))
            for img in reversed(self._playbackImages):
                base = Image.alpha_composite(base, img)
            return base.convert("RGB")

        if not self._cacheDirty and self._cachedComposite is not None:
            return self._cachedComposite
        
        base = Image.new("RGBA", (self.CW, self.CH), (255, 255, 255, 255))
        
        for layer in reversed(self.layers):
            if not layer.visible: continue
            img = layer.image
            if layer.opacity < 255:
                img = img.copy()
                r, g, b, a = img.split()
                a = a.point(lambda p: int(p * layer.opacity / 255))
                img.putalpha(a)
            base = Image.alpha_composite(base, img)
        
        rgb = base.convert("RGB")
        self._cachedComposite = rgb
        self._cacheDirty = False
        return rgb

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

    def _doRender(self):
        self._renderPending = False
        self._lastRender = time.time()
        w  = self.tkCanvas.winfo_width()  or 800
        h  = self.tkCanvas.winfo_height() or 600

        # view params
        sw = int(self.CW * self.zoom)
        sh = int(self.CH * self.zoom)
        ox = self.offsetX if self.offsetX is not None else (w - sw) // 2
        oy = self.offsetY if self.offsetY is not None else (h - sh) // 2

        # Check if we need to crop (zoom > 1.0)
        need_crop = self.zoom > 1.05
        if need_crop:
            # Viewport in image coordinates
            vx1 = max(0, -ox / self.zoom)
            vy1 = max(0, -oy / self.zoom)
            vx2 = min(self.CW, vx1 + w / self.zoom)
            vy2 = min(self.CH, vy1 + h / self.zoom)
        else:
            vx1 = vy1 = 0.0
            vx2 = self.CW
            vy2 = self.CH

        composite = self._composite()

        if need_crop:
            crop = composite.crop((int(vx1), int(vy1), int(vx2), int(vy2)))
            filt = self._renderFilter(self._nextRenderFast)
            rw = max(1, int(round((vx2 - vx1) * self.zoom)))
            rh = max(1, int(round((vy2 - vy1) * self.zoom)))
            resized = crop.resize((rw, rh), filt)
            # Adjust offset so the cropped portion aligns correctly
            image_ox = int(round(ox + vx1 * self.zoom))
            image_oy = int(round(oy + vy1 * self.zoom))
        elif sw == self.CW and sh == self.CH:
            resized = composite
            image_ox, image_oy = ox, oy
        else:
            filt = self._renderFilter(self._nextRenderFast)
            resized = composite.resize((sw, sh), filt)
            image_ox, image_oy = ox, oy

        self.tkPhoto = ImageTk.PhotoImage(resized)

        self.tkCanvas.delete("all")
        self.tkCanvas.config(bg="#ffffff")
        
        self.tkCanvas.create_image(image_ox, image_oy, anchor="nw", image=self.tkPhoto)

        # Border
        self.tkCanvas.create_rectangle(ox, oy, ox+sw, oy+sh, outline=C["border"], width=1)
        self.tkCanvas.create_rectangle(ox+1, oy+1, ox+sw-1, oy+sh-1, outline="#222", width=1)

        # Ruler overlay
        if self.rulerActive:
            cx = int(ox + self.rulerX * self.zoom)
            cy = int(oy + self.rulerY * self.zoom)
            rad = math.radians(self.rulerAngle)
            length = 1000
            dx = math.cos(rad) * length
            dy = math.sin(rad) * length
            self.tkCanvas.create_line(cx-dx, cy-dy, cx+dx, cy+dy,
                                       fill=C["accent"], width=2, dash=(8, 4))

        # Frame overlay
        if self.frameEnabled:
            fs = int(self.frameSize * self.zoom)
            self.tkCanvas.create_rectangle(ox+fs, oy+fs, ox+sw-fs, oy+sh-fs,
                                            outline=self.frameColor, width=3, dash=(6, 2))

        # Selection rect
        if self.selectionRect and self.tool == "select":
            sx1, sy1, sx2, sy2 = self.selectionRect
            sx1 = int(ox + sx1 * self.zoom)
            sy1 = int(oy + sy1 * self.zoom)
            sx2 = int(ox + sx2 * self.zoom)
            sy2 = int(oy + sy2 * self.zoom)
            self.tkCanvas.create_rectangle(sx1, sy1, sx2, sy2,
                                            outline=C["accent"], width=2, dash=(4, 2))

        # Preview overlay (shapes)
        if self.previewX is not None and self.previewY is not None and self.shapeStartPoint:
            px1 = int(ox + self.shapeStartPoint[0] * self.zoom)
            py1 = int(oy + self.shapeStartPoint[1] * self.zoom)
            px2 = int(ox + self.previewX * self.zoom)
            py2 = int(oy + self.previewY * self.zoom)
            self.tkCanvas.create_oval(px2-4, py2-4, px2+4, py2+4, fill=C["accent"], outline="")
            self.tkCanvas.create_line(px1, py1, px2, py2, fill=C["accent"], width=1, dash=(3, 3))

        # Polyline/Bezier preview
        if self.tool == "shape":
            if self.polylinePoints:
                pts = [(ox + p[0]*self.zoom, oy + p[1]*self.zoom) for p in self.polylinePoints]
                for i in range(len(pts)-1):
                    self.tkCanvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1],
                                              fill=C["accent"], width=2, dash=(4, 2))
                if self.previewX is not None:
                    last = pts[-1]
                    px = ox + self.previewX * self.zoom
                    py = oy + self.previewY * self.zoom
                    self.tkCanvas.create_line(last[0], last[1], px, py, fill=C["accent"], width=1, dash=(3, 3))
            elif self.bezierAnchorPoints:
                pts = [(ox + p[0]*self.zoom, oy + p[1]*self.zoom) for p in self.bezierAnchorPoints]
                for p in pts:
                    self.tkCanvas.create_oval(p[0]-3, p[1]-3, p[0]+3, p[1]+3, fill=C["accent"], outline="")
                if len(pts) >= 2:
                    for i in range(len(pts)-1):
                        self.tkCanvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1],
                                                  fill=C["accent"], width=1, dash=(3, 3))

    # * Undo/Redo
    def _saveUndo(self):
        snapshot = []
        for l in self.layers:
            snapshot.append(l.snapshot())
        self.undoStack.append(snapshot)
        self.redoStack.clear()
        if len(self.undoStack) > 100:
            self.undoStack.pop(0)

    def _undo(self):
        if not self.undoStack:
            return
        # Save current state for redo
        current = []
        for l in self.layers:
            current.append(l.snapshot())
        self.redoStack.append(current)
        
        snapshot = self.undoStack.pop()
        for i, l in enumerate(self.layers):
            if i < len(snapshot):
                l.restore(snapshot[i])
        self._cacheDirty = True
        self._scheduleRender(fast=False)

    def _redo(self):
        if not self.redoStack:
            return
        # Save current state for undo
        current = []
        for l in self.layers:
            current.append(l.snapshot())
        self.undoStack.append(current)
        
        snapshot = self.redoStack.pop()
        for i, l in enumerate(self.layers):
            if i < len(snapshot):
                l.restore(snapshot[i])
        self._cacheDirty = True
        self._scheduleRender(fast=False)

    # * Layers
    def _addLayer(self):
        layer = Layer(f"Layer {len(self.layers)}", self.CW, self.CH)
        self.layers.append(layer)
        self.activeIdx = len(self.layers) - 1
        self._refreshLayerPanel()
        self._scheduleRender(fast=False)

    def _delLayer(self):
        if len(self.layers) <= 1:
            return
        del self.layers[self.activeIdx]
        self.activeIdx = min(self.activeIdx, len(self.layers) - 1)
        self._refreshLayerPanel()
        self._scheduleRender(fast=False)

    def _moveLayer(self, direction):
        idx = self.activeIdx
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self.layers):
            return
        self.layers[idx], self.layers[new_idx] = self.layers[new_idx], self.layers[idx]
        self.activeIdx = new_idx
        self._refreshLayerPanel()
        self._cacheDirty = True
        self._scheduleRender(fast=False)

    def _importImageToLayer(self):
        fp = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")])
        if not fp: return
        try:
            img = Image.open(fp).convert("RGBA")
            l_idx = len(self.layers)
            layer = Layer(f"Imported {len(self.layers)}", self.CW, self.CH)
            img.thumbnail((self.CW, self.CH), Image.Resampling.LANCZOS)
            x = (self.CW - img.width) // 2
            y = (self.CH - img.height) // 2
            layer.image.paste(img, (x, y))
            layer.draw = ImageDraw.Draw(layer.image)
            self.layers.append(layer)
            self.activeIdx = l_idx
            self._refreshLayerPanel()
            self._cacheDirty = True
            self._scheduleRender(fast=False)
            
            # Save to strokeHistory for timelapse
            if self.startTime == 0.0:
                self.startTime = time.time()
            import base64
            buf = io.BytesIO()
            img.save(buf, "PNG")
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            self.strokeHistory.append([{
                "mode": "import_image", "img": img_b64,
                "layer_idx": l_idx, "t": 0.0,
            }])
            self._updateStrokeLabel()
        except Exception as e:
            messagebox.showerror("Error", f"Could not import image:\n{e}")

    def _onLayerOpacityChange(self, val):
        idx = self.activeIdx
        if 0 <= idx < len(self.layers):
            self.layers[idx].opacity = int(float(val) * 2.55)
            self._cacheDirty = True
            self._scheduleRender(fast=False)

    def _refreshLayerPanel(self):
        for w in self.layerFrame.winfo_children():
            w.destroy()
        for i, layer in enumerate(self.layers):
            is_active = (i == self.activeIdx)
            bg = C["accent"] if is_active else C["card"]
            fg = "#fff" if is_active else C["text"]
            row = tk.Frame(self.layerFrame, bg=bg, cursor="hand2")
            row.pack(fill="x", pady=1, ipadx=4, ipady=2)

            # Visibility toggle
            vis_text = "\u25c9" if layer.visible else "\u25cb"
            vis = tk.Label(row, text=vis_text, bg=bg, fg=C["dim"], cursor="hand2",
                          font=("Segoe UI", 9))
            vis.pack(side="left", padx=(4, 2))
            vis.bind("<Button-1>", lambda e, i=i: self._toggleVis(i))

            # Name
            name_lbl = tk.Label(row, text=layer.name, bg=bg, fg=fg,
                                font=("Segoe UI", 9), anchor="w", width=16)
            name_lbl.pack(side="left", fill="x", expand=True, padx=2)

            # Timelapse disable button
            tl_vis = "\u25a0" if i not in self.timelapseDisabledLayers else "\u25a1"
            tl_btn = tk.Label(row, text=tl_vis, bg=bg, fg=C["accent"] if i not in self.timelapseDisabledLayers else C["dim"],
                              cursor="hand2", font=("Segoe UI", 8))
            tl_btn.pack(side="right", padx=2)
            tl_btn.bind("<Button-1>", lambda e, i=i: self._toggleTimelapseLayerSecret(i))

            # Select layer
            for w in [row] + row.winfo_children():
                try:
                    w.bind("<Button-1>", lambda e, i=i: self._selectLayer(i), "+")
                except:
                    pass
            
            if is_active:
                self.layerOpacityVar.set(int(layer.opacity / 2.55))

    def _selectLayer(self, idx):
        self.activeIdx = idx
        self._refreshLayerPanel()
        self._scheduleRender(fast=False)

    def _toggleVis(self, idx):
        self.layers[idx].visible = not self.layers[idx].visible
        self._cacheDirty = True
        self._scheduleRender(fast=False)
        self._refreshLayerPanel()

    def _toggleTimelapseLayerSecret(self, idx):
        if idx in self.timelapseDisabledLayers:
            self.timelapseDisabledLayers.remove(idx)
        else:
            self.timelapseDisabledLayers.add(idx)
        self._refreshLayerPanel()

    # * Timelapse
    def _startPlayback(self):
        if not self.strokeHistory:
            return
        if self.isPlaying: return
        self.isPlaying = True
        self.playBtn.config(text="\u25b6  Playing...", state="disabled")
        self.progressVar.set(0)
        threading.Thread(target=self._runPlayback, daemon=True).start()

    def _runPlayback(self):
        oldIdx = self.activeIdx
        # Create temporary PIL images so live layers are NEVER modified
        self._playbackImages = [
            Image.new("RGBA", (self.CW, self.CH), (0, 0, 0, 0))
            for _ in self.layers
        ]
        self._cacheDirty = True
        self.root.after(0, lambda: self._scheduleRender(fast=False))

        try:
            total = len(self.strokeHistory)
            for si, stroke in enumerate(self.strokeHistory):
                if not self.isPlaying: break
                prog = (si / total) * 100
                self.root.after(0, lambda p=prog: self.progressVar.set(p))
                if not stroke: continue

                lIdx = stroke[0].get("layer", 0)
                if lIdx >= len(self._playbackImages): lIdx = 0
                if lIdx in self.timelapseDisabledLayers:
                    continue
                img = self._playbackImages[lIdx]
                draw = ImageDraw.Draw(img)
                dur   = max((stroke[-1]["t"] - stroke[0]["t"]), 0.02)
                self.activeIdx = lIdx

                mode = stroke[0].get("mode", "brush")
                if mode == "import_image":
                    p0 = stroke[0]
                    try:
                        decoded = Image.open(io.BytesIO(base64.b64decode(p0["img"]))).convert("RGBA")
                        t_idx = p0.get("layer_idx", 0)
                        if t_idx < len(self._playbackImages):
                            self._playbackImages[t_idx].paste(decoded, (0, 0))
                    except Exception:
                        pass
                elif mode == "line":
                    p0, p1 = stroke[0], stroke[1]
                    self._drawLineToLayerPlayback(draw, p0["x"], p0["y"], p1["x"], p1["y"])
                elif mode == "bezier":
                    p0 = stroke[0]
                    p1_x, p1_y = p0.get("cx"), p0.get("cy")
                    p2_x, p2_y = p0.get("ex"), p0.get("ey")
                    self._drawBezierToLayerPlayback(draw, (p0["x"], p0["y"]), (p1_x, p1_y), (p2_x, p2_y))
                elif mode.startswith("shape_"):
                    shapeType = mode.split("_", 1)[1]
                    p0 = stroke[0]
                    ex, ey = p0.get("ex"), p0.get("ey")
                    self._drawShapeToLayerPlayback(draw, shapeType, p0["x"], p0["y"], ex, ey)
                elif mode == "bezier_path":
                    pts = [(pt["x"], pt["y"]) for pt in stroke]
                    self._drawSplineToLayerPlayback(draw, pts)
                elif mode == "polyline":
                    pts = [(pt["x"], pt["y"]) for pt in stroke]
                    self._drawPolylineToLayerPlayback(draw, pts)
                else:
                    n_points = len(stroke)
                    px = py = None
                    for pi, pt in enumerate(stroke):
                        if not self.isPlaying: break
                        x, y = pt["x"], pt["y"]
                        r    = pt["size"] // 2
                        clr  = self._rgba(pt["color"], pt["opacity"])
                        if pt["mode"] == "eraser":
                            draw.ellipse([x-r,y-r,x+r,y+r], fill=(0,0,0,0))
                        else:
                            if px is not None:
                                dist  = math.hypot(x-px, y-py)
                                steps = max(int(dist * 2), 2)
                                for i in range(steps+1):
                                    t  = i/steps
                                    xi = px+(x-px)*t; yi = py+(y-py)*t
                                    draw.ellipse([xi-r,yi-r,xi+r,yi+r], fill=clr)
                            else:
                                draw.ellipse([x-r,y-r,x+r,y+r], fill=clr)
                        px, py = x, y
                        self._cacheDirty = True
                        self.root.after(0, lambda: self._scheduleRender(fast=True))
                        point_delay = (dur / max(n_points, 1)) / self.playSpeed
                        time.sleep(max(0.012, point_delay))

            self.root.after(0, lambda: self.progressVar.set(100))
        finally:
            # Always clean up temp images — live layers are untouched
            self.isPlaying = False
            self._playbackImages = None
            self._cacheDirty = True
            self.activeIdx = oldIdx
            self.root.after(0, lambda: self.playBtn.config(
                text="\u25b6  Play Timelapse", state="normal"))
            self.root.after(0, lambda: self._scheduleRender(fast=False))

    # Playback helper methods (draw on temp ImageDraw objects only)
    def _drawLineToLayerPlayback(self, draw, x1, y1, x2, y2):
        r = self.brushSize // 2
        color = self._rgba(self.brushColor, self.brushOpacity)
        draw.line([x1, y1, x2, y2], fill=color, width=r*2)

    def _drawBezierToLayerPlayback(self, draw, p0, p1, p2):
        r = self.brushSize // 2
        color = self._rgba(self.brushColor, self.brushOpacity)
        steps = 100
        prevX, prevY = p0[0], p0[1]
        for i in range(1, steps + 1):
            t = i / steps
            mt = 1 - t
            xi = mt*mt*p0[0] + 2*mt*t*p1[0] + t*t*p2[0]
            yi = mt*mt*p0[1] + 2*mt*t*p1[1] + t*t*p2[1]
            draw.ellipse([xi-r, yi-r, xi+r, yi+r], fill=color)
            prevX, prevY = xi, yi

    def _drawShapeToLayerPlayback(self, draw, shapeType, x, y, ex, ey):
        color = self._rgba(self.brushColor, self.brushOpacity)
        r = self.brushSize
        if shapeType == "rect":
            draw.rectangle([x, y, ex, ey], outline=color, width=r)
        elif shapeType == "oval":
            draw.ellipse([x, y, ex, ey], outline=color, width=r)
        elif shapeType == "circle":
            cx, cy = (x+ex)//2, (y+ey)//2
            rad = max(1, int(math.hypot(ex-cx, ey-cy)))
            draw.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], outline=color, width=r)
        elif shapeType == "line":
            draw.line([x, y, ex, ey], fill=color, width=r)

    def _drawSplineToLayerPlayback(self, draw, pts):
        if len(pts) < 2: return
        color = self._rgba(self.brushColor, self.brushOpacity)
        r = self.brushSize
        if len(pts) == 2:
            draw.line(pts, fill=color, width=r)
        else:
            smooth = self._catmull_rom(pts, num_segments=12)
            draw.line(smooth, fill=color, width=r, joint='curve')

    def _drawPolylineToLayerPlayback(self, draw, pts):
        if len(pts) < 2: return
        color = self._rgba(self.brushColor, self.brushOpacity)
        r = self.brushSize
        draw.line(pts, fill=color, width=r, joint='curve')

    def _stopPlayback(self):
        self.isPlaying = False
        self._playbackImages = None
        self._cacheDirty = True
        self.root.after(0, lambda: self._scheduleRender(fast=False))
        self.playBtn.config(text="\u25b6  Play Timelapse", state="normal")

    def _updateStrokeLabel(self):
        if self.strokeLbl:
            self.strokeLbl.config(text=f"Strokes: {len(self.strokeHistory)}")

    def _viewParams(self):
        w = self.tkCanvas.winfo_width() or 800
        h = self.tkCanvas.winfo_height() or 600
        sw = int(self.CW * self.zoom)
        sh = int(self.CH * self.zoom)
        ox = self.offsetX if self.offsetX is not None else (w - sw) // 2
        oy = self.offsetY if self.offsetY is not None else (h - sh) // 2
        sx = sw / self.CW if self.CW > 0 else 1
        sy = sh / self.CH if self.CH > 0 else 1
        cropped = self.zoom > 1.05
        vx1 = max(0, -ox / self.zoom)
        vy1 = max(0, -oy / self.zoom)
        return ox, oy, vx1, vy1, sx, sy, cropped

    def _toScreen(self, img_x, img_y):
        w = self.tkCanvas.winfo_width() or 800
        h = self.tkCanvas.winfo_height() or 600
        sw = int(self.CW * self.zoom)
        sh = int(self.CH * self.zoom)
        ox = self.offsetX if self.offsetX is not None else (w - sw) // 2
        oy = self.offsetY if self.offsetY is not None else (h - sh) // 2
        return ox + img_x * self.zoom, oy + img_y * self.zoom

    # * Save/Project
    def _save(self, showPopup=True):
        try:
            preview = self._composite().copy()
            preview.thumbnail((256, 256), Image.LANCZOS)
            previewPath = os.path.join(self.projectPath, "preview.png")
            preview.save(previewPath, "PNG")
        except Exception:
            pass

        data = {
            "name": self.projectName,
            "canvasWidth": self.CW,
            "canvasHeight": self.CH,
            "activeLayerIdx": self.activeIdx,
            "layers": [l.toDict() for l in self.layers],
            "strokeHistory": self.strokeHistory,
            "timelapseDisabledLayers": sorted(self.timelapseDisabledLayers),
            "drawQuality": self.drawQuality,
            "renderQuality": self.renderQuality,
            "stabilizerVal": self.stabilizerVal,
            "stabilizerMethod": self.stabilizerMethod,
            "fadeEnabled": self.fadeEnabled,
            "forceFade": self.forceFade,
            "fadeStartPercent": self.fadeStartPercent,
            "fadeEndPercent": self.fadeEndPercent,
            "fadeShape": self.fadeShape,
            "customBrushes": self.customBrushes[:20],
            "savedAt": datetime.now().isoformat(),
        }
        path = os.path.join(self.projectPath, "projectData.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        if showPopup:
            messagebox.showinfo("Saved", f"Project saved to\n{self.projectPath}")

    def _exportPNG(self):
        fp = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("All", "*.*")],
            initialfile=f"{self.projectName}.png"
        )
        if not fp:
            return
        try:
            composite = self._composite()
            composite.save(fp, "PNG")
            messagebox.showinfo("Exported", f"Exported to\n{fp}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export:\n{e}")

    def _goHome(self):
        try:
            self._save(showPopup=False)
        except:
            pass
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("1060x680")
        self.root.state("normal")
        LaunchScreen(self.root)

    def _clearCanvas(self):
        if not messagebox.askyesno("Clear Canvas",
                                    "Hapus semua coretan di semua layer?\nTidak bisa di-undo."):
            return
        for layer in self.layers:
            layer.image = Image.new("RGBA", (self.CW, self.CH), (0, 0, 0, 0))
            layer.draw = ImageDraw.Draw(layer.image)
        self.strokeHistory.clear()
        self.undoStack.clear()
        self.redoStack.clear()
        self._cacheDirty = True
        self._scheduleRender(fast=False)
        self._updateStrokeLabel()


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = TkinterDnD.Tk() if 'TkinterDnD' in dir() else tk.Tk()
    root.configure(bg=C["bg"])
    app = LaunchScreen(root)
    root.mainloop()
