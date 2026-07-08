"""

MADE BY PLUS1ERRRRRRRRRRRR

I LOVE YOU ALL  

"""
import os
import tkinter as tk
from tkinter import filedialog
import pygame

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ============================================================
# THEME - change these to restyle the whole app
# ============================================================
BG_COLOR = "#FF6767"       # background (dark green - Game Boy style)
PANEL_COLOR = "#FF6767"    # panel / button background
FG_COLOR = "#DCFF50"       # pixel/icon color (light green)
TEXT_COLOR = "#FAFCB9"
HILITE_COLOR = "#FFB1A7"   # hover / selected color
FONT = ("Courier New", 11, "bold")  # monospace = more "pixel" feeling
                                     # (install "Press Start 2P" for real pixel font
                                     #  and swap FONT to ("Press Start 2P", 8))

PIXEL = 4  # size of one icon "pixel" in real screen pixels

# ============================================================
# YOUR OWN IMAGES - put file paths here to use custom pictures
# instead of the drawn pixel icons / flat color panel.
# Leave as None to keep the built-in look for that item.
# Recommended: small PNGs (e.g. 40x40 for buttons), ideally already
# pixel-art styled so they don't blur when scaled.
# ============================================================
BUTTON_IMAGES = {
    "play": "\\images\\play.png",      # e.g. "images/play.png"
    "pause": "\\images\\pause.png",     # e.g. "images/pause.png"
    "next": "\\images\\next.png",
    "prev": "\\images\\prev.png",
    "stop": "\\images\\pause.png",
}
BUTTON_SIZE = (40, 40)          # width, height each button image is scaled to
PANEL_BG_IMAGE = "images\\bg.png"           # e.g. "images/panel_bg.png" - fills the whole window
WINDOW_SIZE = (320, 420)        # used to scale PANEL_BG_IMAGE to fill the window


def load_image(path, size):
    """Loads and pixel-scales an image file. Returns None if unavailable."""
    if not path or not PIL_AVAILABLE or not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGBA")
    img = img.resize(size, Image.NEAREST)  # NEAREST keeps pixel-art crisp
    return ImageTk.PhotoImage(img)

# ============================================================
# ICONS - each string in the grid is a row, each char a pixel
# ============================================================
ICONS = {
    "play": [
        "#.......",
        "##......",
        "###.....",
        "####....",
        "###.....",
        "##......",
        "#.......",
    ],
    "pause": [
        "##.##",
        "##.##",
        "##.##",
        "##.##",
        "##.##",
    ],
    "next": [
        "#....#..",
        "##...#..",
        "###..#..",
        "####.#..",
        "###..#..",
        "##...#..",
        "#....#..",
    ],
    "prev": [
        "..#....#",
        "..#...##",
        "..#..###",
        "..#.####",
        "..#..###",
        "..#...##",
        "..#....#",
    ],
    "stop": [
        "######",
        "######",
        "######",
        "######",
        "######",
        "######",
    ],
    "vol_up": [
        "..#.",
        ".###",
        "#####"[:4],
    ],
}


def draw_icon(canvas, grid, color, pad=6):
    """Draws a pixel-grid icon centered on a canvas, returns (w, h) in px."""
    rows = len(grid)
    cols = max(len(r) for r in grid)
    w = cols * PIXEL
    h = rows * PIXEL
    for ry, row in enumerate(grid):
        for cx, ch in enumerate(row):
            if ch == "#":
                x0 = pad + cx * PIXEL
                y0 = pad + ry * PIXEL
                canvas.create_rectangle(
                    x0, y0, x0 + PIXEL, y0 + PIXEL,
                    fill=color, outline=color
                )
    return w + pad * 2, h + pad * 2


