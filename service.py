import os
import bot
if __name__ == "__main__":
    try: os.remove(bot.STOP)
    except Exception: pass
    bot.Bot(bot.load_cfg()).run()
