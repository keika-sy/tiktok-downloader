# TikTok Video Downloader

A comprehensive Python tool to download TikTok videos with multiple methods, batch support, and a clean terminal UI using Rich Table `box.ROUNDED`.

## Features

| Feature | Description |
|---------|-------------|
| Single Download | Download one video with method selection |
| Batch Download | Download multiple URLs from file or input |
| No Watermark | Remove TikTok watermark via API |
| Video Info | View metadata without downloading |
| Settings | Persistent configuration via INI file |
| System Check | Verify all dependencies |
| Rich UI | Clean minimalist terminal interface |

## Requirements

```bash
pip install yt-dlp rich requests
```

Or install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/keika-sy/tiktok-downloader.git
cd tiktok-downloader
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Tool

```bash
python tiktok_downloader.py
```

## Usage

### Interactive Mode (Recommended)

Launch the interactive menu with Rich UI:

```bash
python tiktok_downloader.py
```

Menu options:
- `1` Download Video - Download a single TikTok video
- `2` Batch Download - Download multiple videos at once
- `3` Video Info - View video metadata without downloading
- `4` No Watermark - Download video without TikTok watermark
- `5` Settings - Configure preferences
- `6` System Check - Verify dependencies
- `0` Exit - Quit the application

### CLI - Single Download

Download one video using default settings:

```bash
python tiktok_downloader.py -u "https://vt.tiktok.com/xxxxx"
```

Specify method and output:

```bash
python tiktok_downloader.py -u "URL" -m ytdlp -o /path/to/folder
```

### CLI - Batch Download

Download multiple URLs at once:

```bash
python tiktok_downloader.py -u "URL1" "URL2" "URL3" --batch
```

Set concurrent workers:

```bash
python tiktok_downloader.py -u "URL1" "URL2" --batch --max-workers 5
```

### CLI - No Watermark

Download video without TikTok watermark:

```bash
python tiktok_downloader.py -u "URL" --no-watermark
```

### CLI - Video Info Only

View metadata without downloading:

```bash
python tiktok_downloader.py -u "URL" --info
```

### CLI - Open Settings

Configure preferences via interactive menu:

```bash
python tiktok_downloader.py --settings
```

### CLI - Interactive Mode Flag

Force interactive menu even with other args:

```bash
python tiktok_downloader.py --interactive
```

## Download Methods

| Method | Description | Best For |
|--------|-------------|----------|
| yt-dlp | Best quality, recommended | All videos |
| API No WM | Without watermark | Clean videos |
| Direct | Fallback method | Quick download |

### Method Selection in Interactive Mode

When downloading, you will be prompted to select a method:

```
1. yt-dlp     - Best quality, recommended
2. API No WM  - Without watermark
3. Direct     - Fallback method
```

## Settings

Settings are stored in `~/.config/tiktok_downloader/settings.ini` and persist between sessions.

### Available Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Download Directory | `~/Downloads/TikTok_Videos` | Save location for downloaded videos |
| Default Method | `yt-dlp` | Preferred download method (ytdlp/api/direct) |
| Max Workers | `3` | Number of concurrent downloads (1-10) |
| Auto Open Folder | `false` | Automatically open folder after download |
| Show Thumbnails | `true` | Display video thumbnails in info view |
| Quality | `best` | Video quality preset (best/1080p/720p/480p/360p/audio) |
| Save Metadata | `true` | Save `.json` file with video metadata |
| Clear Screen | `true` | Auto clear terminal when returning to menu |

### Changing Settings

1. Select menu option `5` (Settings) in interactive mode
2. Choose the setting number to modify
3. Enter new value or toggle ON/OFF
4. Settings auto-save to INI file

### Reset to Default

In Settings menu, select option `9` to restore all defaults.

## Project Structure

```
tiktok-downloader/
|-- tiktok_downloader.py    # Main script
|-- requirements.txt        # Python dependencies
|-- README.md               # Documentation
|-- .gitignore              # Git ignore rules
```

## Output Files

When `Save Metadata` is enabled (default), each download creates two files:

```
20260520_114534.mp4       # Video file
20260520_114534.json      # Metadata file (title, views, likes, etc.)
```

To disable metadata files, go to Settings and set `Save Metadata` to OFF.

## System Check

Run dependency verification:

```bash
python tiktok_downloader.py
# Then select option 6 (System Check)
```

Or via CLI:

```bash
python tiktok_downloader.py --check
```

Checks for:
- Python version (3.7+)
- yt-dlp installation
- rich library
- requests library

## Troubleshooting

### yt-dlp not found

```bash
pip install yt-dlp
```

### Rich UI not displaying

```bash
pip install rich
```

### Download fails with API method

- Try `yt-dlp` method instead
- Ensure URL is valid and public
- Check internet connection

### Permission denied on download folder

Change download directory in Settings to a writable path:

```bash
# Example
/sdcard/Download/TikTok_Videos        # Android/Termux
~/Downloads/TikTok_Videos              # Linux/Mac
C:\Users\Name\Downloads\TikTok_Videos  # Windows
```

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | Supported | Full features |
| macOS | Supported | Full features |
| Windows | Supported | Full features |
| Android/Termux | Supported | Use `/sdcard` for storage |

## License

MIT License

## Disclaimer

This tool is for educational purposes only. Respect content creators' rights and TikTok's Terms of Service. Do not use for unauthorized redistribution of content.
