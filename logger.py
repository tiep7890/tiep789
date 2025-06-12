# utils/logger.py
import logging
import sys
import os

# --- CẤU HÌNH LOGGER ---
LOG_DIR = "logs"  # Thư mục để lưu file log
LOG_FILENAME = "bot.log" # Tên file log
LOG_LEVEL = logging.INFO # Mức log: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)-20s (%(filename)s:%(lineno)d): %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# --- KẾT THÚC CẤU HÌNH ---

# Tạo thư mục logs nếu chưa có
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except OSError as e:
        print(f"Không thể tạo thư mục logs '{LOG_DIR}': {e}. Log sẽ chỉ được xuất ra console.")
        # Nếu không tạo được thư mục, không nên cố ghi file nữa

# Lấy logger gốc (root logger) hoặc một logger cụ thể
# Sử dụng một logger cụ thể cho bot giúp tránh xung đột với logger của thư viện khác
logger = logging.getLogger("MyDiscordBot")
logger.setLevel(LOG_LEVEL) # Quan trọng: đặt level cho logger cụ thể này

# Xóa các handler mặc định nếu có để tránh log bị lặp
if logger.hasHandlers():
    logger.handlers.clear()

# Tạo Formatter
formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

# Tạo Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Tạo File Handler (nếu thư mục logs tồn tại)
if os.path.exists(LOG_DIR):
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILENAME), mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
else:
    logger.warning(f"Thư mục logs '{LOG_DIR}' không tồn tại hoặc không thể tạo. Sẽ không ghi log vào file.")

# Ngăn logger lan truyền lên root logger nếu bạn muốn kiểm soát hoàn toàn
# logger.propagate = False

# Ví dụ cách sử dụng trong các file khác:
# from utils.logger import logger
# logger.info("Đây là một tin nhắn info từ logger của tôi.")
# logger.error("Đây là một tin nhắn lỗi nghiêm trọng.")
