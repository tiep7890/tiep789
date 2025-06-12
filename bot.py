# === FILE CHÍNH: bot.py ===
import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils import logger, config  # Đảm bảo bạn có file logger.py và config.py trong thư mục utils
from buff.buff_manager import BuffManager # Đảm bảo bạn có BuffManager trong buff/buff_manager.py
from taixiu.sunwin import SunWinPredictor # Đảm bảo bạn có SunWinPredictor trong taixiu/sunwin.py
import asyncio
import os # Thêm os để tạo thư mục logs nếu cần

# --- Cài đặt Intents ---
intents = discord.Intents.all()

# --- Khởi tạo Bot ---
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Khởi tạo Managers và Variables ---
try:
    buff_manager = BuffManager()
    sunwin_predictor = SunWinPredictor()
    guild_id_config = getattr(config, 'GUILD_ID', 0) # Lấy GUILD_ID, mặc định là 0 nếu không có
    guild_id = discord.Object(id=guild_id_config) if guild_id_config else None

    channel_buff_free_id = config.CHANNEL_BUFF_FREE_ID
except AttributeError as e:
    # Ghi log bằng logger đã import, hoặc print nếu logger chưa sẵn sàng
    print(f"CRITICAL: Lỗi khi đọc cấu hình từ config.py: {e}. Vui lòng kiểm tra file config.py (GUILD_ID, CHANNEL_BUFF_FREE_ID, BOT_TOKEN)")
    if 'logger' in globals(): # Kiểm tra logger đã được import và khởi tạo chưa
        logger.critical(f"Lỗi khi đọc cấu hình từ config.py: {e}. Vui lòng kiểm tra file config.py.", exc_info=True)
    exit() # Thoát nếu thiếu config cơ bản
except Exception as e:
    print(f"CRITICAL: Lỗi không xác định khi khởi tạo manager hoặc config: {e}")
    if 'logger' in globals():
        logger.critical(f"Lỗi không xác định khi khởi tạo manager hoặc config: {e}", exc_info=True)
    exit()

# --- Sự kiện Bot Sẵn Sàng ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    logger.info(f'Bot {bot.user.name} (ID: {bot.user.id}) đã khởi động thành công!')

    try:
        if guild_id:
            # bot.tree.copy_global_to(guild=guild_id) # Bỏ comment nếu bạn muốn copy lệnh global vào guild này
            synced = await bot.tree.sync(guild=guild_id)
            logger.info(f"Đã đồng bộ {len(synced)} lệnh ứng dụng cho guild {guild_id.id}.")
        else:
            logger.warning("Không có GUILD_ID hợp lệ trong config hoặc GUILD_ID=0. Tiến hành đồng bộ lệnh toàn cục.")
            synced = await bot.tree.sync()
            logger.info(f"Đã đồng bộ {len(synced)} lệnh ứng dụng toàn cục.")
    except Exception as e:
        logger.error(f"Lỗi khi đồng bộ lệnh ứng dụng: {e}", exc_info=True)

# --- Định nghĩa Lệnh Ứng Dụng (Slash Command) ---
@bot.tree.command(name="buffview", description="Buff lượt xem video TikTok")
@app_commands.describe(link_or_username="Nhập link video hoặc username TikTok")
async def buff_view(interaction: discord.Interaction, link_or_username: str):
    if interaction.channel_id != channel_buff_free_id:
        await interaction.response.send_message(
            "❌ Lệnh này chỉ được sử dụng trong kênh Buff TikTok Free.",
            ephemeral=True
        )
        return

    user_id = interaction.user.id
    if not buff_manager.can_use_free(user_id):
        cooldown_remaining_str = buff_manager.get_cooldown_remaining_str(user_id)
        message = "❌ Bạn chỉ được sử dụng lệnh này mỗi 1 tiếng!"
        if cooldown_remaining_str:
            message += f" Vui lòng thử lại sau {cooldown_remaining_str}."
        await interaction.response.send_message(message, ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False, thinking=True)

    try:
        logger.info(f"Người dùng {interaction.user} (ID: {user_id}) yêu cầu buff view cho: {link_or_username}")
        result_message = await buff_manager.buff_all("view", link_or_username, user_id=user_id)
        await interaction.followup.send(result_message)
        logger.info(f"Buff view thành công cho '{link_or_username}' bởi {interaction.user}. Kết quả: {result_message}")
        buff_manager.record_free_usage(user_id)
    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng khi thực hiện buff_view cho '{link_or_username}' bởi {interaction.user}: {e}", exc_info=True)
        try:
            await interaction.followup.send(
                " Rất tiếc, đã có lỗi xảy ra trong quá trình buff. Vui lòng thử lại sau hoặc liên hệ quản trị viên.",
                ephemeral=True
            )
        except discord.errors.NotFound:
            logger.warning(f"Không thể gửi followup lỗi cho interaction của {interaction.user} (buff_view) vì interaction không còn tồn tại.")
        except Exception as followup_e:
            logger.error(f"Lỗi khi gửi followup thông báo lỗi cho {interaction.user} (buff_view): {followup_e}", exc_info=True)

# --- Chạy Bot ---
if __name__ == "__main__":
    try:
        # Đảm bảo thư mục logs tồn tại (nếu logger.py có ghi file)
        log_dir_from_logger = getattr(logger, 'LOG_DIR', 'logs') # Cố gắng lấy LOG_DIR từ logger
        if not os.path.exists(log_dir_from_logger) and any(isinstance(h, logging.FileHandler) for h in logger.logger.handlers if hasattr(logger, 'logger')):
             os.makedirs(log_dir_from_logger, exist_ok=True)


        bot_token = config.BOT_TOKEN
        if not bot_token or bot_token == "YOUR_DISCORD_BOT_TOKEN": # Kiểm tra giá trị mặc định
            logger.critical("BOT_TOKEN không được tìm thấy hoặc chưa được cấu hình trong file config.py. Bot không thể khởi động.")
            print("CRITICAL: BOT_TOKEN không được tìm thấy hoặc chưa được cấu hình trong file config.py. Bot không thể khởi động.")
        else:
            logger.info("Đang khởi chạy bot...")
            # Nếu logger của bạn đã được cấu hình, truyền log_handler=None để discord.py không ghi đè
            # Tuy nhiên, discord.py >= 2.0 thường tự xử lý tốt việc này.
            # Bạn có thể bỏ log_handler=None nếu logger của bạn là root logger hoặc bạn muốn discord.py sử dụng nó.
            bot.run(bot_token, log_handler=None if 'logger' in globals() else logging.StreamHandler())
    except AttributeError as e:
        msg = "BOT_TOKEN hoặc các biến config khác không được định nghĩa trong config.py."
        if 'logger' in globals(): logger.critical(msg + f" Lỗi: {e}", exc_info=True)
        else: print(f"CRITICAL: {msg} Lỗi: {e}")
    except discord.errors.LoginFailure:
        msg = "Login thất bại. Vui lòng kiểm tra BOT_TOKEN có chính xác không."
        if 'logger' in globals(): logger.critical(msg, exc_info=True)
        else: print(f"CRITICAL: {msg}")
    except Exception as e:
        msg = f"Lỗi không xác định khi cố gắng chạy bot: {e}"
        if 'logger' in globals(): logger.critical(msg, exc_info=True)
        else: print(f"CRITICAL: {msg}")
