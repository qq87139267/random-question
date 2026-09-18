import tkinter as tk
import random
import os
import sys
import re

# 路径处理（兼容exe与py）
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()

# 样式与尺寸
BG_COLOR = "#1a1a2e"
ACCENT = "#4cc9f0"
WIN_W, WIN_H = 320, 200
MIN_W, MIN_H = 280, 160

FONT_NAME = ("华文行草", "华文行书", "行体", "微软雅黑")
FONT_SIZE_NAME = 51
FONT_SIZE_TITLE = 16
FONT_SIZE_BTN = 12

class RandomNameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("下一位~")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(MIN_W, MIN_H)
        
        # 右上角定位（兼容DPI）
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
            screen_w = ctypes.windll.user32.GetSystemMetrics(0)
            screen_h = ctypes.windll.user32.GetSystemMetrics(1)
        except Exception:
            self.root.update_idletasks()
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
        
        x = screen_w - WIN_W - 15
        y = 15
        self.root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")
        
        self.classes = {}
        self.class_keys = []
        self.current_idx = 0
        self.current_class = ""
        self.pool = []
        self.used = []
        self.running = False
        self.roll_timer = None
        
        self._load_classes()
        if self.class_keys:
            self.current_class = self.class_keys[0]
            self.pool = list(self.classes[self.current_class])
        else:
            self.pool = []
        
        # 变量
        self.title_var = tk.StringVar(value=self.current_class if self.current_class else "无班级")
        self.name_var = tk.StringVar(value="准备" if self.pool else "无名单")
        
        # 布局
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 标题（班级）
        title = tk.Label(root, textvariable=self.title_var, font=(FONT_NAME, FONT_SIZE_TITLE, "bold"),
                         fg=ACCENT, bg=BG_COLOR)
        title.grid(row=0, column=0, pady=(10, 0))
        
        # 名字显示（可点击）
        self.name_label = tk.Label(root, textvariable=self.name_var,
                                   font=(FONT_NAME, FONT_SIZE_NAME, "bold"),
                                   fg="#ffffff", bg=BG_COLOR, pady=10)
        self.name_label.grid(row=1, column=0, sticky="nsew")
        self.name_label.bind("<Button-1>", lambda e: self._toggle())
        
        # 进度
        self.progress = tk.Label(root, text="", font=("微软雅黑", 9), fg="#888", bg=BG_COLOR)
        self.progress.grid(row=2, column=0, pady=(0, 5))
        
        # 按钮区
        btn_frame = tk.Frame(root, bg=BG_COLOR)
        btn_frame.grid(row=3, column=0, pady=5, padx=10, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        self.start_btn = tk.Button(btn_frame, text="开始", command=self._toggle,
                                   font=(FONT_NAME, FONT_SIZE_BTN, "bold"),
                                   bg=ACCENT, fg="white", relief=tk.FLAT)
        self.start_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        switch_btn = tk.Button(btn_frame, text="换班", command=self._switch_class,
                               font=(FONT_NAME, FONT_SIZE_BTN), bg="#4361ee", fg="white", relief=tk.FLAT)
        switch_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        reset_btn = tk.Button(btn_frame, text="重置", command=self._reset,
                              font=(FONT_NAME, FONT_SIZE_BTN), bg="#888", fg="white", relief=tk.FLAT)
        reset_btn.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="ew")
        
        # 触屏提示
        hint = tk.Label(root, text="点击名字:开始/停止", font=("微软雅黑", 8), fg="#555", bg=BG_COLOR)
        hint.grid(row=4, column=0, pady=(0, 5))
    
    def _load_classes(self):
        try:
            files = os.listdir(BASE_DIR)
            for f in files:
                if re.match(r"class.*\.txt", f, re.IGNORECASE):
                    path = os.path.join(BASE_DIR, f)
                    names = []
                    for enc in ["utf-8", "gbk"]:
                        try:
                            with open(path, "r", encoding=enc) as fp:
                                names = [l.strip() for l in fp if l.strip()]
                            break
                        except UnicodeDecodeError:
                            continue
                    if names:
                        cls = re.sub(r"class|\.txt", "", f, flags=re.IGNORECASE).strip("_")
                        display = f"{cls}班" if cls.isdigit() else (cls or "默认")
                        self.classes[display] = names
                        self.class_keys.append(display)
            self.class_keys.sort()
        except Exception:
            pass
    
    def _toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()
    
    def _start(self):
        if not self.pool:
            if self.classes:
                self.pool = list(self.classes[self.current_class])
                self.used = []
            else:
                return
        
        self.running = True
        self.start_btn.config(text="停止", bg="#ef5350", fg="white")
        self.name_label.config(fg="#ff4d4f")  # 滚动：柔红
        self._roll()
    
    def _stop(self):
        self.running = False
        self.start_btn.config(text="开始", bg=ACCENT, fg="white")
        if self.roll_timer:
            self.root.after_cancel(self.roll_timer)
            self.roll_timer = None
    
    def _roll(self):
        if not self.running:
            return
        if self.pool:
            self.name_var.set(random.choice(self.pool))
        self.roll_timer = self.root.after(80, self._roll)
        if not hasattr(self, '_roll_count'):
            self._roll_count = 0
        self._roll_count += 1
        if self._roll_count >= 25:
            self._roll_count = 0
            self._auto_stop()
    
    def _auto_stop(self):
        if not self.running:
            return
        self.running = False
        self.start_btn.config(text="开始", bg=ACCENT, fg="white")
        if self.roll_timer:
            self.root.after_cancel(self.roll_timer)
            self.roll_timer = None
        
        chosen = self.name_var.get()
        if chosen in self.pool:
            self.pool.remove(chosen)
            self.used.append(chosen)
        
        # 停止：抽中金色，抽完变红，默认白
        if not self.pool:
            self.name_label.config(fg="#ff4d4f")  # 抽完红
        else:
            self.name_label.config(fg="#ffd700")  # 抽中金
        
        total = len(self.classes[self.current_class])
        self.progress.config(text=f"剩余 {len(self.pool)}/{total}")
    
    def _switch_class(self, init=False):
        if not init and self.class_keys:
            self.current_idx = (self.current_idx + 1) % len(self.class_keys)
            self.current_class = self.class_keys[self.current_idx]
        elif self.class_keys:
            self.current_class = self.class_keys[0]
        
        if self.current_class:
            self.title_var.set(self.current_class)
            self.pool = list(self.classes[self.current_class])
            self.used = []
            self.name_var.set("准备")
            self.name_label.config(fg="#ffffff")  # 换班白
            self.progress.config(text="")
        self._stop()
    
    def _reset(self):
        if self.current_class:
            self.pool = list(self.classes[self.current_class])
            self.used = []
            self.name_var.set("准备")
            self.name_label.config(fg="#ffffff")  # 重置白
            self.progress.config(text="")
        self._stop()


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomNameApp(root)
    root.mainloop()
