import tkinter as tk
from tkinter import font

# ================= 基础配置（请结合你原有变量） =================
ACTIVE_ALPHA = 1.0      # 活跃状态不透明度
IDLE_ALPHA = 0.5        # 静置20秒后半透明
IDLE_TIME = 20000       # 20秒（毫秒）

root = tk.Tk()
root.title("💪 → 下一位~~就你啦 ~~~👉")
root.geometry("300x200")
root.attributes("-alpha", ACTIVE_ALPHA)

# 假设的类名与状态（请替换为你实际的变量）
current_class = "426"
remaining_count = 4  # 测试用，实际为全班人数

# ================= UI 布局（参考你的截图） =================
top_label = tk.Label(root, text="默认", fg="#1E90FF", bg="#0A0F1C", font=("华文行楷", 24))
top_label.pack(pady=10)

name_var = tk.StringVar(value="赵六")
name_label = tk.Label(root, textvariable=name_var, fg="#FFD700", bg="#0A0F1C", font=("华文行楷", 60))
name_label.pack(expand=True, fill="both")

bottom_label = tk.Label(root, text=f"剩余 {remaining_count}/4", fg="#CCCCCC", bg="#0A0F1C", font=("微软雅黑", 12))
bottom_label.pack(side="bottom", pady=5)

btn_frame = tk.Frame(root, bg="#0A0F1C")
btn_frame.pack(side="bottom", pady=10)

btn_start = tk.Button(btn_frame, text="开始", width=8)
btn_start.grid(row=0, column=0, padx=5)
btn_reset = tk.Button(btn_frame, text="重置", width=8)
btn_reset.grid(row=0, column=1, padx=5)
btn_switch = tk.Button(btn_frame, text="换班", width=8)
btn_switch.grid(row=0, column=2, padx=5)

# ================= 核心逻辑：换班 + 重置 + 抽名 =================
def do_switch(event=None):
    """全局换班逻辑（Esc触发 / 按钮触发）"""
    global current_class, remaining_count
    # 示例：426 <-> 428 切换
    if current_class == "426":
        current_class = "428"
    else:
        current_class = "426"
    
    # 这里插入你真实的：读取 class{current_class}.txt 并重置名单逻辑
    remaining_count = 4  # 实际应设为 len(全班名单)
    name_var.set("（换班成功）")
    bottom_label.config(text=f"剩余 {remaining_count}/{remaining_count}")
    
    # 强制恢复不透明 & 重置计时
    reset_alpha()
    print(f"已换至 {current_class} 班")
    return "break"  # 关键：截断事件，防止按钮/其他控件拦截

def do_reset():
    """重置当前班级进度"""
    global remaining_count
    remaining_count = 4  # 实际恢复全班总数
    bottom_label.config(text=f"剩余 {remaining_count}/{remaining_count}")
    name_var.set("默认")
    reset_alpha()

def do_draw():
    """抽名逻辑（示例）"""
    global remaining_count
    if remaining_count > 0:
        remaining_count -= 1
        name_var.set("赵六")  # 实际为随机抽取
        bottom_label.config(text=f"剩余 {remaining_count}/4")
    reset_alpha()

btn_start.config(command=do_draw)
btn_reset.config(command=do_reset)
btn_switch.config(command=do_switch)

# ================= 核心逻辑：半透明 & 点击恢复 =================
idle_timer = None

def set_idle_alpha():
    """静置20秒后变半透明"""
    root.attributes("-alpha", IDLE_ALPHA)

def reset_alpha(event=None):
    """点击/按键/操作时恢复100%不透明，并重启20秒计时"""
    root.attributes("-alpha", ACTIVE_ALPHA)
    global idle_timer
    if idle_timer:
        root.after_cancel(idle_timer)
    idle_timer = root.after(IDLE_TIME, set_idle_alpha)

# 1. 点击窗口任意处恢复不透明（用 bind_all 确保全局）
root.bind_all("<Button-1>", reset_alpha, add="+")
# 2. 键盘按键也恢复不透明（防止打字/按Esc时误入半透明）
root.bind_all("<Key>", reset_alpha, add="+")

# ================= 核心修复：Esc 全局换班 =================
# 必须用 bind_all，且加 add="+"，确保不被按钮焦点拦截
root.bind_all("<Escape>", do_switch, add="+")

# 启动初始计时
reset_alpha()

root.mainloop()
