#!/usr/bin/env python3
"""
TikTok Video Downloader v3.0
Rich UI Edition | Clean Minimalist | box.ROUNDED
Features: Single Download, Batch, No Watermark, Video Info, Settings
"""

import os
import sys
import json
import re
import time
import subprocess
import configparser
import requests
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Rich UI
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    from rich.align import Align
    from rich.text import Text
    from rich.prompt import Prompt, Confirm, IntPrompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[INFO] Install rich untuk UI terbaik: pip install rich")

# ============================================================
# CONFIG & SETTINGS
# ============================================================
CONFIG_DIR = Path.home() / ".config" / "tiktok_downloader"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "settings.ini"

DEFAULT_SETTINGS = {
    "General": {
        "download_dir": str(Path.home() / "Downloads" / "TikTok_Videos"),
        "default_method": "ytdlp",
        "max_workers": "3",
        "auto_open_folder": "false",
        "show_thumbnails": "true",
    },
    "Download": {
        "quality": "best",
        "no_watermark": "false",
        "save_metadata": "true",
    },
    "UI": {
        "theme": "default",
        "show_progress_bar": "true",
        "clear_screen": "true",
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.tiktok.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

console = Console() if RICH_AVAILABLE else None

# ============================================================
# SETTINGS MANAGER
# ============================================================

class SettingsManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            self.config.read(CONFIG_FILE)
        else:
            self.config.read_dict(DEFAULT_SETTINGS)
            self.save()

    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)

    def get(self, section, key, fallback=None):
        try:
            return self.config.get(section, key)
        except:
            return fallback or DEFAULT_SETTINGS.get(section, {}).get(key, "")

    def get_bool(self, section, key, fallback=False):
        val = self.get(section, key, str(fallback).lower())
        return val.lower() in ('true', '1', 'yes', 'on')

    def get_int(self, section, key, fallback=0):
        try:
            return int(self.get(section, key, str(fallback)))
        except:
            return fallback

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save()

    def reset(self):
        self.config.read_dict(DEFAULT_SETTINGS)
        self.save()

    def get_download_dir(self):
        path = Path(self.get("General", "download_dir", str(Path.home() / "Downloads" / "TikTok_Videos")))
        path.mkdir(parents=True, exist_ok=True)
        return path

settings = SettingsManager()

# ============================================================
# UTILITIES
# ============================================================

def clean_filename(text, max_length=50):
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '_', text).strip('_')
    return text[:max_length] if text else "tiktok_video"

def extract_video_id(url):
    patterns = [
        r'tiktok\.com/.*/video/(\d+)',
        r'tiktok\.com/t/(\w+)',
        r'vm\.tiktok\.com/(\w+)',
        r'tiktok\.com/(@[^/]+)/video/(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1) if len(match.groups()) == 1 else match.group(2)
    return None

def get_timestamp():
    return time.strftime("%Y%m%d_%H%M%S")

def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_names[i]}"

def format_duration(seconds):
    if not seconds:
        return "N/A"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

# ============================================================
# RICH UI - CLEAN MINIMALIST
# ============================================================

def print_banner():
    if RICH_AVAILABLE and console:
        banner_text = "[bold cyan]TIKTOK VIDEO DOWNLOADER[/bold cyan]\n[dim]Rich Table Edition v3.0[/dim]"
        console.print(Panel(
            Align.center(banner_text),
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        ))
    else:
        print("\n  TIKTOK VIDEO DOWNLOADER v3.0\n")

