# pixelart

使用 Unicode 半块字符 `▀`（U+2580）将图片渲染为终端像素画的 CLI 工具。每两个纵向像素分别映射为一个字符的前景色和背景色，将纵向分辨率翻倍。

```bash
pixelart cat.jpg -w 120 | head
```

## 安装

```bash
pip install -e .
```

## 使用方法

```bash
# 终端渲染（自动检测终端宽度）
pixelart <图片路径>

# 指定宽度
pixelart <图片路径> -w 80

# 灰度 ASCII
pixelart <图片路径> -n

# 256 色模式
pixelart <图片路径> --256color

# 直接运行（无需安装）
python pixelart.py <图片路径>
```

### HTML 预览

```bash
python pixelart_html.py <图片路径> [宽度]
# 生成 {图片路径}.html，在浏览器中打开即可预览
```

## 技术原理

利用终端字符 `▀`（上半块）的前景色和背景色分别承载两个纵向像素，每个终端字符行对应两个像素行，纵向分辨率翻倍。

三种颜色模式：
- **truecolor**（默认） — 24 位 RGB，`\033[38;2;r;g;b` + `\033[48;2;r;g;b`
- **256color** — 6×6×6 色彩立方体
- **grayscale** — ASCII 灰度字符

相邻像素颜色相同时跳过重复的 ANSI 转义码，减少输出体积。

## 依赖

- Python >= 3.9
- [Pillow](https://python-pillow.org/) >= 10.0
