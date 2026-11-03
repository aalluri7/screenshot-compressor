# Screenshot Compressor for Android (Termux)

A lightweight, high-performance Python utility designed to batch-compress Android screenshots into modern, highly-optimized WebP images right on your device.

---

## 💭 The Origin: Why I Built This

I’m not a writer, and I’ve never been good at typing or keeping written journals. Instead, I record my life visually—photographing what I eat, keeping track of things I need to remember, and taking screenshots of articles, ideas, or pieces of context I feed into AI models. If I ever need to figure something out about my past, I web my way back into it through the timestamps of these images. 

For camera photos, I used Open Camera with aggressive compression to capture sub-100 KB images that still preserved all the text and information I cared about. But I ran into a wall with phone screenshots:
* They are captured as full uncompressed PNGs (**3 MB to 8 MB+ each**).
* Whenever I switched phones, old screenshots weren't easily carried over.
* Backing up raw PNGs flooded and quickly exhausted my Google Photos cloud storage quota.
* Existing Play Store compression apps were full of ads, background battery-draining services, or subscriptions.

I knew that if Open Camera could produce readable, sub-100 KB records of physical documents, digital screenshots should be able to do the same. 

So I built this utility directly inside Termux on my phone using voice dictation:
* It mirrors screenshots into a compressed folder (`SmolScreenShots`), taking them from **~5 MB down to ~40 KB – 80 KB** (>95% size reduction).
* It preserves original timestamps (`os.utime`) so Google Photos retains the exact chronological history of my records.
* It notifies Android's MediaStore (`termux-media-scan`) so I can set just the compressed folder to auto-backup to Google Photos without the original raw PNGs eating up cloud storage.

---

## 🚀 Why It Was Built (Technical Architecture)

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

## 📦 Installation & Setup

You can set up all dependencies automatically using the included setup script:

```bash
cd ~/code/screenshot-compressor
chmod +x setup.sh
./setup.sh
```

*(The setup script detects whether you are on Termux/Android or standard Linux/macOS and installs the appropriate dependencies automatically).*

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
* **Default Destination:** Configured in `config.json` (defaults to `CompressedScreenshots`)
* **Default Scale:** `50%`
* **Default Quality:** `45`
* **Default Format:** `webp`

> [!TIP]
> **Android MediaStore & Directory Naming Note:**
> Android's media scanner and Google Photos can be finicky about custom folder names under `~/storage/pictures/`:
> * **Avoid spaces** in folder names (e.g. use `SmolScreenShots` or `CompressedScreenshots`, not `compressed screenshots`). Folders with spaces often cause Google Photos indexing delays or fail to group cleanly in the *On this device* gallery view.
> * **Use CamelCase or capitalized names** (e.g., `SmolScreenShots`) so Android recognizes it as a distinct media collection rather than an app cache or hidden directory.
> * Always make sure `termux-api` is installed so `termux-media-scan` automatically notifies Google Photos the moment new files are written.

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
