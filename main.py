from server import server
from bot import bot
if __name__ == "__main__":
    bot.loop.create_task(server.serve())
    bot.run()
