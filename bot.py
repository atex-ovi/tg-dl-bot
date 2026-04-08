#!/usr/bin/env python3
import os
import yt_dlp
import asyncio
from concurrent.futures import ThreadPoolExecutor
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.error import TimedOut

TOKEN = os.getenv("BOT_TOKEN")
# TOKEN = "your_telegram_bot_token_here"  # Uncomment for local testing

if not TOKEN:
    print("❌ BOT_TOKEN not set!")
    print("   Local: uncomment hardcode line above")
    print("   Production: export BOT_TOKEN='your_token'")
    exit(1)

DOWNLOAD_DIR = ".downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

user_platform = {}
executor = ThreadPoolExecutor(max_workers=4)

def detect_platform_from_url(url):
    url_lower = url.lower()
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube'
    elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
        return 'Facebook'
    elif 'instagram.com' in url_lower or 'instagr.am' in url_lower:
        return 'Instagram'
    elif 'tiktok.com' in url_lower or 'vt.tiktok.com' in url_lower:
        return 'TikTok'
    return None

def download_media_sync(url, format_type, quality):
    try:
        platform = detect_platform_from_url(url)
        
        if format_type == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
            }
        else:
            if platform in ['Facebook', 'Instagram', 'TikTok']:
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
                    'quiet': True,
                    'no_warnings': True,
                }
            else:
                if quality == 'best' or quality is None:
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
                        'quiet': True,
                        'no_warnings': True,
                        'merge_output_format': 'mp4',
                    }
                else:
                    ydl_opts = {
                        'format': f'best[height<={quality}]',
                        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
                        'quiet': True,
                        'no_warnings': True,
                        'merge_output_format': 'mp4',
                    }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            filename = None
            for ext in ['.mp4', '.webm', '.mkv', '.mp3', '.m4a']:
                test_path = f"{DOWNLOAD_DIR}/{info['id']}{ext}"
                if os.path.exists(test_path):
                    filename = test_path
                    break
            
            if not filename:
                for f in os.listdir(DOWNLOAD_DIR):
                    if info['id'] in f:
                        filename = os.path.join(DOWNLOAD_DIR, f)
                        break
            
            return filename, info['title'], platform
                
    except Exception as e:
        print(f"Download error: {e}")
        return None, None, None

