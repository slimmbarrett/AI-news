import asyncio
import aiohttp
from keep_alive import keep_alive

from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, MessageMediaWebPage

# ===== Запуск mini-сервера для Railway =====
keep_alive()

# ===== Настройки Telegram API =====
api_id = 25448007
api_hash = 'f4dba8e8c884bbabfd9cd6a742eeb695'

# ===== Каналы =====
source_channels = [
    'discoveryit_channel',
    'black_triangle_tg',
    'technosplit',
    'jumbuu'
]

# Канал для публикации (без https://t.me/)
my_channel = 'Cortex_Innovation'

# ===== Настройки DeepSeek API =====
deepseek_api_url = 'https://api.deepseek.com/v1/chat/completions'
api_key = 'sk-39d991d8c2664a3881a6bef71c172299'

# ===== Инициализация клиента =====
client = TelegramClient('anon', api_id, api_hash)

async def process_text_with_deepseek(text):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    system_prompt = """Ты - профессиональный редактор и аналитик. 
    Твоя задача - проанализировать предоставленный текст и создать новое, 
    более структурированное и информативное сообщение для канала в телеграмме "Схемный Переулок". 
    Сделай так, чтобы текст был понятен для людей, в дружественной форме, попунктам. Максимальное количество символов 500."""

    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text}
        ],
        'temperature': 0.7
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(deepseek_api_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('choices', [{}])[0].get('message', {}).get('content', 'Ошибка: пустой ответ от DeepSeek')
                else:
                    return f'Ошибка API: {response.status} - {await response.text()}'
        except Exception as e:
            return f'Ошибка при обращении к API: {str(e)}'

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    try:
        source_channel = await event.get_chat()
        print(f'\n[+] Получен новый пост из канала: {source_channel.title}')

        original_text = event.text or ""
        print(f'[i] Оригинальный текст: {original_text[:100]}...')

        processed_text = ""
        if original_text:
            processed_text = await process_text_with_deepseek(original_text)
            print(f'[+] Обработанный текст: {processed_text[:100]}...')

        if event.media:
            if isinstance(event.media, (MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage)):
                try:
                    await client.send_file(my_channel, event.media, caption=processed_text)
                    print('[✅] Медиа успешно отправлено в канал!')
                except Exception as e:
                    print(f'[!] Ошибка при отправке медиа: {str(e)}')
                    if processed_text:
                        await client.send_message(my_channel, processed_text)
                        print('[!] Отправлен только текст из-за ошибки с медиа')
            else:
                if processed_text:
                    await client.send_message(my_channel, processed_text)
                    print('[!] Неподдерживаемое медиа, отправлен только текст')
        elif processed_text:
            await client.send_message(my_channel, processed_text)
            print('[✅] Текст без медиа успешно отправлен!')
        else:
            print('[i] Пустой пост пропущен.')
    except Exception as e:
        print(f'[❌] Ошибка при обработке поста: {str(e)}')

async def main():
    await client.start()
    print('✅ Бот успешно запущен и ожидает новые сообщения...')
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())