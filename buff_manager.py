# buff/buff_manager.py
import time
import asyncio # Thêm asyncio
from utils.logger import logger

# Lưu trữ thời gian sử dụng cuối cùng của người dùng cho dịch vụ free
# {user_id: timestamp}
free_usage_timestamps = {}
FREE_COOLDOWN_SECONDS = 60 * 60  # 1 tiếng (3600 giây)

class BuffManager:
    def __init__(self):
        logger.info("BuffManager initialized.")
        # Khởi tạo các kết nối hoặc cấu hình cần thiết ở đây
        # Ví dụ: self.api_client = SomeAPIClient()

    def can_use_free(self, user_id: int) -> bool:
        """Kiểm tra xem người dùng có thể sử dụng dịch vụ free không (dựa trên cooldown)."""
        last_usage = free_usage_timestamps.get(user_id)
        if last_usage is None:
            return True  # Chưa sử dụng lần nào
        
        if time.time() - last_usage >= FREE_COOLDOWN_SECONDS:
            return True # Đã hết cooldown
        return False

    def get_cooldown_remaining_str(self, user_id: int) -> str:
        """Trả về chuỗi thời gian cooldown còn lại, hoặc chuỗi rỗng nếu không có cooldown."""
        last_usage = free_usage_timestamps.get(user_id)
        if last_usage is None:
            return "" # Không có cooldown
        
        elapsed_time = time.time() - last_usage
        if elapsed_time >= FREE_COOLDOWN_SECONDS:
            return "" # Đã hết cooldown
        
        remaining_seconds = int(FREE_COOLDOWN_SECONDS - elapsed_time)
        
        hours = remaining_seconds // 3600
        minutes = (remaining_seconds % 3600) // 60
        seconds = remaining_seconds % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours} giờ")
        if minutes > 0:
            parts.append(f"{minutes} phút")
        # Luôn hiển thị giây nếu không có giờ/phút, hoặc nếu là phần còn lại duy nhất
        if seconds > 0 or not parts: 
            parts.append(f"{seconds} giây")
        
        return ", ".join(parts) if parts else "0 giây"


    def record_free_usage(self, user_id: int):
        """Ghi nhận người dùng đã sử dụng dịch vụ free."""
        free_usage_timestamps[user_id] = time.time()
        logger.info(f"User {user_id} used free buff service. Cooldown started for {FREE_COOLDOWN_SECONDS // 3600} hour(s).")

    async def buff_all(self, service_type: str, target: str, user_id: int = None) -> str:
        """
        Thực hiện hành động buff.
        Đây là một placeholder, bạn cần triển khai logic thực tế ở đây.
        Ví dụ: gọi API của một dịch vụ buff.
        """
        logger.info(f"User {user_id} requested to buff '{service_type}' for target '{target}'.")
        
        # --- LOGIC BUFF THỰC TẾ CỦA BẠN SẼ Ở ĐÂY ---
        # Ví dụ mô phỏng một cuộc gọi API và xử lý kết quả
        try:
            # logger.debug(f"Calling external API for {service_type} on {target}...")
            # response = await some_async_http_client.post(
            #     "https://api.examplebuff.com/buff",
            #     json={"service": service_type, "target": target, "quantity": 1000}
            # )
            # response.raise_for_status() # Ném lỗi nếu HTTP status là 4xx hoặc 5xx
            # data = response.json()
            # if data.get("status") == "success":
            #     return f"✅ Đã buff thành công {data.get('amount', 'một lượng')} {service_type} cho {target}!"
            # else:
            #     error_message = data.get("message", "Lỗi không xác định từ API.")
            #     logger.error(f"API error for {target}: {error_message}")
            #     return f"❌ Lỗi khi buff {service_type} cho {target}: {error_message}"

            # Placeholder logic:
            await asyncio.sleep(3) # Giả lập một tác vụ I/O tốn thời gian (ví dụ: gọi API)

            if "error_target" in target.lower(): # Giả lập một lỗi có thể xảy ra
                 logger.warning(f"Simulated error for target: {target}")
                 # raise ValueError("Simulated error during buffing process for target: " + target)
                 return f"❌ Đã xảy ra lỗi mô phỏng khi buff cho `{target}`."
            
            # Nếu thành công
            views_buffed = 1000 # Số lượng buff được (ví dụ)
            logger.info(f"Successfully processed buff request for {target}. Views added: {views_buffed}")
            return f"✅ Yêu cầu buff `{service_type}` cho `{target}` đã được xử lý thành công. Đã thêm khoảng {views_buffed} lượt xem (đây là phản hồi mẫu)."

        except Exception as e:
            logger.error(f"Exception during buff_all for {target} (User: {user_id}): {e}", exc_info=True)
            # Ném lại lỗi để bot.py có thể bắt và gửi thông báo lỗi chung
            raise
        # --- KẾT THÚC LOGIC BUFF THỰC TẾ ---
