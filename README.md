<p align="center">
  <img src="https://raw.githubusercontent.com/atex-ovi/tg-dl-bot/main/.1775579507045.png" alt="tg-dl-bot" width="400"/>
</p>

Telegram bot for downloading videos/audio from YouTube, Facebook, Instagram, and TikTok.

## Features

- YouTube (Audio, Video Best, Select Quality)
- Facebook (Audio, Video Best)
- Instagram (Audio, Video Best)
- TikTok (Audio, Video Best)

## Requirements

- Python >= 3.10
- FFmpeg
- Telegram Bot Token (from @BotFather)

## Installation

1. Clone repository

```bash
git clone https://github.com/atex-ovi/tg-dl-bot.git
cd tg-dl-bot
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Install FFmpeg (Termux)

```bash
pkg install ffmpeg
```

4. Set bot token

```bash
export BOT_TOKEN="your_telegram_bot_token"
```

5. Run bot

```bash
python bot.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| BOT_TOKEN | Telegram bot token from @BotFather |

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

## Notes

- Maximum file size: 50MB (Telegram limit)
- Large files may take a few minutes to upload
- Uses yt-dlp for video downloading
- Requires Deno for YouTube extraction (install with: pkg install deno)

## License

[MIT](LICENSE.md)
