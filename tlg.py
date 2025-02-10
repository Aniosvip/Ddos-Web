import threading
import time
import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Cấu hình logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Thông tin bot
GROUP_CHAT_ID = -1002307642304  # ID nhóm Telegram
TELEGRAM_BOT_TOKEN = "7554983188:AAE1VbqSBBVilW8wsJYC-LZEn1rmORE1Rqo"  # Token bot

# Danh sách người dùng được ủy quyền (có thể mở rộng với cơ sở dữ liệu)
AUTHORIZED_USERS = [123456789]  # Thay bằng ID của bạn

# Biến toàn cục để kiểm soát tấn công
attack_event = threading.Event()

# Kiểm tra xem lệnh có đến từ nhóm được ủy quyền hay không
def is_from_authorized_group(update):
    return update.message.chat_id == GROUP_CHAT_ID

# Gửi thông báo vào nhóm
def send_notification(context, message):
    context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message)

# Xử lý lệnh /lag
def lag(update, context):
    if not is_from_authorized_group(update):
        update.message.reply_text("Lệnh này chỉ được sử dụng trong nhóm ủy quyền.")
        return

    try:
        args = context.args
        if len(args) != 4:
            update.message.reply_text("Sai cú pháp. Sử dụng: /lag <phương thức> <ip:port> <luồng> <thời lượng>")
            return

        method, target, threads, duration = args[0].upper(), args[1], int(args[2]), int(args[3])

        if attack_event.is_set():
            attack_event.clear()
            update.message.reply_text("Đã dừng tấn công hiện tại.")

        attack_event.set()
        threading.Thread(target=start_attack, args=(method, target, threads, duration, attack_event)).start()
        send_notification(context, f"Cuộc tấn công đã bắt đầu: {method} -> {target}")
        update.message.reply_text("Cuộc tấn công đã bắt đầu.")

    except Exception as e:
        logger.error(f"Lỗi khi xử lý lệnh /lag: {e}")
        update.message.reply_text("Đã xảy ra lỗi. Vui lòng thử lại.")

# Xử lý lệnh /stop
def stop_attack(update, context):
    if not is_from_authorized_group(update):
        update.message.reply_text("Lệnh này chỉ được sử dụng trong nhóm ủy quyền.")
        return

    if attack_event.is_set():
        attack_event.clear()
        send_notification(context, "Cuộc tấn công đã dừng.")
        update.message.reply_text("Cuộc tấn công đã dừng.")
    else:
        update.message.reply_text("Không có cuộc tấn công nào đang chạy.")

# Xử lý lệnh /get_group_id để kiểm tra ID nhóm
def get_group_id(update, context):
    update.message.reply_text(f"Group ID của bạn là: {update.message.chat_id}")

# Hàm chạy bot Telegram
def run_bot():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("lag", lag))
    dp.add_handler(CommandHandler("stop", stop_attack))
    dp.add_handler(CommandHandler("get_group_id", get_group_id))

    updater.start_polling()
    updater.idle()

# Chạy bot trong một luồng riêng
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True  
bot_thread.start()
