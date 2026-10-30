#!/data/data/com.termux/files/usr/bin/env python3
"""
Android Screenshot Compressor & Archiver
Lossy WebP batch compressor designed for Termux on Android.
"""

import argparse
import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image


def human_size(num_bytes: int) -> str:
    """Format bytes into human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def main():
    parser = argparse.ArgumentParser(
        description="Batch compress Android screenshots into WebP for efficient archiving."
    )
    parser.add_argument(
        "--source",
        "-s",
        type=Path,
        default=Path.home() / "storage/pictures/Screenshots",
        help="Source directory containing uncompressed screenshots (default: ~/storage/pictures/Screenshots)",
    )
    parser.add_argument(
        "--dest",
        "-d",
        type=Path,
        default=Path.home() / "storage/pictures/SmolScreenShots",
        help="Destination directory for compressed files (default: ~/storage/pictures/SmolScreenShots)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=50.0,
        help="Scale percentage to resize image dimensions (default: 50.0)",
    )
    parser.add_argument(
        "--quality",
        "-q",
        type=int,
        default=45,
        help="Compression quality from 1 to 100 (default: 45)",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="webp",
        help="Target image format extension (default: webp)",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path.home() / "storage/pictures/compressed_screenshots.log",
        help="Log file path (default: ~/storage/pictures/compressed_screenshots.log)",
    )

    args = parser.parse_args()

    source_dir: Path = args.source.expanduser().resolve()
    dest_dir: Path = args.dest.expanduser().resolve()
    log_file: Path = args.log.expanduser().resolve()
    scale: float = args.scale
    quality: int = args.quality
    fmt: str = args.format.lstrip(".").lower()

    dest_dir.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    start_iso = datetime.datetime.now().astimezone().isoformat()
    with log_file.open("a", encoding="utf-8") as log:
        log.write(f"\n=== Compression Job Started: {start_iso} ===\n")
        log.write(f"Source: {source_dir}\n")
        log.write(f"Destination: {dest_dir}\n")
        log.write(f"Scale: {scale}% | Quality: {quality} | Format: {fmt}\n")

    # Fast in-memory lookup set of existing base filenames
    existing_stems = set()
    if dest_dir.exists():
        for entry in os.scandir(dest_dir):
            if entry.is_file():
                entry_path = Path(entry.path)
                if entry_path.suffix.lstrip(".").lower() == fmt:
                    existing_stems.add(entry_path.stem)

    # Reverse-chronological traversal (newest first by mtime)
    source_files = []
    if source_dir.exists():
        for entry in os.scandir(source_dir):
            if entry.is_file() and entry.name.lower().endswith(".png"):
                source_files.append(Path(entry.path))

    # Sort descending by modification time
    source_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    total_source = len(source_files)

    success_count = 0
    skipped_count = 0
    failed_count = 0

    if total_source == 0:
        print(f"No PNG screenshots found in {source_dir}.")
    else:
        for idx, src_path in enumerate(source_files, start=1):
            stem = src_path.stem

            # O(1) in-memory skip check
            if stem in existing_stems:
                skipped_count += 1
                continue

            dest_path = dest_dir / f"{stem}.{fmt}"
            timestamp = datetime.datetime.now().astimezone().isoformat()

            print(f"[{timestamp}] [ATTEMPT] ({idx}/{total_source}) {src_path.name} -> {dest_path.name}")
            with log_file.open("a", encoding="utf-8") as log:
                log.write(f"[{timestamp}] [ATTEMPT] Input: \"{src_path}\" -> Output: \"{dest_path}\"\n")

            try:
                # Open image and preserve ICC color profile
                with Image.open(src_path) as img:
                    icc_profile = img.info.get("icc_profile")

                    # Handle color modes
                    if img.mode in ("P", "1"):
                        img = img.convert("RGBA" if "transparency" in img.info else "RGB")

                    # High-quality Lanczos downscaling
                    if scale != 100.0:
                        new_w = max(1, int(img.width * (scale / 100.0)))
                        new_h = max(1, int(img.height * (scale / 100.0)))
                        processed_img = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)
                    else:
                        processed_img = img

                    # Save parameters
                    save_kwargs = {
                        "format": "WEBP" if fmt == "webp" else fmt.upper(),
                        "quality": quality,
                        "method": 6,  # Max compression effort for WebP
                    }
                    if icc_profile:
                        save_kwargs["icc_profile"] = icc_profile

                    processed_img.save(dest_path, **save_kwargs)

                # Replicate touch -r: copy source access and modification times
                st = src_path.stat()
                os.utime(dest_path, (st.st_atime, st.st_mtime))

                # Update in-memory set
                existing_stems.add(stem)
                success_count += 1

                status_time = datetime.datetime.now().astimezone().isoformat()
                print(f"[{status_time}] [SUCCESS] {src_path.name}")
                with log_file.open("a", encoding="utf-8") as log:
                    log.write(f"[{status_time}] [SUCCESS] Successfully compressed \"{src_path}\" to \"{dest_path}\"\n")

            except Exception as e:
                failed_count += 1
                status_time = datetime.datetime.now().astimezone().isoformat()
                print(f"[{status_time}] [FAILED] {src_path.name}: {e}", file=sys.stderr)
                with log_file.open("a", encoding="utf-8") as log:
                    log.write(f"[{status_time}] [FAILED] Error compressing \"{src_path}\": {e}\n")

    # Trigger Android MediaStore scan if new images were created
    if success_count > 0:
        media_scan_bin = shutil.which("termux-media-scan")
        if media_scan_bin:
            print(f"Notifying Android MediaStore of {success_count} new screenshot(s)...")
            try:
                subprocess.run([media_scan_bin, "-r", str(dest_dir)], check=False)
            except Exception as e:
                print(f"Media scan warning: {e}", file=sys.stderr)

    # Fast in-memory directory size calculation
    total_bytes = 0
    total_dest_files = 0
    if dest_dir.exists():
        for entry in os.scandir(dest_dir):
            if entry.is_file():
                total_dest_files += 1
                try:
                    total_bytes += entry.stat().st_size
                except OSError:
                    pass

    end_iso = datetime.datetime.now().astimezone().isoformat()
    summary = f"""
========================================
===   COMPRESSION JOB SUMMARY        ===
========================================
Job Completed:         {end_iso}
Source Directory:      {source_dir}
Destination Directory: {dest_dir}
Parameters:            Scale: {scale}% | Quality: {quality} | Format: {fmt}

Metrics:
  - Total Source PNGs Found:         {total_source}
  - Newly Converted ([SUCCESS]):     {success_count}
  - Skipped Files ([SKIPPED]):       {skipped_count}
  - Failed Conversions ([FAILED]):   {failed_count}

Archive Status:
  - Total Files in Destination:      {total_dest_files}
  - Total Archive Directory Size:    {human_size(total_bytes)}
========================================
"""
    print(summary)
    with log_file.open("a", encoding="utf-8") as log:
        log.write(summary + "\n")


if __name__ == "__main__":
    main()
