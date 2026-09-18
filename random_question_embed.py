import os
import re
import random
import tkinter as tk
from tkinter import font

# ========== 基础配置 ==========
ACCENT = "#1677ff"
BTN_BG = "#1a3a5c"
BTN_FG = "#ffffff"
BG_COLOR = "#111111"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 字号（行草建议 58，比行书大一点更清晰）
FONT_SIZE_NAME = 58
_CANDIDATE_FONTS = ["华文行草", "华文行楷", "华文草书", "楷体", "微软雅黑"]

FONT_TITLE = ("微软雅黑", 14, "bold")
FONT_BTN = ("微软雅黑", 11)
FONT_PROGRESS = ("微软雅黑", 10)

# ⚠️ 不再顶层探测字体，留空，等 root 创建后再定
FONT_NAME = "微软雅黑"  # 临时默认值，后面会覆盖


def pick_available_font(root):
    """必须在 tk.Tk() 之后调用"""
    global FONT_NAME
    try:
        available = set(font.families(root))
        for f in _CANDIDATE_FONTS:
            if f in available:
                FONT_NAME = f
                return FONT_NAME
    except Exception:
        pass
    FONT_NAME = "微软雅黑"
    return FONT_NAME


class RandomNameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💪 →下一位 ～～～👉")
        self.root.geometry("320x200")
        self.root.minsize(280, 160)
        self.root.configure(bg=BG_COLOR)

        # ✅ 关键：先有 root，再探测字体
        pick_available_font(root)

        self.name_font = (FONT_NAME, FONT_SIZE_NAME, "bold")

        # 班级数据（示例，保持你原有逻辑）
        self.classes = {}
        self._load_classes()
        self.class_keys = list(self.classes.keys())
        self.current_idx = 0
        self.current_class = self.class_keys[0] if self.class_keys else "默认"

        self.pool = list(self.classes.get(self.current_class, []))
        self.used = []
        self.running = False
        self.roll_timer = None
        self._roll_count = 0

        # 标题
        self.title_var = tk.StringVar(value=self.current_class)
        tk.Label(root, textvariable=self.title_var, font=FONT_TITLE,
                 fg="#fff", bg=BG_COLOR).pack(pady=(8, 0))

        # 名字显示区
        name_frame = tk.Frame(root, bg="#111", relief="ridge", bd=2)
        name_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)

        self.name_var = tk.StringVar(value="准备")
        self.name_label = tk.Label(
            name_frame, textvariable=self.name_var,
            font=self.name_font, fg="#ffffff", bg="#111"
        )
        self.name_label.pack(expand=True, fill=tk.BOTH, pady=10)
        self.name_label.bind("<Button-1>", lambda e: self._toggle())

        # 进度
        self.progress = tk.Label(root, text="", font=FONT_PROGRESS,
                                 fg="#888", bg=BG_COLOR)
        self.progress.pack()

        # 按钮
        btn_frame = tk.Frame(root, bg=BG_COLOR)
        btn_frame.pack(pady=5)

        self.start_btn = tk.Button(btn_frame, text="开始", font=("微软雅黑", 11, "bold"),
                                   width=5, height=2, command=self._toggle,
                                   bg=ACCENT, fg="#1a1a2e", relief="flat")
        self.start_btn.pack(side="left", padx=4)

        tk.Button(btn_frame, text="重置", font=("微软雅黑", 11), width=5, height=2,
                  command=self._reset, bg=BTN_BG, fg=BTN_FG,
                  relief="flat", activebackground="#1a3a5c").pack(side="left", padx=4)

        # 快捷键
        root.bind("<space>", lambda e: self._toggle())
        root.bind("<Escape>", lambda e: self._switch_class())
        root.bind("<BackSpace>", lambda e: self._reset())

        hint = tk.Label(root, text="空格:开始 | ESC:换班 | 退格:重置 | 点击名字:开始",
                        font=("微软雅黑", 8), fg="#555", bg=BG_COLOR)
        hint.pack(pady=(5, 0))

    def _load_classes(self):
        # 保持你原有的 class428.txt 逻辑（简版示意）
        try:
            path = os.path.join(BASE_DIR, "class428.txt")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    names = [l.strip() for l in f if l.strip()]
                self.classes["class428"] = names
            else:
                self.classes["默认"] = ["张三", "李四", "王五", "赵六"]
        except Exception:
            self.classes["默认"] = ["张三", "李四", "王五", "赵六"]

    def _toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        if not self.pool:
            self.pool = list(self.classes[self.current_class])
            self.used = []
        self.running = True
        self.start_btn.config(text="停止", bg="#ef5350", fg="white")
        self.name_label.config(fg="#ff4d4f")
        self._roll_count = 0
        self._roll()

    def _roll(self):
        if not self.running:
            return
        if self.pool:
            self.name_var.set(random.choice(self.pool))
        self.roll_timer = self.root.after(80, self._roll)
        self._roll_count += 1
        if self._roll_count >= 25:
            self._auto_stop()

    def _stop(self):
        self.running = False
        self.start_btn.config(text="开始", bg=ACCENT, fg="#1a1a2e")
        if self.roll_timer:
            self.root.after_cancel(self.roll_timer)
            self.roll_timer = None
        self.progress.config(text="")

    def _auto_stop(self):
        self.running = False
        self.start_btn.config(text="开始", bg=ACCENT, fg="#1a1a2e")
        if self.roll_timer:
            self.root.after_cancel(self.roll_timer)
            self.roll_timer = None

        chosen = self.name_var.get()
        if chosen in self.pool:
            self.pool.remove(chosen)
            self.used.append(chosen)

        if not self.pool:
            self.name_label.config(fg="#ff4d4f")
        else:
            self.name_label.config(fg="#ffd700")

        total = len(self.classes[self.current_class])
        remaining = len(self.pool)
        self.progress.config(text=f"剩余 {remaining}/{total}")

    def _switch_class(self):
        if not self.class_keys:
            return
        self.current_idx = (self.current_idx + 1) % len(self.class_keys)
        self.current_class = self.class_keys[self.current_idx]
        self.title_var.set(self.current_class)
        self.pool = list(self.classes[self.current_class])
        self.used = []
        self.name_var.set("准备")
        self.name_label.config(fg="#ffffff")
        self.progress.config(text="")
        self._stop()

    def _reset(self):
        self.pool = list(self.classes[self.current_class])
        self.used = []
        self.name_var.set("准备")
        self.name_label.config(fg="#ffffff")
        self.progress.config(text="")
        self._stop()


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomNameApp(root)
    root.mainloop()
