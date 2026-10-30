# Screenshot Compressor for Android (Termux)

A lightweight, high-performance Python utility designed to batch-compress Android screenshots into modern, highly-optimized WebP images right on your device.

---

## 🌟 What This Project Does

Mobile screenshots on high-DPI devices like the Google Pixel 9 Pro are captured as uncompressed PNGs, frequently taking **3 MB to 8 MB+** per image. 

This tool:
* Downscales resolution (default 50%) and converts screenshots into WebP at quality 45.
* Drops average screenshot file sizes from **~5 MB down to ~40 KB – 80 KB** (>95% size reduction).
* Preserves sharp, legible text and UI contrast for record-keeping and archiving.
* Preserves ICC color profile metadata and exact original timestamps (`os.utime`).
* Dramatically reduces Google Photos cloud storage usage and local phone storage.

---

## 🚀 Why It Was Built

1. **Overcoming Android Background Restrictions:** Android aggressively terminates background apps and restricts battery usage. Running directly in Termux gives full user control.
2. **Eliminating Subprocess Bottlenecks:** Unlike traditional Bash scripts that spawn hundreds of individual subprocesses (`ls`, `basename`, `date`, `touch`, `du`), this Python implementation executes completely in-memory using `os.scandir` and `Pillow`'s native C bindings.
3. **Instant $O(1)$ Duplicate Skipping:** Uses in-memory hashing to instantly skip screenshots that have already been converted without disk thrashing.
4. **Chronological Sorting:** Processes files newest-first so recent captures are archived immediately.
5. **Exact Timestamp Preservation:** Replicates `touch -r` so Google Photos and gallery apps display images in their true chronological order.

---

## 🛠 Tech Stack

* **Language:** Python 3
* **Image Processing:** [Pillow](https://python-pillow.org/) (PIL) using `LANCZOS` high-quality anti-aliasing resampling and `libwebp` encoder.
* **Environment:** [Termux](https://termux.dev/) on Android.

---

## 📦 Installation & Prerequisites

Inside Termux, install Python and Pillow:

```bash
pkg update && pkg upgrade -y
pkg install -y python python-pillow git termux-api
```

Ensure storage access is granted to Termux:

```bash
termux-setup-storage
```

---

## ⚙️ Usage

Make the script executable:

```bash
chmod +x ~/code/screenshot-compressor/compress.py
```

### Configuration

Defaults can be customized in `config.json` (git-ignored for personal privacy). On first run, `compress.py` automatically initializes `config.json` from `config.example.json`:

```json
{
  "source_directory": "~/storage/pictures/Screenshots",
  "destination_directory": "~/storage/pictures/CompressedScreenshots",
  "scale_percent": 50.0,
  "quality": 45,
  "format": "webp"
}
```

Any CLI flag passed at runtime (`--dest`, `--scale`, etc.) will override the config file.

### Basic Run (Default Settings)
```bash
python ~/code/screenshot-compressor/compress.py
```

* **Default Source:** `~/storage/pictures/Screenshots`
* **Default Destination:** `~/storage/pictures/SmolScreenShots`
* **Default Scale:** `50%`
* **Default Quality:** `45`
* **Default Format:** `webp`

### Custom Options
```bash
# Custom scale, quality, and output format
python ~/code/screenshot-compressor/compress.py --scale 40 --quality 50 --format webp

# Specify custom source and destination folders
python ~/code/screenshot-compressor/compress.py \
  --source ~/storage/pictures/Screenshots \
  --dest ~/storage/pictures/ArchivedScreenshots \
  --quality 40
```

---

## 📱 Android One-Tap Shortcut with Termux:Widget

You can trigger batch compression with a single tap from your Android Home Screen using the **Termux:Widget** add-on:

1. Install **Termux:Widget** (via F-Droid or GitHub Releases).
2. Create the widget shortcuts directory in Termux:
   ```bash
   mkdir -p ~/.shortcuts
   ```
3. Create a launcher script:
   ```bash
   cat << 'EOF' > ~/.shortcuts/CompressScreenshots.sh
   #!/data/data/com.termux/files/usr/bin/bash
   python $HOME/code/screenshot-compressor/compress.py
   read -p "Press Enter to close..."
   EOF
   chmod +x ~/.shortcuts/CompressScreenshots.sh
   ```
4. Long-press your Android home screen, select **Widgets**, find **Termux:Widget**, and drag `CompressScreenshots.sh` to your home screen!

---

## 📄 License
MIT License. Feel free to modify and adapt for your personal archiving workflow.
