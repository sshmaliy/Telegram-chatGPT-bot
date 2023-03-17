import openai
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions
from aiogram import executor

# Set up the OpenAI API credentials
openai.api_key = "YOUR_OPENAI_API_KEY"

# Set up the Telegram bot
bot = Bot(token="YOUR_TELEGRAM_TOKEN")
dp = Dispatcher(bot)

# Define the message handler
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_message(message: types.Message):
    if message.chat.type == types.ChatType.PRIVATE:
        # If the message is from a private chat, call the OpenAI API to generate a response
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=message.text,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
        )
        # Send the response to the user
        await message.reply(response.choices[0].text)
    elif message.chat.type == types.ChatType.GROUP or message.chat.type == types.ChatType.SUPERGROUP:
        # If the message is from a group or a supergroup, check if the bot is mentioned
        bot_username = (await bot.me).username
        if f"@{bot_username}" in message.text:
            # If the bot is mentioned, call the OpenAI API to generate a response
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=message.text,
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.7,
            )
            # Send the response to the group chat
            try:
                await bot.send_message(chat_id=message.chat.id, text=response.choices[0].text)
            except exceptions.BotBlocked:
                print(f"Bot is blocked by the group chat {message.chat.title} ({message.chat.id})")
            except exceptions.ChatNotFound:
                print(f"Group chat not found: {message.chat.title} ({message.chat.id})")
            except exceptions.RetryAfter as e:
                print(f"Rate limited. Retry in {e.timeout} seconds.")
                await asyncio.sleep(e.timeout)
                return handle_message(message)  # Recursive call
            except exceptions.TelegramAPIError:
                print(f"Failed to send message to group chat {message.chat.title} ({message.chat.id})")

# Start the bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