class PixelButton(tk.Canvas):
    """A clickable canvas-based button. Uses a custom image from
    BUTTON_IMAGES if one is set for this icon_name, otherwise falls
    back to the drawn pixel-icon grid."""

    def __init__(self, master, icon_name, command=None, **kwargs):
        w, h = BUTTON_SIZE
        super().__init__(
            master, width=w, height=h, bg=PANEL_COLOR,
            highlightthickness=0, **kwargs
        )
        self.command = command
        self.icon_name = icon_name
        self._photo = None  # keep a reference so it isn't garbage collected
        self._redraw()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self._set_bg(HILITE_COLOR))
        self.bind("<Leave>", lambda e: self._set_bg(PANEL_COLOR))

    def _redraw(self):
        self.delete("all")
        img_path = BUTTON_IMAGES.get(self.icon_name)
        photo = load_image(img_path, BUTTON_SIZE)
        if photo:
            self._photo = photo  # keep reference
            self.create_image(BUTTON_SIZE[0] // 2, BUTTON_SIZE[1] // 2, image=photo)
        else:
            draw_icon(self, ICONS[self.icon_name], FG_COLOR)

    def set_icon(self, icon_name):
        self.icon_name = icon_name
        self._redraw()

    def _set_bg(self, color):
        self.config(bg=color)

    def _on_click(self, event):
        if self.command:
            self.command()


class PixelPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("nigger songs")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")

        # Hide the OS title bar for a fully custom look
        self.overrideredirect(True)
        self._enable_dragging()

        # Optional full-window background picture
        self._bg_photo = load_image(PANEL_BG_IMAGE, WINDOW_SIZE)
        if self._bg_photo:
            bg_label = tk.Label(self, image=self._bg_photo, bd=0)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.bind("<Button-1>", self._start_move)
            bg_label.bind("<B1-Motion>", self._do_move)

        pygame.mixer.init()

        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)

        self._build_ui()
        self._poll_song_end()

    # ---------------- Window dragging (needed since we removed the title bar) ----------------
    def _enable_dragging(self):
        self._drag_x = 0
        self._drag_y = 0
        self.bind("<Button-1>", self._start_move)
        self.bind("<B1-Motion>", self._do_move)

    def _start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_move(self, event):
        x = self.winfo_x() + event.x - self._drag_x
        y = self.winfo_y() + event.y - self._drag_y
        self.geometry(f"+{x}+{y}")

    # ---------------- UI ----------------
    def _build_ui(self):
        top_bar = tk.Frame(self, bg=BG_COLOR)
        top_bar.pack(fill="x", pady=(10, 4), padx=10)

        title = tk.Label(
            top_bar, text="nigger songs", font=("Courier New", 16, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR
        )
        title.pack(side="left")

        close_btn = tk.Label(
            top_bar, text="[X]", font=FONT, bg=BG_COLOR, fg=TEXT_COLOR, cursor="hand2"
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.destroy())

        load_btn = tk.Button(
            self, text="[ LOAD FOLDER ]", command=self.load_folder,
            bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT,
            activebackground=HILITE_COLOR, relief="flat", bd=2
        )
        load_btn.pack(pady=4)

        list_frame = tk.Frame(self, bg=BG_COLOR)
        list_frame.pack(padx=10, pady=6)
        self.listbox = tk.Listbox(
            list_frame, width=36, height=8, bg=PANEL_COLOR, fg=TEXT_COLOR,
            font=FONT, selectbackground=HILITE_COLOR, activestyle="none",
            highlightthickness=1, highlightbackground=FG_COLOR, bd=0
        )
        self.listbox.pack()
        self.listbox.bind("<Double-Button-1>", self._on_song_double_click)

        self.now_playing = tk.Label(
            self, text="NO SONG LOADED", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT
        )
        self.now_playing.pack(pady=(4, 8))

        controls = tk.Frame(self, bg=BG_COLOR)
        controls.pack(pady=4)

        self.prev_btn = PixelButton(controls, "prev", command=self.prev_song)
        self.prev_btn.grid(row=0, column=0, padx=4)

        self.play_btn = PixelButton(controls, "play", command=self.toggle_play)
        self.play_btn.grid(row=0, column=1, padx=4)

        self.stop_btn = PixelButton(controls, "stop", command=self.stop_song)
        self.stop_btn.grid(row=0, column=2, padx=4)

        self.next_btn = PixelButton(controls, "next", command=self.next_song)
        self.next_btn.grid(row=0, column=3, padx=4)

        vol_frame = tk.Frame(self, bg=BG_COLOR)
        vol_frame.pack(pady=(8, 12))
        tk.Label(vol_frame, text="VOL", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT).pack(side="left", padx=(0, 6))
        self.vol_scale = tk.Scale(
            vol_frame, from_=0, to=100, orient="horizontal",
            bg=PANEL_COLOR, fg=TEXT_COLOR, troughcolor=BG_COLOR,
            highlightthickness=0, showvalue=False, length=140,
            command=self._on_volume_change
        )
        self.vol_scale.set(int(self.volume * 100))
        self.vol_scale.pack(side="left")

    # ---------------- Logic ----------------
    def load_folder(self):
        folder = filedialog.askdirectory(title="Select folder with your songs")
        if not folder:
            return
        songs = [f for f in os.listdir(folder) if f.lower().endswith((".mp3", ".wav", ".ogg"))]
        songs.sort()
        self.playlist = [os.path.join(folder, f) for f in songs]
        self.listbox.delete(0, tk.END)
        for f in songs:
            self.listbox.insert(tk.END, f)
        if self.playlist:
            self.current_index = 0
            self.listbox.selection_set(0)
            self.now_playing.config(text=self._short_name(self.playlist[0]))

    def _short_name(self, path):
        name = os.path.basename(path)
        return name[:32] + "..." if len(name) > 32 else name

    def _on_song_double_click(self, event):
        sel = self.listbox.curselection()
        if sel:
            self.current_index = sel[0]
            self.play_current()

    def play_current(self):
        if not self.playlist or self.current_index < 0:
            return
        path = self.playlist[self.current_index]
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.is_playing = True
        self.play_btn.set_icon("pause")
        self.now_playing.config(text=self._short_name(path))
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.current_index)

    def toggle_play(self):
        if not self.playlist:
            return
        if self.current_index == -1:
            self.current_index = 0

        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_btn.set_icon("play")
        else:
            if pygame.mixer.music.get_busy() or pygame.mixer.music.get_pos() > 0:
                pygame.mixer.music.unpause()
            else:
                self.play_current()
                return
            self.is_playing = True
            self.play_btn.set_icon("pause")

    def stop_song(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_btn.set_icon("play")

    def next_song(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current()

    def prev_song(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_current()

    def _on_volume_change(self, val):
        self.volume = int(val) / 100
        pygame.mixer.music.set_volume(self.volume)

    def _poll_song_end(self):
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.next_song()
        self.after(500, self._poll_song_end)


if __name__ == "__main__":
    app = PixelPlayer()
    app.mainloop()
