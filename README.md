# 随机点名（行草版）

## 功能
- 华文行草字体显示（字体文件随 exe 打包，无需目标电脑安装）
- 多班切换：点标题 / 点"换班"按钮 / 按 Esc 均可换班
- 换班时名单、剩余人数同步重置（真·切换，不是原地转圈）
- 点击名字 / 空格 = 开始·停止；重置 / Backspace = 重抽

## 名单命名规则
- `class数字.txt` → 显示为「X班」（如 `class428.txt` → 428班）
- `class名称.txt` → 显示为「名称」（如 `class土木1班.txt` → 土木1班）
- 不带 `class` 前缀的 txt 不会被识别
- 每行一个名字，`#` 开头为注释

## 固化行草字体的步骤
1. 把 `STXINGKA.TTF`（华文行草）放到仓库根目录
2. `build.yml` 里已有 `--add-data "STXINGKA.TTF;."`，无需改动
3. 提交后 Actions 打包，exe 内即含字体，任意电脑均显示行草

## 文件结构
```
random-question/
├── random_question_embed.py   # 主程序
├── build.yml                  # GitHub Actions 构建配置
├── STXINGKA.TTF               # 华文行草字体（需自行放入）
├── class1.txt                 # 1班名单
├── class2.txt                 # 2班名单
└── README.md
```
