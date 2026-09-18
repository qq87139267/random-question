# -*- coding: utf-8 -*-
"""
随机点名（触屏友好完整版）
------------------------------------------------
功能：
  - 窗口自动贴屏幕【右上角】+ 持续强制置顶（PPT / 大屏不遮挡）
  - 自动扫描 exe 同目录下的 class1.txt / class2.txt ...（每行一个名字，#开头为备注）
  - 一个班点完自动不重复；全部点完自动重置
  - 空格 / 回车 = 开始·停止；ESC = 换班；退格 = 重置本轮
  - 【触屏 / 无键盘】点按钮即可：换班 / 开始 / 重置；直接戳中间大名字也能开始·停止

名单文件示例（UTF-8 编码，与 exe 放同一文件夹）：
    class1.txt
    ---------
    # 一班
    张三
    李四
    ...

打包：pyinstaller --onefile --windowed --name "随机点名" random_question_embed.py
"""
import os
import sys
import glob
import random
import time
import threading

import tkinter as tk
from tkinter import font as tkfont

# ============ 外观配置 ============
BG_COLOR = "#1a1a2e"
FG_COLOR = "#e94560"
BTN_FONT = ("微软雅黑", 13)
NAME_FONT = ("微软雅黑", 34, "bold")
HINT_FONT = ("微软雅黑", 10)
TITLE_FONT = ("微软雅黑", 12)
WINDOW_W, WINDOW_H = 340, 230
MARGIN = 10  # 距屏幕边缘边距