def print_menu_table():
    if RICH_AVAILABLE and console:
        table = Table(
            title="[bold green]MAIN MENU[/bold green]",
            box=box.ROUNDED,
            border_style="green",
            show_header=True,
            header_style="bold bright_green",
            title_justify="center",
            padding=(0, 1)
        )
        table.add_column("No", style="bold yellow", justify="center", width=4)
        table.add_column("Option", style="bold cyan", min_width=25)
        table.add_column("Description", style="dim", min_width=30)
        table.add_column("Icon", justify="center", width=4)

        menu_items = [
            ("1", "Download Video", "Download single video URL", "VID"),
            ("2", "Batch Download", "Download from file list", "BAT"),
            ("3", "Video Info", "Show metadata only", "INF"),
            ("4", "No Watermark", "Download without watermark", "NOWM"),
            ("5", "Settings", "Configure preferences", "SET"),
            ("6", "System Check", "Check dependencies", "CHK"),
            ("0", "Exit", "Quit application", "EXT"),
        ]

        for num, option, desc, icon in menu_items:
            table.add_row(f"[{num}]", f"[bold]{option}[/bold]", desc, icon)

        console.print(table)
        return Prompt.ask(
            "\n[bold yellow]Select option[/bold yellow]",
            choices=["0", "1", "2", "3", "4", "5", "6"],
            default="1"
        )
    else:
        print("\n  MENU:")
        print("  1. Download Video     5. Settings")
        print("  2. Batch Download     6. System Check")
        print("  3. Video Info         0. Exit")
        print("  4. No Watermark")
        return input("Select (0-6): ").strip() or "1"

def print_quality_table():
    if RICH_AVAILABLE and console:
        table = Table(
            title="[bold magenta]SELECT QUALITY[/bold magenta]",
            box=box.ROUNDED,
            border_style="magenta",
            show_header=True,
            header_style="bold bright_magenta",
            title_justify="center"
        )
        table.add_column("No", style="bold yellow", justify="center", width=4)
        table.add_column("Quality", style="bold cyan", min_width=12)
        table.add_column("Description", style="dim", min_width=25)
        table.add_column("Best For", style="green", min_width=15)

        qualities = [
            ("1", "Best", "Highest available quality", "Archive"),
            ("2", "1080p", "Full HD", "High quality"),
            ("3", "720p", "HD", "Balanced"),
            ("4", "480p", "SD", "Fast download"),
            ("5", "360p", "Low", "Slow internet"),
            ("6", "Audio", "Audio only", "Music"),
        ]

        for num, quality, desc, best in qualities:
            table.add_row(num, quality, desc, best)

        console.print(table)
        choice = Prompt.ask(
            "\n[bold yellow]Select quality[/bold yellow]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="1"
        )
        quality_map = {"1": "best", "2": "1080p", "3": "720p", "4": "480p", "5": "360p", "6": "audio"}
        return quality_map[choice]
    else:
        print("\n  QUALITY:")
        print("  1. Best    4. 480p")
        print("  2. 1080p   5. 360p")
        print("  3. 720p    6. Audio")
        choice = input("Select (1-6): ").strip() or "1"
        quality_map = {"1": "best", "2": "1080p", "3": "720p", "4": "480p", "5": "360p", "6": "audio"}
        return quality_map.get(choice, "best")

def print_settings_table():
    if RICH_AVAILABLE and console:
        table = Table(
            title="[bold yellow]SETTINGS[/bold yellow]",
            box=box.ROUNDED,
            border_style="yellow",
            show_header=True,
            header_style="bold bright_yellow",
            title_justify="center"
        )
        table.add_column("No", style="bold cyan", justify="center", width=4)
        table.add_column("Setting", style="bold green", min_width=20)
        table.add_column("Current Value", style="yellow", min_width=25)
        table.add_column("Description", style="dim", min_width=20)

        settings_data = [
            ("1", "Output Directory", settings.get("General", "download_dir"), "Download location"),
            ("2", "Default Method", settings.get("General", "default_method"), "ytdlp/api/direct"),
            ("3", "Max Workers", settings.get("General", "max_workers"), "Concurrent downloads"),
            ("4", "Auto Open Folder", settings.get("General", "auto_open_folder"), "Open after download"),
            ("5", "Show Thumbnails", settings.get("General", "show_thumbnails"), "Display thumbnails"),
            ("6", "Quality", settings.get("Download", "quality"), "Video quality"),
            ("7", "Save Metadata", settings.get("Download", "save_metadata"), "Save info file"),
            ("8", "Clear Screen", settings.get("UI", "clear_screen"), "Auto clear on menu"),
            ("9", "Reset to Default", "-", "Restore defaults"),
            ("0", "Back to Menu", "-", "Return to main menu"),
        ]

        for num, setting, value, desc in settings_data:
            table.add_row(num, setting, str(value), desc)

        console.print(table)
        return Prompt.ask(
            "\n[bold yellow]Select setting to change[/bold yellow]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            default="0"
        )
    else:
        print("\n  SETTINGS:")
        print(f"  1. Download Dir : {settings.get('General', 'download_dir')}")
        print(f"  2. Default Method: {settings.get('General', 'default_method')}")
        print(f"  3. Max Workers  : {settings.get('General', 'max_workers')}")
        print(f"  4. Auto Open    : {settings.get('General', 'auto_open_folder')}")
        print(f"  5. Thumbnails   : {settings.get('General', 'show_thumbnails')}")
        print(f"  6. Quality      : {settings.get('Download', 'quality')}")
        print(f"  7. Save Metadata: {settings.get('Download', 'save_metadata')}")
        print(f"  8. Clear Screen : {settings.get('UI', 'clear_screen')}")
        print("  9. Reset Default")
        print("  0. Back")
        return input("Select (0-9): ").strip() or "0"

