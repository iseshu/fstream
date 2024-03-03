from pyrogram import Client
from os import environ as env
api_id = env.get('API_ID',10031344)
api_hash = env.get('API_HASH','41a778bcd36bad91cadb5bb76f013ddd')
bot_token = env.get('BOT_TOKEN','6327070022:AAFOkBCeWYCb9JYdvkCVoN9j-5F9nWHEHr8')

bot = Client(
    "my_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    plugins=dict(root="plugins")
)
