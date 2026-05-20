# TikTok Video Downloader

A modern, terminal-based TikTok video downloader built with Python. Features an interactive menu system powered by [Rich](https://github.com/Textualize/rich) tables with rounded borders, multiple download methods, batch downloads, no-watermark support, and persistent configuration.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Rich](https://img.shields.io/badge/Rich-UI-orange)

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Interactive Mode](#interactive-mode)
  - [Command Line Mode](#command-line-mode)
  - [Batch Download](#batch-download)
  - [No Watermark](#no-watermark)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | Description |
|---------|-------------|
| **Interactive Menu** | Beautiful terminal UI with Rich table layouts |
| **Multiple Methods** | yt-dlp, API No Watermark, Direct download |
| **No Watermark** | Remove TikTok watermark via API |
| **Batch Download** | Process multiple URLs at once |
| **Video Metadata** | View title, uploader, duration, views, likes |
| **Progress Bar** | Real-time download progress with ETA |
| **Persistent Config** | Save default settings to `~/.config/tiktok_downloader/settings.ini` |
| **System Check** | Verify all dependencies before running |

---

## Installation

### Prerequisites

- Python 3.7 or higher
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (required)

### Step 1: Clone the Repository

```bash
git clone https://github.com/keika-sy/tiktok-downloader.git
cd tiktok-downloader
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install yt-dlp rich requests
```

### Step 3: Verify Installation

```bash
python tiktok_downloader.py
# Select option 6 (System Check)
```

Expected output:
```
+-------------------------------+
|         SYSTEM CHECK          |
+----------+--------+-----------+
| Component| Status | Version   |
+----------+--------+-----------+
| Python   | OK     | 3.11.0    |
| yt-dlp   | OK     | 2025.01.01|
| rich     | OK     | 13.7.0    |
| requests | OK     | 2.31.0    |
+----------+--------+-----------+
```

---

## Usage

### Interactive Mode (Recommended)

Launch the interactive menu for a guided experience:

```bash
python tiktok_downloader.py
```

This will display the main menu:

```
+-------------------------------+
|           MAIN MENU           |
+----+---------------+----------+
| No | Option        | Icon     |
+----+---------------+----------+
| 1  | Download Video| VID      |
| 2  | Batch Download| BAT      |
| 3  | Video Info    | INF      |
| 4  | No Watermark  | NOWM     |
| 5  | Settings      | SET      |
| 6  | System Check  | CHK      |
| 0  | Exit          | EXT      |
+----+---------------+----------+
```

**Navigation:**
1. Enter the number of your choice
2. Follow the on-screen prompts
3. Press Enter to continue after each operation

### Command Line Mode

For quick downloads without the interactive menu:

#### Download Single Video

```bash
# Using default method (yt-dlp)
python tiktok_downloader.py -u "https://vt.tiktok.com/xxxxx"

# Specify method
python tiktok_downloader.py -u "URL" -m ytdlp
python tiktok_downloader.py -u "URL" -m api
python tiktok_downloader.py -u "URL" -m direct
```

#### No Watermark Download

```bash
# Download without TikTok watermark
python tiktok_downloader.py -u "URL" --no-watermark
```

#### Custom Output Directory

```bash
# Save to specific folder
python tiktok_downloader.py -u "URL" -o ~/Videos
python tiktok_downloader.py -u "URL" -o /sdcard/Download
```

#### Video Info Only

```bash
# View metadata without downloading
python tiktok_downloader.py -u "URL" --info
```

#### Open Settings

```bash
# Configure preferences via interactive menu
python tiktok_downloader.py --settings
```

### Batch Download

Download multiple videos at once from input.

#### Interactive Batch Mode

```bash
python tiktok_downloader.py
# Select option 2 (Batch Download)
# Enter URLs one per line, blank line to finish
```

#### CLI Batch Mode

```bash
# Download multiple URLs
python tiktok_downloader.py -u "URL1" "URL2" "URL3" --batch

# Set concurrent workers
python tiktok_downloader.py -u "URL1" "URL2" --batch --max-workers 5
```

#### Review Results

After completion, a summary table will display:

```
+-------------------------------+
|   BATCH DOWNLOAD SUMMARY      |
+----+--------+--------+--------+
| #  | Status | Title  | Size   |
+----+--------+--------+--------+
| 1  | OK     | Vid 1  | 2.3 MB |
| 2  | OK     | Vid 2  | 5.1 MB |
| 3  | FAIL   | Vid 3  | -      |
+----+--------+--------+--------+
| Successful: 2 | Failed: 1 | Total: 3 |
+-------------------------------+
```

### No Watermark

Download TikTok videos without the TikTok watermark:

**Interactive mode:**
```bash
python tiktok_downloader.py
# Select option 4 (No Watermark)
# Enter TikTok URL
```

**CLI mode:**
```bash
python tiktok_downloader.py -u "URL" --no-watermark
```

This uses the TikTok API to fetch the clean video source.

---

## Configuration

Settings are automatically saved to `~/.config/tiktok_downloader/settings.ini`.

### Change Settings via Interactive Menu

1. Run `python tiktok_downloader.py`
2. Select option **5 (Settings)**
3. Choose the setting to modify:

```
+-------------------------------+
|           SETTINGS            |
+----+----------------+---------+
| No | Setting        | Current |
+----+----------------+---------+
| 1  | Output Dir     | ~/Down..|
| 2  | Default Method | ytdlp   |
| 3  | Max Workers    | 3       |
| 4  | Auto Open      | false   |
| 5  | Thumbnails     | true    |
| 6  | Quality        | best    |
| 7  | Save Metadata  | true    |
| 8  | Clear Screen   | true    |
| 9  | Reset Default  | -       |
| 0  | Back to Menu   | -       |
+----+----------------+---------+
```

### Manual Config File

You can also edit the config file directly:

```bash
nano ~/.config/tiktok_downloader/settings.ini
```

Example configuration:

```ini
[General]
download_dir = /home/user/Downloads/TikTok_Videos
default_method = ytdlp
max_workers = 3
auto_open_folder = false
show_thumbnails = true

[Download]
quality = best
no_watermark = false
save_metadata = true

[UI]
theme = default
show_progress_bar = true
clear_screen = true
```

### Config Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `download_dir` | string | `~/Downloads/TikTok_Videos` | Download destination folder |
| `default_method` | string | `ytdlp` | Default download method (ytdlp/api/direct) |
| `max_workers` | integer | `3` | Concurrent download threads (1-10) |
| `auto_open_folder` | boolean | `false` | Open folder after download |
| `show_thumbnails` | boolean | `true` | Display thumbnails in info view |
| `quality` | string | `best` | Video quality preset |
| `save_metadata` | boolean | `true` | Save `.json` metadata file |
| `clear_screen` | boolean | `true` | Auto clear terminal on menu |

---

## Project Structure

```
tiktok-downloader/
|-- tiktok_downloader.py    # Main script (entry point)
|-- requirements.txt        # Python dependencies
|-- README.md               # Documentation
|-- LICENSE                 # MIT License
|-- .gitignore              # Git ignore rules
|-- examples/
|   |-- urls.txt            # Example batch URL file
```

---

## Requirements

### Python Packages

| Package | Minimum Version | Purpose |
|---------|-----------------|---------|
| Python  | 3.7+            | Runtime environment |
| yt-dlp  | 2023.0.0        | Video download engine |
| rich    | 13.0.0          | Terminal UI and tables |
| requests| 2.31.0          | HTTP requests for API |

### Supported Platforms

- Linux (Ubuntu, Debian, Fedora, Arch)
- macOS (Intel & Apple Silicon)
- Windows (10/11)
- Termux (Android)

---

## Troubleshooting

### yt-dlp Not Found

**Error:** `yt-dlp not installed`

**Solution:**
```bash
pip install --upgrade yt-dlp
```

If still not found, try:
```bash
python -m pip install yt-dlp
```

### Permission Denied (Linux/macOS/Termux)

**Error:** `Permission denied`

**Solution:**
```bash
chmod +x tiktok_downloader.py
```

Or run with Python explicitly:
```bash
python tiktok_downloader.py
```

Also check your download directory permissions:
```bash
# Android/Termux - use sdcard
/sdcard/Download/TikTok_Videos

# Linux/Mac
~/Downloads/TikTok_Videos

# Windows
C:\Users\Name\Downloads\TikTok_Videos
```

### Slow Download Speeds

**Possible causes and solutions:**

1. **Network issues:** Check your internet connection
2. **VPN/Proxy:** Some VPNs slow down TikTok traffic
3. **Peak hours:** Try downloading during off-peak hours
4. **Method selection:** Try `direct` method for faster fallback

### API Method Fails

**Error:** `Failed to download via API`

**Possible causes:**
- Video is private or deleted
- TikTok API rate limiting
- URL is invalid or expired

**Solution:**
- Try `yt-dlp` method instead
- Verify the URL in your browser first
- Wait a few minutes and retry

### Video Info Cannot Be Retrieved

**Possible causes:**
- Video is private or region-blocked
- Video has been removed
- URL is invalid

**Solution:** Verify the URL in your browser first.

### Config File Corrupted

**Solution:** Delete and regenerate:
```bash
rm ~/.config/tiktok_downloader/settings.ini
python tiktok_downloader.py
# Settings will be recreated with defaults
```

### Unicode/Encoding Errors

**Solution:** Ensure your terminal supports UTF-8:
```bash
export PYTHONIOENCODING=utf-8
```

---

## Contributing

Contributions are welcome. Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes:
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push** to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/keika-sy/tiktok-downloader.git
cd tiktok-downloader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate   # Windows

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black tiktok_downloader.py
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

```
MIT License

Copyright (c) 2025 keika-sy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The powerful download engine
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [requests](https://requests.readthedocs.io/) - HTTP library for Python

---

## Disclaimer

This tool is for educational and personal use only. Respect copyright laws and TikTok's Terms of Service. The authors are not responsible for any misuse of this software.

**Do not use this tool to:**
- Download copyrighted content without permission
- Redistribute downloaded content commercially
- Circumvent content protection mechanisms
- Violate any local or international laws

---

## Contact

For questions, issues, or suggestions:

- Open an [Issue](https://github.com/keika-sy/tiktok-downloader/issues)
- Start a [Discussion](https://github.com/keika-sy/tiktok-downloader/discussions)

---

**Happy Downloading!**