def print_method_table():
    if RICH_AVAILABLE and console:
        table = Table(
            title="[bold magenta]SELECT METHOD[/bold magenta]",
            box=box.ROUNDED,
            border_style="magenta",
            show_header=True,
            header_style="bold bright_magenta",
            title_justify="center"
        )
        table.add_column("No", style="bold yellow", justify="center", width=4)
        table.add_column("Method", style="bold cyan", min_width=12)
        table.add_column("Description", style="dim", min_width=25)
        table.add_column("Best For", style="green", min_width=15)

        methods = [
            ("1", "yt-dlp", "Best quality, recommended", "All videos"),
            ("2", "API No WM", "Without watermark", "Clean videos"),
            ("3", "Direct", "Fallback method", "Quick download"),
        ]

        for num, method, desc, best in methods:
            table.add_row(num, method, desc, best)

        console.print(table)
        choice = Prompt.ask(
            "\n[bold yellow]Select method[/bold yellow]",
            choices=["1", "2", "3"],
            default="1"
        )
        method_map = {"1": "ytdlp", "2": "api", "3": "direct"}
        return method_map[choice]
    else:
        print("\n  METHOD:")
        print("  1. yt-dlp     - Best quality")
        print("  2. API No WM  - No watermark")
        print("  3. Direct     - Fallback")
        choice = input("Select (1-3): ").strip() or "1"
        method_map = {"1": "ytdlp", "2": "api", "3": "direct"}
        return method_map.get(choice, "ytdlp")

def print_video_info_table(info):
    if RICH_AVAILABLE and console and info.get("success"):
        info_table = Table(
            title="[bold cyan]VIDEO INFORMATION[/bold cyan]",
            box=box.ROUNDED,
            border_style="cyan",
            show_header=False,
            padding=(0, 1)
        )
        info_table.add_column("Field", style="bold green", min_width=12)
        info_table.add_column("Value", style="white", min_width=40)

        info_table.add_row("Title", info.get("title", "N/A"))
        info_table.add_row("Uploader", info.get("uploader", "N/A"))
        info_table.add_row("Duration", format_duration(info.get("duration")))
        info_table.add_row("Views", f"{info.get('views', 0):,}" if info.get('views') else 'N/A')
        info_table.add_row("Likes", f"{info.get('likes', 0):,}" if info.get('likes') else 'N/A')
        info_table.add_row("Comments", f"{info.get('comments', 0):,}" if info.get('comments') else 'N/A')
        info_table.add_row("Formats", str(info.get('formats', 'N/A')))

        console.print(info_table)
    elif not info.get("success"):
        if RICH_AVAILABLE and console:
            console.print(Panel(
                f"[bold red]Failed to get info: {info.get('error', '')}[/bold red]",
                border_style="red",
                box=box.ROUNDED
            ))
        else:
            print(f"Failed: {info.get('error', '')}")

