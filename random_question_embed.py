import tkinter as tk
import random
import threading
import time
import glob

BG_COLOR = "#1a1a2e"
FG_COLOR = "#e94560"

class App:
    def __init__(self, root):
        self.root = root
        root.title("随机点名")
        root.geometry("300x260")
        root.configure(bg=BG_COLOR)
        root.attributes("-topmost", True)
        root.after(500, self._force_top)

        self.all_names = []
        self.remaining = []
        self.running = False
        self._rolling = False
        self.current_class = ""

        files = glob.glob("class*.txt")
        if files:
            self.current_class = files[0]
            with open(self.current_class, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            self.all_names = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
            self.remaining = list(self.all_names)

        if not self.all_names:
            self.all_names = ["张三", "李四", "王五"]
            self.remaining = list(self.all_names)

        self.class_var = tk.StringVar(value=self.current_class.replace(".txt", "") or "默认")
        self.display_var = tk.StringVar(value="准备")
        self.hint_var = tk.StringVar(value="空格开始 | ESC换班")

        tk.Label(root, textvariable=self.class_var, font=("微软雅黑", 12), bg=BG_COLOR, fg="#aaa").pack(pady=5)
        tk.Label(root, textvariable=self.display_var, font=("微软雅黑", 32, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=15)

        self.progress = tk.Canvas(root, width=220, height=3, bg="#333", highlightthickness=0)
        self.progress.pack()
        self.progress_bar = self.progress.create_rectangle(0, 0, 0, 3, fill=FG_COLOR)

        tk.Label(root, textvariable=self.hint_var, font=("微软雅黑", 10), bg=BG_COLOR, fg="#888").pack(pady=5)

        btn_f = tk.Frame(root, bg=BG_COLOR)
        btn_f.pack(pady=5)
        self.start_btn = tk.Button(btn_f, text="开始 (空格)", font=("微软雅黑", 12), width=10,
                                   command=self._toggle, bg=FG_COLOR, fg="#1a1a2e", relief="flat")
        self.start_btn.pack(side="left", padx=4)
        tk.Button(btn_f, text="重置", font=("微软雅黑", 12), width=6,
                  command=self._reset_round, bg="#333", fg="#ccc", relief="flat").pack(side="left", padx=4)

        self.root.bind("<space>", lambda e: self._toggle())
        self.root.bind("<Return>", lambda e: self._toggle())
        self.root.bind("<BackSpace>", lambda e: self._reset_round())
        self.root.bind("<Escape>", lambda e: self._choose_class())

    def _force_top(self):
        try:
            self.root.attributes("-topmost", True)
            self.root.lift()
            self.root.after(500, self._force_top)
        except:
            pass

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
        self.display_var.set("滚动中...")
        self.hint_var.set("2秒后自动停")
        self.start_btn.config(text="停止", bg="#ff4444", fg="#fff")
        threading.Thread(target=self._roll, daemon=True).start()
        self.root.after(2000, self._stop)
        self._anim_progress(0)

    def _roll(self):
        while self._rolling:
            pool = self.remaining if self.remaining else self.all_names
            n = random.choice(pool)
            self.root.after(0, lambda name=n: self.display_var.set(name))
            time.sleep(0.05)

    def _anim_progress(self, elapsed):
        if not self.running:
            return
        ratio = min(elapsed / 2000, 1.0)
        self.progress.coords(self.progress_bar, 0, 0, int(220 * ratio), 3)
        if ratio < 1.0:
            self.root.after(30, lambda: self._anim_progress(elapsed + 30))

    def _stop(self):
        self.running = False
        self._rolling = False
        self.start_btn.config(text="开始 (空格)", bg=FG_COLOR, fg="#1a1a2e")
        pool = self.remaining if self.remaining else self.all_names
        result = random.choice(pool)
        if self.remaining and result in self.remaining:
            self.remaining.remove(result)
        self.display_var.set(result)
        self.hint_var.set(f"剩余 {len(self.remaining)} 人 | 退格重置")
        self.progress.coords(self.progress_bar, 0, 0, 0, 3)

    def _reset_round(self):
        self.remaining = list(self.all_names)
        self.display_var.set("已重置")
        self.hint_var.set("空格开始新一轮")

    def _choose_class(self):
        files = glob.glob("class*.txt")
        if not files:
            return
        idx = files.index(self.current_class) if self.current_class in files else 0
        self.current_class = files[(idx + 1) % len(files)]
        with open(self.current_class, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.all_names = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
        self.remaining = list(self.all_names)
        self.class_var.set(self.current_class.replace(".txt", ""))
        self.display_var.set("准备")
        self.hint_var.set("已换班，空格开始")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
