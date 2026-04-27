# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

一个将图片渲染为终端像素画的 Python 工具，利用 Unicode 半块字符 `▀`（U+2580）实现。每两个纵向像素分别映射为一个字符的前景色和背景色，从而将纵向分辨率翻倍。包含终端渲染器和 HTML 渲染器（用于浏览器预览）。

## 运行方式

```bash
# 安装为 CLI 工具
pip install -e .

# 使用 CLI
pixelart <图片路径> [-w 宽度] [-n] [--256color]

# 不安装直接运行
python pixelart.py <图片路径>

# HTML 渲染器（未注册为 CLI 入口点）
python pixelart_html.py <图片路径> [宽度]
```

CLI 参数：`-w` 设置输出宽度（列数，默认自动检测终端宽度），`-n` 输出灰度 ASCII，`--256color` 使用 256 色而非 24 位真彩色。

## 架构

- **`pixelart.py`** — 可安装的 CLI 工具。处理流程：`main()` → `detect_color_mode()` → `load_and_resize()` → `render_image()` → stdout。三种颜色模式：`truecolor`（24 位 `\033[38;2;r;g;b`）、`256color`（6×6×6 色彩立方体，通过 `rgb_to_256()` 映射）、`grayscale`（ASCII 灰度字符）。相邻像素颜色相同时跳过重复的 ANSI 转义码以减少输出长度。默认宽度为终端宽度。

- **`pixelart_html.py`** — 独立脚本，**未注册为 CLI 入口点**。`render_html(image_path, width=66)` 返回完整 HTML 字符串，`__main__` 才负责写文件到 `{原文件名}.html`。使用相同的半块字符技术，但输出 `<span style="color:rgb(…);background:rgb(…)">▀</span>` 而非 ANSI 转义序列。

- **`pyproject.toml`** — 包配置。入口点 `pixelart` 映射到 `pixelart:main`。唯一依赖：Pillow。当前无测试框架。

## 注意事项

- **错误处理** — `main()` 对 `BrokenPipeError` 静默退出（pipe 场景如 `pixelart ... | head`），对 `KeyboardInterrupt` 返回 130。这是有意设计，不要为这些情况添加 stderr 输出。
- **根目录中的 `.txt` / `.html` 文件**是运行示例输出，不是源码。项目缺少 `.gitignore`，未来添加时应忽略这些生成文件。
- **`pixelart_html.py` 的默认宽度 66** 与 CLI 自动检测终端宽度的行为不同，修改时注意保持一致或有意保持差异。