def print_download_result_table(result):
    if RICH_AVAILABLE and console:
        if result.get("success"):
            table = Table(
                title="[bold green]DOWNLOAD COMPLETE[/bold green]",
                box=box.ROUNDED,
                border_style="green",
                show_header=False,
                padding=(0, 1)
            )
            table.add_column("Field", style="bold cyan", min_width=12)
            table.add_column("Value", style="white", min_width=40)

            table.add_row("File", result.get('file', 'Unknown'))
            table.add_row("Title", result.get('title', 'Unknown'))
            table.add_row("Author", result.get('uploader', result.get('author', 'Unknown')))
            table.add_row("Duration", format_duration(result.get('duration')))
            table.add_row("Size", format_size(result.get('size', 0)))
            table.add_row("Time", time.strftime("%Y-%m-%d %H:%M:%S"))

            console.print(table)
        else:
            table = Table(
                title="[bold red]DOWNLOAD FAILED[/bold red]",
                box=box.ROUNDED,
                border_style="red",
                show_header=False
            )
            table.add_column("Error", style="red")
            table.add_row(result.get('error', 'Unknown error'))
            console.print(table)
    else:
        if result.get("success"):
            print(f"\n  OK: {result.get('file')}")
        else:
            print(f"\n  Failed: {result.get('error', '')}")

def print_batch_result_table(results):
    if RICH_AVAILABLE and console:
        table = Table(
            title="[bold cyan]BATCH DOWNLOAD SUMMARY[/bold cyan]",
            box=box.ROUNDED,
            border_style="cyan",
            show_header=True,
            header_style="bold bright_cyan"
        )
        table.add_column("#", style="dim", width=4, justify="center")
        table.add_column("Status", style="bold", width=8, justify="center")
        table.add_column("Title", style="cyan", min_width=25)
        table.add_column("Size", style="green", width=12)

        for i, result in enumerate(results, 1):
            status = "[green]OK[/green]" if result["success"] else "[red]FAIL[/red]"
            title = result.get('title', result.get('url', 'Unknown'))[:30] + "..." if len(result.get('title', '')) > 30 else result.get('title', 'Unknown')
            table.add_row(str(i), status, title, format_size(result.get('size', 0)))

        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful

        console.print(table)

        summary = Table(box=box.ROUNDED, border_style="green", show_header=False)
        summary.add_column("Metric", style="bold")
        summary.add_column("Value", style="bold")
        summary.add_row("Successful", str(successful))
        summary.add_row("Failed", str(failed))
        summary.add_row("Total", str(len(results)))
        console.print(summary)
    else:
        success = sum(1 for r in results if r["success"])
        print(f"\n  Summary: {success} OK, {len(results)-success} Failed")