async def send_file_with_retry(bot, chat_id, file, caption, file_type, title=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            if file_type == 'video':
                return await bot.send_video(
                    chat_id=chat_id,
                    video=file,
                    caption=caption,
                    read_timeout=120,
                    write_timeout=120,
                    connect_timeout=120,
                    pool_timeout=120
                )
            else:
                return await bot.send_audio(
                    chat_id=chat_id,
                    audio=file,
                    title=title[:100] if title else "Audio",
                    caption=caption,
                    read_timeout=120,
                    write_timeout=120,
                    connect_timeout=120,
                    pool_timeout=120
                )
        except TimedOut:
            if attempt < max_retries - 1:
                print(f"Timeout, retry {attempt + 2}/{max_retries}...")
                await asyncio.sleep(5)
                file.seek(0)
                continue
            else:
                raise
        except Exception as e:
            raise e

async def process_download_and_send(bot, chat_id, message_id, url, format_type, quality):
    status_msg = None
    try:
        status_msg = await bot.send_message(
            chat_id=chat_id,
            text="📥 *Downloading...*",
            parse_mode='Markdown'
        )
        
        loop = asyncio.get_event_loop()
        filename, title, platform = await loop.run_in_executor(
            executor, 
            download_media_sync, 
            url, format_type, quality
        )
        
        if not filename or not os.path.exists(filename):
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text="❌ *Download failed!* Please try again.",
                parse_mode='Markdown'
            )
            return
        
        file_size = os.path.getsize(filename) / (1024 * 1024)
        
        if file_size > 50:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text=f"⚠️ *File too large!* ({file_size:.1f}MB)\nTelegram limit: 50MB",
                parse_mode='Markdown'
            )
            os.remove(filename)
            return
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg.message_id,
            text="📤 *Bot is preparing your file...*",
            parse_mode='Markdown'
        )
        
        with open(filename, 'rb') as f:
            if filename.endswith('.mp3') or format_type == 'audio':
                await send_file_with_retry(
                    bot, chat_id, f,
                    caption=f"🎵 {title[:50]}\n📱 Platform: {platform}",
                    file_type='audio',
                    title=title
                )
            else:
                await send_file_with_retry(
                    bot, chat_id, f,
                    caption=f"🎬 {title[:50]}\n📱 Platform: {platform}",
                    file_type='video'
                )
        
        # KIRIM NOTIFIKASI DI BAWAH (PESAN TERPISAH)
        format_name = "MP3" if (filename.endswith('.mp3') or format_type == 'audio') else "MP4"
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        
        await bot.send_message(
            chat_id=chat_id,
            text=f"✅ *Download complete!*\n\n📹 *{title[:50]}*\n📦 Size: {file_size:.2f} MB\n🎵 Format: {format_name}\n📱 Platform: {platform}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        try:
            await bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        except:
            pass
        
        # HAPUS FILE
        await asyncio.sleep(5)
        if os.path.exists(filename):
            os.remove(filename)
        
    except Exception as e:
        print(f"Process error: {e}")
        error_text = f"❌ *Error:* {str(e)[:100]}"
        if status_msg:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text=error_text,
                parse_mode='Markdown'
            )
        else:
            await bot.send_message(chat_id=chat_id, text=error_text, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_platform:
        del user_platform[user_id]
    
    keyboard = [
        [InlineKeyboardButton("YouTube", callback_data="platform_youtube")],
        [InlineKeyboardButton("Facebook", callback_data="platform_facebook")],
        [InlineKeyboardButton("Instagram", callback_data="platform_instagram")],
        [InlineKeyboardButton("TikTok", callback_data="platform_tiktok")],
    ]
    await update.message.reply_text(
        "🎬 *Select Platform:*\n\nChoose the platform you want to download from.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def platform_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    platform = query.data.replace('platform_', '')
    user_id = query.from_user.id
    user_platform[user_id] = platform
    
    platform_icons = {
        'youtube': 'YouTube',
        'facebook': 'Facebook',
        'instagram': 'Instagram',
        'tiktok': 'TikTok'
    }
    
    await query.edit_message_text(
        f"✅ Platform: *{platform_icons.get(platform, platform)}*\n\n"
        f"Now send me the video link from {platform_icons.get(platform, platform)}.",
        parse_mode='Markdown'
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id in user_platform:
        del user_platform[user_id]
    
    context.user_data.clear()
    
    keyboard = [
        [InlineKeyboardButton("YouTube", callback_data="platform_youtube")],
        [InlineKeyboardButton("Facebook", callback_data="platform_facebook")],
        [InlineKeyboardButton("Instagram", callback_data="platform_instagram")],
        [InlineKeyboardButton("TikTok", callback_data="platform_tiktok")],
    ]
    
    await query.edit_message_text(
        "🎬 *Select Platform:*\n\nChoose the platform you want to download from.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    url = update.message.text.strip()
    
    if user_id not in user_platform:
        await update.message.reply_text("❌ *Please select platform first!*\n\nType /start to choose platform.", parse_mode='Markdown')
        return
    
    selected_platform = user_platform[user_id]
    detected_platform = detect_platform_from_url(url)
    
    if detected_platform and detected_platform.lower() != selected_platform:
        await update.message.reply_text(
            f"❌ *Platform mismatch!*\n\nYou selected: *{selected_platform.upper()}*\nLink is from: *{detected_platform}*\n\nPlease send the correct link.",
            parse_mode='Markdown'
        )
        return
    
    msg = await update.message.reply_text("🔍 *Analyzing...*", parse_mode='Markdown')
    
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            context.user_data['url'] = url
            context.user_data['title'] = info.get('title', 'Video')
            
            if selected_platform == 'youtube':
                keyboard = [
                    [InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio")],
                    [InlineKeyboardButton("🎬 Video (Best)", callback_data="video_best")],
                    [InlineKeyboardButton("🎬 Video (Select Quality)", callback_data="video_quality")],
                ]
            else:
                keyboard = [
                    [InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio")],
                    [InlineKeyboardButton("🎬 Video (Best)", callback_data="video_best")],
                ]
            
            duration = info.get('duration', '?')
            duration_str = f"{duration // 60}:{duration % 60:02d}" if isinstance(duration, int) else '?'
            
            await msg.edit_text(
                f"📹 *{info['title'][:60]}*\n\n📱 Platform: *{selected_platform.upper()}*\n⏱️ Duration: {duration_str}\n\nSelect format:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)[:100]}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    url = context.user_data.get('url')
    title = context.user_data.get('title', 'Video')
    user_id = query.from_user.id
    selected_platform = user_platform.get(user_id, 'Unknown')
    
    if not url:
        await query.edit_message_text("❌ Session expired. Type /start to begin again.")
        return
    
    await query.edit_message_text(
        f"⏳ *Processing...*\n\n📹 {title[:50]}\n📱 Platform: {selected_platform.upper()}\n\nThis may take a few moments...",
        parse_mode='Markdown'
    )
    
    if choice == 'audio':
        asyncio.create_task(process_download_and_send(
            context.bot, 
            query.message.chat_id, 
            query.message.message_id,
            url, 
            'audio', 
            None
        ))
    elif choice == 'video_best':
        asyncio.create_task(process_download_and_send(
            context.bot, 
            query.message.chat_id, 
            query.message.message_id,
            url, 
            'video', 
            'best'
        ))
    elif choice == 'video_quality':
        keyboard = [
            [InlineKeyboardButton("360p", callback_data="quality_360"), InlineKeyboardButton("480p", callback_data="quality_480")],
            [InlineKeyboardButton("720p", callback_data="quality_720"), InlineKeyboardButton("1080p", callback_data="quality_1080")],
        ]
        await query.edit_message_text(
            f"🎬 *Select video quality:*\n\n📹 {title[:50]}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def quality_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    quality = query.data.replace('quality_', '')
    url = context.user_data.get('url')
    title = context.user_data.get('title', 'Video')
    user_id = query.from_user.id
    selected_platform = user_platform.get(user_id, 'Unknown')
    
    if not url:
        await query.edit_message_text("❌ Session expired. Type /start to begin again.")
        return
    
    await query.edit_message_text(
        f"⏳ *Processing {quality}p video...*\n\n📹 {title[:50]}\n📱 Platform: {selected_platform.upper()}\n\nThis may take a few moments...",
        parse_mode='Markdown'
    )
    
    asyncio.create_task(process_download_and_send(
        context.bot, 
        query.message.chat_id, 
        query.message.message_id,
        url, 
        'video', 
        quality
    ))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(platform_handler, pattern="^platform_"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(audio|video_best|video_quality)$"))
    app.add_handler(CallbackQueryHandler(quality_handler, pattern="^quality_"))
    
    print("🚀 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

    
