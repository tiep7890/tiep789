class ZefoyBuff:
    async def send(self, buff_type, username):
        await asyncio.sleep(1)  # Giả lập delay
        return f"Zefoy đã buff {buff_type} cho {username}"
