# -*- coding: utf-8 -*-
import os
import sys
import glob
import random
import tkinter as tk
from tkinter import font as tkfont

# ========== 路径处理（关键修复：强制基于 exe 所在目录） ==========
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ========== 配置 ==========
WIN_W = 340
WIN_H = 200
BG_COLOR = "#1a1a2e"
FG_COLOR = "#e0e0e0"
ACCENT = "#4fc3f7"
BTN_BG = "#16213e"
BTN_FG = "#b0bec5"

# ========== 班级名单加载 ==========
def load_classes():
    """扫描 BASE_DIR 下所有 class*.txt，支持多数字（class1/class428等）"""
    classes = {}
    pattern = os.path.join(BASE_DIR, "class*.txt")
    files = sorted(glob.glob(pattern))
    
    if not files:
        # 没有找到任何 class*.txt，用内置测试名单
        classes["默认"] = ["张三", "李四", "王五", "赵六", "钱七"]
        return classes
    
    for fpath in files:
        fname = os.path.basename(fpath)
        # 从文件名提取班级标识：class428.txt → "428班"
        stem = os.path.splitext(fname)[0]  # class428
        class_id = stem.replace("class", "") or "1"
        class_name = f"{class_id}班" if class_id.isdigit() else stem
        
        names = []
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        names.append(line)
        except (UnicodeDecodeError, OSError):
            # UTF-8 失败则尝试 GBK（兼容旧文件）
            try:
                with open(fpath, "r", encoding="gbk") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            names.append(line)
            except Exception:
                continue
        
        if names:
            classes[class_name] = names
    
    if not classes:
        classes["默认"] = ["张三", "李四", "王五"]
    
    return classes


# ========== 主程序 ==========
class RandomNameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("随机点名")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        # 右上角定位
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        x = screen_w - WIN_W - 10
        y = 10
        self.root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")
        
        # 持续置顶
        self.root.attributes("-topmost", True)
        self.root.after(500, self._force_top)
        
        # 加载班级
        self.classes = load_classes()
        self.class_keys = list(self.classes.keys())
        self.current_idx = 0
        self.current_class = self.class_keys[0]
        self.pool = list(self.classes[self.current_class])
        self.used = []
        self.running = False
        self.roll_timer = None
        
        self._build_ui()
        
        # 键盘绑定
        self.root.bind("<space>", lambda e: self._toggle())
        self.root.bind("<Escape>", lambda e: self._switch_class())
        self.root.bind("<BackSpace>", lambda e: self._reset())
        
        self.root.mainloop()
    
    def _force_top(self):
        """每500ms强制置顶"""
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.after(500, self._force_top)
    
    def _build_ui(self):
        """构建界面"""
        # 标题
        self.title_var = tk.StringVar(value=self.current_class)
        title_label = tk.Label(self.root, textvariable=self.title_var,
                               font=("微软雅黑", 12), fg=ACCENT, bg=BG_COLOR)
        title_label.pack(pady=(10, 5))
        
        # 名字显示（可点击）
        self.name_var = tk.StringVar(value="准备")
        self.name_label = tk.Label(self.root, textvariable=self.name_var,
                                   font=("微软雅黑", 28, "bold"),
                                   fg=FG_COLOR, bg=BG_COLOR, cursor="hand2")
        self.name_label.pack(pady=10)
        self.name_label.bind("<Button-1>", lambda e: self._toggle())
        
        # 进度条
        self.progress = tk.Label(self.root, text="", font=("微软雅黑", 9),
                                 fg="#666", bg=BG_COLOR)
        self.progress.pack()
        
        # 按钮区
        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack(pady=(10, 5))
        
        tk.Button(btn_frame, text="换班", font=("微软雅黑", 11), width=5, height=2,
                  command=self._switch_class, bg=BTN_BG, fg=BTN_FG,
                  relief="flat", activebackground="#1a3a5c").pack(side="left", padx=4)
        
        self.start_btn = tk.Button(btn_frame, text="开始", font=("微软雅黑", 11, "bold"),
                                   width=5, height=2, command=self._toggle,
                                   bg=ACCENT, fg="#1a1a2e", relief="flat")
        self.start_btn.pack(side="left", padx=4)
        
        tk.Button(btn_frame, text="重置", font=("微软雅黑", 11), width=5, height=2,
                  command=self._reset, bg=BTN_BG, fg=BTN_FG,
                  relief="flat", activebackground="#1a3a5c").pack(side="left", padx=4)
        
        # 底部提示
        hint = tk.Label(self.root, text="空格:开始 | ESC:换班 | 退格:重置 | 点击名字:开始",
                        font=("微软雅黑", 8), fg="#555", bg=BG_COLOR)
        hint.pack(pady=(5, 0))
    
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
        self._roll()
    
    def _stop(self):
        self.running = False
        self.start_btn.config(text="开始", bg=ACCENT, fg="#1a1a2e")
        if self.roll_timer:
            self.root.after_cancel(self.roll_timer)
            self.roll_timer = None
        self.progress.config(text="")
    
    def _roll(self):
        if not self.running:
            return
        
        if self.pool:
            name = random.choice(self.pool)
            self.name_var.set(name)
        
        self.roll_timer = self.root.after(80, self._roll)
        
        # 2秒后自动停止
        if not hasattr(self, '_roll_count'):
            self._roll_count = 0
        self._roll_count += 1
        if self._roll_count >= 25:  # 25 × 80ms ≈ 2秒
            self._roll_count = 0
            self._auto_stop()
    
    def _auto_stop(self):
        if not self.running:
            return
        self.running = False
        self.start_btn.config(text="开始", bg=ACCENT, fg="#1a1a2e")
        if self.roll_timer:
            self.root.after_cancel(self.roll_timer)
            self.roll_timer = None
        
        # 从池里移除已抽中的人
        chosen = self.name_var.get()
        if chosen in self.pool:
            self.pool.remove(chosen)
            self.used.append(chosen)
        
        # 进度显示
        total = len(self.classes[self.current_class])
        remaining = len(self.pool)
        self.progress.config(text=f"剩余 {remaining}/{total}")
    
    def _switch_class(self):
        self.current_idx = (self.current_idx + 1) % len(self.class_keys)
        self.current_class = self.class_keys[self.current_idx]
        self.title_var.set(self.current_class)
        self.pool = list(self.classes[self.current_class])
        self.used = []
        self.name_var.set("准备")
        self.progress.config(text="")
        self._stop()
    
    def _reset(self):
        self.pool = list(self.classes[self.current_class])
        self.used = []
        self.name_var.set("准备")
        self.progress.config(text="")
        self._stop()


if __name__ == "__main__":
    RandomNameApp()
