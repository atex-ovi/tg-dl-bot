<p align="center">
  <img src="logo.png" alt="tg-dl-bot" width="400"/>
</p>

**Telegram bot for downloading videos/audio from YouTube, Facebook, Instagram, and TikTok.**

📺 **Video Tutorial:** [click here](https://www.facebook.com/share/v/1BJBdz7hgX/)

---

## Features

- **YouTube** - Audio, Video Best, Select Quality (360p-1080p)
- **Facebook** - Audio, Video Best
- **Instagram** - Audio, Video Best
- **TikTok** - Audio, Video Best

---

## Requirements

- Python >= 3.10
- FFmpeg
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

---

## Getting Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Choose a name for your bot (example: `My Downloader Bot`)
4. Choose a username (must end with `bot`, example: `mydownloader_bot`)
5. Copy the token you receive. It looks like:
```

1234567890:ABCdefGHIjklmNOPqrStuVWXyz

```

> [!TIP]
> Keep your token secret! Anyone with this token can control your bot.

---

## Installation

### 1. Clone repository

```bash
git clone https://github.com/atex-ovi/tg-dl-bot.git
cd tg-dl-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg (Termux)

```bash
pkg install ffmpeg
```

### 4. Setup bot token (choose one)

Option A: Local Testing (Hardcode) - Edit bot.py:

```python
TOKEN = "your_telegram_bot_token_here"  # Uncomment this line
```

Option B: Production (Environment Variable):

```bash
export BOT_TOKEN="your_telegram_bot_token"
```

### 5. Run bot

```bash
python bot.py
```

> [!IMPORTANT]
> **Never commit hardcoded token to GitHub! Use environment variable for production.**

---

## Usage

1. Start bot with /start
2. Select platform (YouTube/Facebook/Instagram/TikTok)
3. Send video link
4. Choose format (Audio/Video)
5. For YouTube, can select video quality (360p-1080p)
6. File will be sent automatically
7. Click "Back to Menu" to download again

## File Structure

```text
tg-dl-bot/
├── bot.py
├── requirements.txt
├── .gitignore
└── README.md
```

> [!NOTE]
> - Maximum file size: 50MB (Telegram limit)
> - Large files may take a few minutes to upload
> - Uses yt-dlp for video downloading
> - Requires Deno for YouTube extraction (install with: pkg install deno)

## License

[MIT](LICENSE.md)
