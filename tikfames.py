class TikFamesBuff:
    async def send(self, buff_type, username):
        await asyncio.sleep(1)
        return f"TikFames đã buff {buff_type} cho {username}"
