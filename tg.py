import asyncio
import aiohttp
from telethon import TelegramClient, events
import telethon.tl.types

# ===== Настройки Telegram API =====
# IMPORTANT: These credentials are invalid. You need to get new ones:
# 1. Go to https://my.telegram.org/auth
# 2. Log in with your phone number (+37124830631)
# 3. Go to "API development tools"
# 4. Click "Create application"
# 5. Fill in the form and submit
# 6. Copy the new api_id and api_hash here
api_id = '25448007'  # Replace with your new api_id
api_hash = 'f4dba8e8c884bbabfd9cd6a742eeb695'  # Replace with your new api_hash

# Список исходных каналов
source_channels = [
    'https://t.me/neviaia',  # Первый канал
    # 'https://t.me/discoveryit_channel',  # Второй канал
    # 'https://t.me/black_triangle_tg',   # Третий канал
    # Добавьте столько каналов, сколько нужно
]

my_channel = 'https://t.me/Cortex_Innovation'

# ===== Настройки DeepSeek API =====
# Для получения правильных данных:
# 1. Зарегистрируйтесь на https://platform.deepseek.com/
# 2. Создайте новый API ключ
# 3. Скопируйте ваш API ключ и URL эндпоинта
deepseek_api_url = 'https://api.deepseek.com/v1/chat/completions'  # Замените на ваш правильный URL
api_key = 'sk-39d991d8c2664a3881a6bef71c172299'  # Замените на ваш API ключ

# ===== Инициализация клиента =====
client = TelegramClient('session_name', api_id, api_hash)

async def process_text_with_deepseek(text):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Системный промпт, который будет использоваться для всех запросов
    system_prompt = """Ты - профессиональный редактор и аналитик. 
    Твоя задача - проанализировать предоставленный текст и создать новое, 
    более структурированное и информативное сообщение. 
    Сохраняй ключевую информацию, но излагай её более чётко и профессионально для канала в телеграмме который называется Схемный Переулок. Сделай так чтобы текст был понятен для людей в дружественной форме попунктам. Максимальное количество символов 500."""
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': text
            }
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
        # Получаем информацию о канале-источнике
        source_channel = await event.get_chat()
        print(f'Получен новый пост из канала: {source_channel.title}')
        
        # Получаем оригинальный текст сообщения
        original_text = event.text or ""
        print(f'Текст: {original_text[:100]}...')

        # Обрабатываем текст через DeepSeek, если он есть
        processed_text = ""
        if original_text:
            processed_text = await process_text_with_deepseek(original_text)
            print(f'Текст обработан через DeepSeek: {processed_text[:100]}...')

        # Проверяем наличие медиа
        if event.media:
            # Проверяем тип медиа
            if isinstance(event.media, telethon.tl.types.MessageMediaWebPage):
                # Если это веб-превью, отправляем только текст
                if processed_text:
                    await client.send_message(
                        my_channel,
                        processed_text
                    )
                    print('Веб-превью обработано как текст')
            elif isinstance(event.media, (telethon.tl.types.MessageMediaPhoto, 
                                        telethon.tl.types.MessageMediaDocument,
                                        telethon.tl.types.MessageMediaVideo)):
                # Для поддерживаемых типов медиа
                try:
                    await client.send_file(
                        my_channel,
                        event.media,
                        caption=processed_text
                    )
                    print('Медиа успешно отправлено в целевой канал')
                except Exception as e:
                    print(f'Ошибка при отправке медиа: {str(e)}')
                    # Если не удалось отправить медиа, отправляем хотя бы текст
                    if processed_text:
                        await client.send_message(
                            my_channel,
                            processed_text
                        )
                        print('Отправлен только текст из-за ошибки с медиа')
            else:
                # Для неподдерживаемых типов медиа отправляем только текст
                if processed_text:
                    await client.send_message(
                        my_channel,
                        processed_text
                    )
                    print('Неподдерживаемый тип медиа, отправлен только текст')
        elif processed_text:  # Если есть только текст, отправляем его
            await client.send_message(
                my_channel,
                processed_text
            )
            print('Текст успешно отправлен в целевой канал')
        else:
            print('Пропущен пустой пост.')
    except Exception as e:
        print(f'Ошибка при обработке сообщения: {str(e)}')

async def main():
    await client.start()
    print('Бот запущен!')
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
