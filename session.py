from telethon.sync import TelegramClient

api_id = 25448007
api_hash = 'f4dba8e8c884bbabfd9cd6a742eeb695'

client = TelegramClient('anon', api_id, api_hash)
client.start()

print("Сессия успешно создана: anon.session")

