import asyncio
from buff.zefoy import ZefoyBuff
from buff.tikfollowers import TikFollowersBuff
from buff.tikfames import TikFamesBuff

class BuffManager:
    def __init__(self):
        self.auto_users = {}
        self.cooldowns = {}

    def can_use_free(self, user_id):
        from time import time
        if user_id in self.cooldowns and time() - self.cooldowns[user_id] < 3600:
            return False
        self.cooldowns[user_id] = time()
        return True

    def set_auto_user(self, user_id, username):
        self.auto_users[user_id] = username

    async def run_auto_buff(self):
        results = []
        for uid, username in self.auto_users.items():
            result = await self.buff_all("follow", username)
            results.append(result)
        return results

    async def buff_all(self, buff_type, username):
        results = []
        for buff_class in [ZefoyBuff, TikFollowersBuff, TikFamesBuff]:
            try:
                result = await buff_class().send(buff_type, username)
                results.append(f"✅ API đã tăng {buff_type.upper()} thành công cho `{username}`")
                await asyncio.sleep(25)
            except Exception as e:
                results.append(f"❌ Lỗi từ API: {e}")
        return "\n".join(results)