def resource_path(rel):
    """兼容 PyInstaller 打包后的资源路径（读取同目录 class*.txt）"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("随机点名")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")

        # ---- 触屏按钮要够大 ----
        try:
            tkfont.Font(name="TkDefaultFont", exists=True)
        except Exception:
            pass

        # 状态数据
        self.all_names = []
        self.remaining = []
        self.running = False
        self._rolling = False
        self.class_files = []
        self.class_index = 0
        self.current_class = ""

        self.class_var = tk.StringVar(value="无班级")
        self.display_var = tk.StringVar(value="准备")
        self.hint_var = tk.StringVar(value="点「开始」或戳名字开始")

        self._build_ui()
        self._load_class_list()
        self._load_current_class()

        # 启动后定位 + 持续置顶
        self.root.after(50, self._place_top_right)
        self.root.after(200, self._force_top)

        # 键盘快捷键（有键盘时也可用）
        self.root.bind("<space>", lambda e: self._toggle())
        self.root.bind("<Return>", lambda e: self._toggle())
        self.root.bind("<BackSpace>", lambda e: self._reset_round())
        self.root.bind("<Escape>", lambda e: self._choose_class())

    # ---------------- UI ----------------
    def _build_ui(self):
        tk.Label(self.root, textvariable=self.class_var, font=TITLE_FONT,
                 bg=BG_COLOR, fg="#aaaaaa").pack(pady=(8, 0))

        # 名字显示区（可点击 = 开始/停止）
        self.display_label = tk.Label(self.root, textvariable=self.display_var,
                                     font=NAME_FONT, bg=BG_COLOR, fg=FG_COLOR,
                                     cursor="hand2", height=2)
        self.display_label.pack(pady=6)
        self.display_label.bind("<Button-1>", lambda e: self._toggle())

        # 进度条
        self.progress = tk.Canvas(self.root, width=260, height=4, bg="#333333",
                                  highlightthickness=0)
        self.progress.pack(pady=4)
        self.progress_bar = self.progress.create_rectangle(0, 0, 0, 4, fill=FG_COLOR)

        tk.Label(self.root, textvariable=self.hint_var, font=HINT_FONT,
                 bg=BG_COLOR, fg="#888888").pack(pady=(2, 6))

        # 触屏按钮区（无键盘也能操作）
        btn_f = tk.Frame(self.root, bg=BG_COLOR)
        btn_f.pack(pady=4)
        tk.Button(btn_f, text="换班", font=BTN_FONT, width=6, height=2,
                  command=self._choose_class, bg="#333333", fg="#dddddd",
                  relief="flat", activebackground="#444444").pack(side="left", padx=4)
        self.start_btn = tk.Button(btn_f, text="开始", font=BTN_FONT, width=6, height=2,
                                   command=self._toggle, bg=FG_COLOR, fg="#1a1a2e",
                                   relief="flat", activebackground="#ff6b81")
        self.start_btn.pack(side="left", padx=4)
        tk.Button(btn_f, text="重置", font=BTN_FONT, width=6, height=2,
                  command=self._reset_round, bg="#333333", fg="#dddddd",
                  relief="flat", activebackground="#444444").pack(side="left", padx=4)

    # ---------------- 窗口位置 / 置顶 ----------------
    def _place_top_right(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        x = sw - WINDOW_W - MARGIN
        y = MARGIN
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

    def _force_top(self):
        try:
            self.root.attributes("-topmost", True)
            self.root.lift()
            self.root.after(500, self._force_top)
        except Exception:
            pass

    # ---------------- 班级 / 名单 ----------------
    def _load_class_list(self):
        files = sorted(glob.glob(resource_path("class*.txt")))
        self.class_files = files

    def _load_current_class(self):
        if not self.class_files:
            self.all_names = ["张三", "李四", "王五"]
            self.remaining = list(self.all_names)
            self.current_class = ""
            self.class_var.set("默认名单")
            return
        self.current_class = self.class_files[self.class_index]
        with open(self.current_class, "r", encoding="utf-8") as f:
            lines = f.readlines()
        names = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
        self.all_names = names
        self.remaining = list(self.all_names)
        base = os.path.splitext(os.path.basename(self.current_class))[0]
        self.class_var.set(base)

    def _choose_class(self):
        if not self.class_files:
            self.display_var.set("无名单")
            self.hint_var.set("请把 class*.txt 与 exe 放一起")
            return
        self.class_index = (self.class_index + 1) % len(self.class_files)
        self._load_current_class()
        self.display_var.set("准备")
        self.hint_var.set(f"已换班：{self.class_var.get()}  （戳名字开始）")
        self.progress.coords(self.progress_bar, 0, 0, 0, 4)

    # ---------------- 点名逻辑 ----------------
    def _toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        if not self.remaining:
            self.remaining = list(self.all_names)
        self.running = True
        self._rolling = True
        self.display_var.set("滚动中…")
        self.hint_var.set("2 秒后自动停")
        self.start_btn.config(text="停止", bg="#ff4444", fg="#ffffff")
        threading.Thread(target=self._roll, daemon=True).start()
        self.root.after(2000, self._stop)
        self._anim_progress(0)

    def _roll(self):
        pool = self.remaining if self.remaining else self.all_names
        while self._rolling and pool:
            n = random.choice(pool)
            self.root.after(0, lambda name=n: self.display_var.set(name))
            time.sleep(0.05)

    def _anim_progress(self, elapsed):
        if not self.running:
            return
        ratio = min(elapsed / 2000, 1.0)
        self.progress.coords(self.progress_bar, 0, 0, int(260 * ratio), 4)
        if ratio < 1.0:
            self.root.after(30, lambda: self._anim_progress(elapsed + 30))

    def _stop(self):
        self.running = False
        self._rolling = False
        self.start_btn.config(text="开始", bg=FG_COLOR, fg="#1a1a2e")
        pool = self.remaining if self.remaining else self.all_names
        result = random.choice(pool) if pool else "—"
        if self.remaining and result in self.remaining:
            self.remaining.remove(result)
        self.display_var.set(result)
        self.hint_var.set(f"剩余 {len(self.remaining)} 人 | 点「重置」重开")
        self.progress.coords(self.progress_bar, 0, 0, 0, 4)

    def _reset_round(self):
        self.remaining = list(self.all_names)
        self.display_var.set("已重置")
        self.hint_var.set("戳名字或点「开始」开始")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