def print_system_check_table():
    if RICH_AVAILABLE and console:
        table = Table(
            title="[bold cyan]SYSTEM CHECK[/bold cyan]",
            box=box.ROUNDED,
            border_style="cyan",
            show_header=True,
            header_style="bold bright_cyan"
        )
        table.add_column("Component", style="bold green", min_width=15)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Version/Info", style="yellow", min_width=25)
        table.add_column("Required", style="dim", width=10)

        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        table.add_row("Python", "[green]OK[/green]", py_version, "3.7+")

        try:
            import yt_dlp
            table.add_row("yt-dlp", "[green]OK[/green]", yt_dlp.version.__version__, "Yes")
        except:
            table.add_row("yt-dlp", "[red]FAIL[/red]", "Not installed", "Yes")

        try:
            import rich
            table.add_row("rich", "[green]OK[/green]", rich.__version__, "Yes")
        except:
            table.add_row("rich", "[red]FAIL[/red]", "Not installed", "Yes")

        try:
            import requests
            table.add_row("requests", "[green]OK[/green]", requests.__version__, "Yes")
        except:
            table.add_row("requests", "[red]FAIL[/red]", "Not installed", "Yes")

        console.print(table)
    else:
        print("\n  SYSTEM CHECK:")
        print(f"  Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        try:
            import yt_dlp
            print(f"  yt-dlp: OK")
        except:
            print("  yt-dlp: Not installed")

# ============================================================
# DOWNLOAD METHODS
# ============================================================

def download_with_ytdlp(url, output_path=None, quality="best"):
    try:
        import yt_dlp
    except ImportError:
        return {"success": False, "error": "yt-dlp not installed. Run: pip install yt-dlp"}

    download_dir = settings.get_download_dir()
    if output_path is None:
        video_id = extract_video_id(url) or get_timestamp()
        output_path = download_dir / f"{video_id}.mp4"
    else:
        output_path = Path(output_path)

    ydl_opts = {
        'format': quality,
        'outtmpl': str(output_path),
        'quiet': True,
        'no_warnings': True,
        'headers': HEADERS,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            result = {
                "success": True,
                "file": str(output_path),
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "views": info.get("view_count", 0),
                "likes": info.get("like_count", 0),
                "size": os.path.getsize(output_path) if os.path.exists(output_path) else 0,
            }

            if settings.get_bool("Download", "save_metadata"):
                meta_file = output_path.with_suffix('.json')
                with open(meta_file, 'w') as f:
                    json.dump({k: v for k, v in info.items() if k not in ['formats', 'thumbnails']}, f, indent=2, default=str)

            return result
    except Exception as e:
        return {"success": False, "error": str(e)}

def download_no_watermark(url, output_path=None):
    video_id = extract_video_id(url)
    if not video_id:
        return {"success": False, "error": "Cannot extract video ID from URL"}

    download_dir = settings.get_download_dir()
    if output_path is None:
        output_path = download_dir / f"tiktok_{video_id}_nowm.mp4"
    else:
        output_path = Path(output_path)

    api_url = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_id}"

    try:
        response = requests.get(api_url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if "aweme_list" in data and len(data["aweme_list"]) > 0:
                video_info = data["aweme_list"][0]
                video_url = None

                if "video" in video_info:
                    video_data = video_info["video"]
                    if "play_addr" in video_data and "url_list" in video_data["play_addr"]:
                        video_url = video_data["play_addr"]["url_list"][0]
                    elif "download_addr" in video_data and "url_list" in video_data["download_addr"]:
                        video_url = video_data["download_addr"]["url_list"][0]

                if video_url:
                    video_response = requests.get(video_url, headers=HEADERS, stream=True, timeout=30)
                    if video_response.status_code == 200:
                        downloaded = 0
                        with open(output_path, 'wb') as f:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)

                        return {
                            "success": True,
                            "file": str(output_path),
                            "title": video_info.get("desc", "TikTok Video"),
                            "author": video_info.get("author", {}).get("nickname", "Unknown"),
                            "size": downloaded,
                        }

        return {"success": False, "error": "Failed to download via API"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def download_direct(url, output_path=None):
    download_dir = settings.get_download_dir()
    if output_path is None:
        video_id = extract_video_id(url) or get_timestamp()
        output_path = download_dir / f"tiktok_{video_id}_direct.mp4"
    else:
        output_path = Path(output_path)

    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        response = session.get(url, allow_redirects=True, timeout=15)
        html_content = response.text

        video_patterns = [
            r'"playAddr":"(https://[^"]+)"',
            r'"downloadAddr":"(https://[^"]+)"',
            r'<video[^>]+src="(https://[^"]+)"',
        ]

        video_url = None
        for pattern in video_patterns:
            match = re.search(pattern, html_content)
            if match:
                video_url = match.group(1).replace("\\u0026", "&")
                break

        if video_url:
            video_response = session.get(video_url, stream=True, timeout=30)
            if video_response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                return {
                    "success": True,
                    "file": str(output_path),
                    "size": os.path.getsize(output_path),
                }

        return {"success": False, "error": "Cannot find video link in page"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_video_info(url):
    try:
        import yt_dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "success": True,
                "title": info.get("title", "Unknown"),
                "uploader": info.get("uploader", "Unknown"),
                "duration": info.get("duration", 0),
                "views": info.get("view_count", 0),
                "likes": info.get("like_count", 0),
                "comments": info.get("comment_count", 0),
                "shares": info.get("repost_count", 0),
                "thumbnail": info.get("thumbnail", ""),
                "description": info.get("description", ""),
                "formats": len(info.get("formats", [])),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def batch_download(urls, method="ytdlp", max_workers=None):
    if max_workers is None:
        max_workers = settings.get_int("General", "max_workers", 3)

    results = []

    if RICH_AVAILABLE and console and settings.get_bool("UI", "show_progress_bar", True):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TransferSpeedColumn(),
            console=console,
        ) as progress:

            task = progress.add_task("[cyan]Downloading...", total=len(urls))

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {}
                for url in urls:
                    if method == "ytdlp":
                        future = executor.submit(download_with_ytdlp, url)
                    elif method == "api":
                        future = executor.submit(download_no_watermark, url)
                    else:
                        future = executor.submit(download_direct, url)
                    futures[future] = url

                for future in as_completed(futures):
                    url = futures[future]
                    try:
                        result = future.result()
                        results.append({"url": url, **result})
                    except Exception as e:
                        results.append({"url": url, "success": False, "error": str(e)})
                    progress.advance(task)
    else:
        print(f"Downloading {len(urls)} videos...")
        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] {url}")
            if method == "ytdlp":
                result = download_with_ytdlp(url)
            elif method == "api":
                result = download_no_watermark(url)
            else:
                result = download_direct(url)
            results.append({"url": url, **result})
            status = "OK" if result['success'] else f"Failed: {result.get('error', '')}"
            print(f"    -> {status}")

    return results

# ============================================================
# SETTINGS INTERACTIVE
# ============================================================

def handle_settings():
    while True:
        choice = print_settings_table()

        if choice == "1":
            new_dir = Prompt.ask("Enter new output directory", default=settings.get("General", "download_dir")) if RICH_AVAILABLE else input("Enter new output directory: ").strip()
            if new_dir:
                path = Path(new_dir)
                path.mkdir(parents=True, exist_ok=True)
                settings.set("General", "download_dir", str(path))
                if RICH_AVAILABLE and console:
                    console.print("[green]Output directory updated[/green]")

        elif choice == "2":
            method = print_method_table()
            settings.set("General", "default_method", method)
            if RICH_AVAILABLE and console:
                console.print(f"[green]Default method set to: {method}[/green]")

        elif choice == "3":
            workers = IntPrompt.ask("Enter max workers (1-10)", default=settings.get_int("General", "max_workers", 3)) if RICH_AVAILABLE else input("Enter max workers (1-10): ").strip()
            try:
                w = int(workers)
                if 1 <= w <= 10:
                    settings.set("General", "max_workers", str(w))
                    if RICH_AVAILABLE and console:
                        console.print(f"[green]Max workers set to: {w}[/green]")
            except:
                pass

        elif choice == "4":
            current = settings.get_bool("General", "auto_open_folder")
            new_val = not current
            settings.set("General", "auto_open_folder", str(new_val).lower())
            if RICH_AVAILABLE and console:
                console.print(f"[green]Auto open folder: {'ON' if new_val else 'OFF'}[/green]")

        elif choice == "5":
            current = settings.get_bool("General", "show_thumbnails")
            new_val = not current
            settings.set("General", "show_thumbnails", str(new_val).lower())
            if RICH_AVAILABLE and console:
                console.print(f"[green]Show thumbnails: {'ON' if new_val else 'OFF'}[/green]")

        elif choice == "6":
            quality = print_quality_table()
            settings.set("Download", "quality", quality)
            if RICH_AVAILABLE and console:
                console.print(f"[green]Quality set to: {quality}[/green]")

        elif choice == "7":
            current = settings.get_bool("Download", "save_metadata")
            new_val = not current
            settings.set("Download", "save_metadata", str(new_val).lower())
            if RICH_AVAILABLE and console:
                console.print(f"[green]Save metadata: {'ON' if new_val else 'OFF'}[/green]")

        elif choice == "8":
            current = settings.get_bool("UI", "clear_screen")
            new_val = not current
            settings.set("UI", "clear_screen", str(new_val).lower())
            if RICH_AVAILABLE and console:
                console.print(f"[green]Clear screen: {'ON' if new_val else 'OFF'}[/green]")

        elif choice == "9":
            confirm = Confirm.ask("Reset all settings to default?", default=False) if RICH_AVAILABLE else input("Reset all to default? (y/n): ").strip().lower()
            if (RICH_AVAILABLE and confirm) or (not RICH_AVAILABLE and confirm == 'y'):
                settings.reset()
                if RICH_AVAILABLE and console:
                    console.print("[green]Settings reset to default[/green]")

        elif choice == "0":
            break

        else:
            if RICH_AVAILABLE and console:
                console.print("[red]Invalid choice[/red]")

        if RICH_AVAILABLE and console:
            console.input("\n[dim]Press Enter to continue...[/dim]")
        else:
            input("\nPress Enter to continue...")

# ============================================================
# INTERACTIVE HANDLERS
# ============================================================

def handle_single_download():
    url = Prompt.ask("\n[bold cyan]Enter TikTok URL[/bold cyan]") if RICH_AVAILABLE else input("\nEnter TikTok URL: ").strip()
    if not url:
        if RICH_AVAILABLE and console:
            console.print("[yellow]No URL provided[/yellow]")
        return

    with console.status("[bold green]Fetching video info...", spinner="dots") if (RICH_AVAILABLE and console) else None:
        info = get_video_info(url)

    if not info.get("success"):
        if RICH_AVAILABLE and console:
            console.print("[red]Failed to get video info[/red]")
        return

    print_video_info_table(info)

    if RICH_AVAILABLE and console:
        console.print("\n[bold green]Download this video?[/bold green]")
        if not Confirm.ask("Proceed", default=True):
            return
    else:
        proceed = input("Download this video? (y/n): ").strip().lower()
        if proceed != 'y':
            return

    method = print_method_table()

    if RICH_AVAILABLE and console:
        with console.status("[bold green]Downloading...", spinner="dots"):
            if method == "api":
                result = download_no_watermark(url)
            elif method == "direct":
                result = download_direct(url)
            else:
                result = download_with_ytdlp(url)
    else:
        print("Downloading...")
        if method == "api":
            result = download_no_watermark(url)
        elif method == "direct":
            result = download_direct(url)
        else:
            result = download_with_ytdlp(url)

    print_download_result_table(result)

def handle_batch_download():
    if RICH_AVAILABLE and console:
        console.print("\n[bold cyan]Batch Download[/bold cyan]")
        console.print("[dim]Enter URLs (one per line, blank to finish):[/dim]\n")
    else:
        print("\nBatch Download")
        print("Enter URLs (one per line, blank to finish):\n")

    urls = []
    while True:
        url = Prompt.ask("URL") if RICH_AVAILABLE else input("URL: ").strip()
        if not url:
            break
        urls.append(url)

    if not urls:
        if RICH_AVAILABLE and console:
            console.print("[yellow]No URLs entered[/yellow]")
        else:
            print("No URLs entered")
        return

    if RICH_AVAILABLE and console:
        console.print(f"\n[bold cyan]Found {len(urls)} URLs[/bold cyan]")
    else:
        print(f"Found {len(urls)} URLs")

    method = print_method_table()
    results = batch_download(urls, method=method)
    print_batch_result_table(results)

def handle_video_info():
    url = Prompt.ask("\n[bold cyan]Enter TikTok URL[/bold cyan]") if RICH_AVAILABLE else input("\nEnter TikTok URL: ").strip()
    if not url:
        return

    with console.status("[bold green]Fetching info...", spinner="dots") if (RICH_AVAILABLE and console) else None:
        info = get_video_info(url)

    print_video_info_table(info)

def handle_no_watermark():
    url = Prompt.ask("\n[bold cyan]Enter TikTok URL[/bold cyan]") if RICH_AVAILABLE else input("\nEnter TikTok URL: ").strip()
    if not url:
        return

    with console.status("[bold green]Downloading no-watermark...", spinner="dots") if (RICH_AVAILABLE and console) else None:
        result = download_no_watermark(url)

    print_download_result_table(result)

def open_download_folder():
    import platform
    system = platform.system()
    folder = str(settings.get_download_dir())

    try:
        if system == "Windows":
            subprocess.run(["explorer", folder], check=True)
        elif system == "Darwin":
            subprocess.run(["open", folder], check=True)
        else:
            subprocess.run(["xdg-open", folder], check=True)

        if RICH_AVAILABLE and console:
            console.print(Panel(
                f"[bold green]Folder opened:[/bold green]\n[cyan]{folder}[/cyan]",
                border_style="green",
                box=box.ROUNDED
            ))
        else:
            print(f"Folder opened: {folder}")
    except Exception as e:
        if RICH_AVAILABLE and console:
            console.print(Panel(
                f"[bold red]Error:[/bold red] {str(e)}\n[cyan]{folder}[/cyan]",
                border_style="red",
                box=box.ROUNDED
            ))
        else:
            print(f"Error: {e}")
            print(f"Location: {folder}")

# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    if RICH_AVAILABLE and console:
        console.clear()

    while True:
        print_banner()
        choice = print_menu_table()

        if choice == "0":
            if RICH_AVAILABLE and console:
                console.print(Panel(
                    "[bold green]Thank you for using TikTok Video Downloader![/bold green]",
                    border_style="green",
                    box=box.ROUNDED
                ))
            else:
                print("\nThank you! Goodbye.\n")
            break

        elif choice == "1":
            handle_single_download()
        elif choice == "2":
            handle_batch_download()
        elif choice == "3":
            handle_video_info()
        elif choice == "4":
            handle_no_watermark()
        elif choice == "5":
            handle_settings()
        elif choice == "6":
            print_system_check_table()

        if RICH_AVAILABLE and console:
            console.print("\n")
            Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
            if settings.get_bool("UI", "clear_screen", True):
                console.clear()
        else:
            input("\nPress Enter to continue...")
            print("\n" * 2)

# ============================================================
# CLI MODE
# ============================================================

def cli_mode():
    import argparse

    parser = argparse.ArgumentParser(
        description="TikTok Video Downloader v3.0 - Rich Table Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tiktok_downloader.py
  python tiktok_downloader.py -u "URL"
  python tiktok_downloader.py -u "URL1" "URL2" --batch
  python tiktok_downloader.py -u "URL" --info
  python tiktok_downloader.py -u "URL" --no-watermark
        """
    )

    parser.add_argument("-u", "--url", nargs="+", help="TikTok video URL")
    parser.add_argument("-o", "--output", help="Output path")
    parser.add_argument("-m", "--method", choices=["ytdlp", "api", "direct"], 
                        default=None, help="Download method")
    parser.add_argument("--batch", action="store_true", help="Batch mode")
    parser.add_argument("--info", action="store_true", help="Info only")
    parser.add_argument("--no-watermark", action="store_true", help="No watermark")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--max-workers", type=int, default=None, help="Max concurrent")
    parser.add_argument("--settings", action="store_true", help="Open settings")

    args = parser.parse_args()

    if args.settings:
        handle_settings()
        return

    if args.interactive or (not args.url and len(sys.argv) == 1):
        main()
        return

    if not args.url:
        parser.print_help()
        return

    method = args.method or settings.get("General", "default_method", "ytdlp")
    max_workers = args.max_workers or settings.get_int("General", "max_workers", 3)

    if args.info:
        for url in args.url:
            info = get_video_info(url)
            print_video_info_table(info)
        return

    if args.batch or len(args.url) > 1:
        method = "api" if args.no_watermark else method
        results = batch_download(args.url, method=method, max_workers=max_workers)
        print_batch_result_table(results)
    else:
        url = args.url[0]
        if args.no_watermark:
            result = download_no_watermark(url, args.output)
        elif method == "direct":
            result = download_direct(url, args.output)
        else:
            result = download_with_ytdlp(url, args.output)

        print_download_result_table(result)

if __name__ == "__main__":
    cli_mode()
