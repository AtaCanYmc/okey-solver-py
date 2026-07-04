# demo/telegram/bot.py
import os
import sys
import tempfile
import telebot
import numpy as np
import cv2

# Ensure correct module resolution paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from okey_solver import SolverEngine, OkeyMeta, TileColor
from okey_vision import VisionSolverEngine, LocalYoloProvider

# Token is fetched from environment variable E.g. export TELEGRAM_BOT_TOKEN="your-token"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# YOLO model path must be configured. E.g. export YOLO_MODEL_PATH="models/best.pt"
MODEL_PATH = os.environ.get("YOLO_MODEL_PATH", "models/best.pt")

if not BOT_TOKEN:
    print(
        "Warning: TELEGRAM_BOT_TOKEN environment variable is not set. The bot cannot start."
    )

bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

# Keep track of user session meta (Okey Meta info)
user_okey_meta = {}  # E.g. {chat_id: OkeyMeta}


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    welcome_text = (
        "Welcome to the Okey Vision Telegram Bot!\n\n"
        "Instructions:\n"
        "1. Define the Okey tile color and value using `/setokey COLOR VALUE` (e.g. `/setokey RED 7`).\n"
        "2. Send an image/photo of your Okey layout.\n"
        "3. The bot will detect the tiles and solve the best arrangement layout for you!"
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=["setokey"])
def set_okey_meta(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError()

        color_str = parts[1].upper()
        value = int(parts[2])

        color = TileColor(color_str)
        if value < 1 or value > 13:
            raise ValueError()

        user_okey_meta[message.chat.id] = OkeyMeta(color=color, value=value)
        bot.reply_to(
            message, f"Success! Okey tile is set to: **{color.value} {value}**."
        )
    except Exception:
        bot.reply_to(
            message, "Invalid format. E.g: `/setokey RED 7` or `/setokey BLUE 10`."
        )


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    chat_id = message.chat.id

    # 1. Check if model exists
    if not os.path.exists(MODEL_PATH):
        bot.reply_to(
            message,
            f"Error: YOLO model not found at path '{MODEL_PATH}'. Configure YOLO_MODEL_PATH.",
        )
        return

    bot.send_chat_action(chat_id, "typing")
    bot.reply_to(message, "Received your image. Downloading and processing...")

    # 2. Get photo details (select highest resolution available)
    photo_file = message.photo[-1]
    file_info = bot.get_file(photo_file.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # 3. Write temporarily and resolve frame using OpenCV
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(downloaded_file)
        tmp_path = tmp.name

    try:
        # Load vision providers
        okey_meta = user_okey_meta.get(chat_id)

        provider = LocalYoloProvider(model_path=MODEL_PATH)
        engine = VisionSolverEngine(pipeline=provider, okey_meta=okey_meta)

        # Analyze frame
        result = engine.analyze_frame(tmp_path)

        # Format response
        tiles_detected = result["tiles"]
        arrangement = result["arrangement"]

        response = "=== Analysis Complete ===\n"
        if okey_meta:
            response += f"Active Okey Tile: {okey_meta.color.value} {okey_meta.value}\n"
        else:
            response += "Active Okey Tile: Not defined (Defaulting/None)\n"

        response += f"Detected Tiles Count: {len(tiles_detected)}\n"
        response += f"Arrangement Score: {arrangement.totalScore}\n"
        response += f"Melds Count: {len(arrangement.melds)}\n\n"

        for idx, meld in enumerate(arrangement.melds):
            tiles_str = ", ".join([f"{t.color.value}-{t.value}" for t in meld.tiles])
            response += f"  Meld #{idx + 1} ({meld.type.value}): [{tiles_str}] - score: {meld.score}\n"

        if arrangement.remainingTiles:
            leftovers = ", ".join(
                [f"{t.color.value}-{t.value}" for t in arrangement.remainingTiles]
            )
            response += f"\nLeftover Tiles: [{leftovers}]"
        else:
            response += "\nLeftover Tiles: [None]"

        bot.reply_to(message, response)

    except Exception as e:
        bot.reply_to(message, f"Error processing frame: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    if bot:
        print("Starting Telegram Bot listener...")
        bot.infinity_polling()
