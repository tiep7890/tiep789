# === FILE CHÍNH: bot.py ===
import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils import logger, config
from buff.buff_manager import BuffManager
from taixiu.sunwin import SunWinPredictor
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

buff_manager = BuffManager()
sunwin_predictor = SunWinPredictor()
guild_id = discord.Object(id=config.GUILD_ID)

@tree.command(name="buffview", description="Buff lượt xem video TikTok")
@app_commands.describe(username="Nhập link hoặc tên TikTok")
async def buff_view(interaction: discord.Interaction, username: str):
    if interaction.channel.id != config.CHANNEL_BUFF_FREE_ID:
        return await interaction.response.send_message("❌ Lệnh này chỉ dùng trong kênh Buff TikTok Free.", ephemeral=True)
    if not buff_manager.can_use_free(interaction.user.id):
        return await interaction.response.send_message("❌ Bạn chỉ được sử dụng lệnh này mỗi 1 tiếng!", ephemeral=True)
    await interaction.response.send_message("🔄 Đang tiến hành buff... Vui lòng chờ.")
    result = await buff_manager.buff_all("view", username)
    await interaction.followup.send(result)

@tree.command(name="bufftim", description="Buff tim video TikTok")
@app_commands.describe(username="Nhập link hoặc tên TikTok")
async def buff_tim(interaction: discord.Interaction, username: str):
    if interaction.channel.id != config.CHANNEL_BUFF_FREE_ID:
        return await interaction.response.send_message("❌ Lệnh này chỉ dùng trong kênh Buff TikTok Free.", ephemeral=True)
    if not buff_manager.can_use_free(interaction.user.id):
        return await interaction.response.send_message("❌ Bạn chỉ được sử dụng lệnh này mỗi 1 tiếng!", ephemeral=True)
    await interaction.response.send_message("🔄 Đang tiến hành buff... Vui lòng chờ.")
    result = await buff_manager.buff_all("tim", username)
    await interaction.followup.send(result)

@tree.command(name="bufffl", description="Buff follow TikTok")
@app_commands.describe(username="Nhập link hoặc tên TikTok")
async def buff_fl(interaction: discord.Interaction, username: str):
    if interaction.channel.id != config.CHANNEL_BUFF_FREE_ID:
        return await interaction.response.send_message("❌ Lệnh này chỉ dùng trong kênh Buff TikTok Free.", ephemeral=True)
    if not buff_manager.can_use_free(interaction.user.id):
        return await interaction.response.send_message("❌ Bạn chỉ được sử dụng lệnh này mỗi 1 tiếng!", ephemeral=True)
    await interaction.response.send_message("🔄 Đang tiến hành buff... Vui lòng chờ.")
    result = await buff_manager.buff_all("follow", username)
    await interaction.followup.send(result)

@tree.command(name="setauto", description="Lưu username TikTok để auto buff")
@app_commands.describe(username="Tên tài khoản TikTok")
async def set_auto(interaction: discord.Interaction, username: str):
    if interaction.channel.id != config.CHANNEL_BUFF_AUTO_ID:
        return await interaction.response.send_message("❌ Lệnh này chỉ dùng trong kênh Buff Auto.", ephemeral=True)
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Chỉ admin mới có quyền dùng chức năng auto.", ephemeral=True)
    buff_manager.set_auto_user(interaction.user.id, username)
    await interaction.response.send_message(f"✅ Đã lưu TikTok: `{username}` cho auto buff!")

@tasks.loop(minutes=17)
async def auto_buff_task():
    channel = bot.get_channel(config.CHANNEL_BUFF_AUTO_ID)
    if not channel:
        return
    results = await buff_manager.run_auto_buff()
    for res in results:
        await channel.send(res)

@tasks.loop(seconds=60)
async def auto_taixiu():
    channel = bot.get_channel(config.CHANNEL_TAIXIU_ID)
    if not channel:
        return
    prediction = await sunwin_predictor.fetch_and_predict()
    if prediction:
        await channel.send(prediction)

@bot.event
async def on_ready():
    await tree.sync(guild=guild_id)
    print(f"Bot đã hoạt động dưới tên: {bot.user}")
    auto_buff_task.start()
    auto_taixiu.start()

bot.run(config.DISCORD_BOT_TOKEN)
