import asyncio
import random
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = os.getenv("8760493717:AAFYyw8sEYozXlpteQTKGYjomHXLMizedYE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

games = {}

# =======================
# КАРТЫ
# =======================

MAPS = [
    ("Космическая база", "Вы прилетели в космос... найдите самозванца."),
    ("Ферма", "Заброшенная ферма... кто-то поставил мины."),
    ("Луна", "Экспедиция провалилась... найдите предателя."),
    ("Шахта", "Темная шахта... кто-то украл кирку."),
    ("Парк", "Парк закрыт... сотрудники исчезли.")
]

# =======================
# КНОПКИ
# =======================

def join_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Зайти", callback_data="join")]
    ])

# =======================
# УТИЛИТЫ
# =======================

def is_group(msg: Message):
    return msg.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]

async def safe_dm(uid, text):
    try:
        await bot.send_message(uid, text)
        return True
    except:
        return False

# =======================
# START
# =======================

@dp.message(Command("start"))
async def start(message: Message):
    if not is_group(message):
        await message.answer("Напиши /start в группе")
        return

    chat_id = message.chat.id

    games[chat_id] = {
        "players": {},
        "started": False,
        "agent": None,
        "map": None,
        "lobby_open": True,
        "talks": 3
    }

    await message.answer(
        "❗ Набор в игру (15 сек)\n\n👤 Игроки:",
        reply_markup=join_kb()
    )

    asyncio.create_task(lobby_timer(chat_id, message))

# =======================
# ЛОББИ ТАЙМЕР
# =======================

async def lobby_timer(chat_id, message):
    await asyncio.sleep(15)

    game = games.get(chat_id)
    if not game:
        return

    game["lobby_open"] = False

    if len(game["players"]) < 3:
        await message.answer("❌ Нужно минимум 3 игрока")
        return

    await start_game(chat_id, message)

# =======================
# JOIN
# =======================

@dp.callback_query(F.data == "join")
async def join(call: CallbackQuery):
    chat_id = call.message.chat.id
    user = call.from_user

    game = games.get(chat_id)
    if not game or game["started"]:
        return

    if not game["lobby_open"]:
        await call.answer("Набор закрыт!", show_alert=True)
        return

    if user.id in game["players"]:
        await call.answer("Ты уже в игре")
        return

    ok = await safe_dm(user.id, "💌 Ты присоединился к игре!")
    if not ok:
        await call.answer("Открой ЛС с ботом!", show_alert=True)
        return

    game["players"][user.id] = {
        "name": user.full_name,
        "role": None,
        "alive": True
    }

    text = "👤 Игроки:\n\n"
    for p in game["players"].values():
        text += f"- {p['name']}\n"

    await call.message.edit_text(text, reply_markup=join_kb())
    await call.answer("Ты в игре!")

# =======================
# СТАРТ ИГРЫ
# =======================

async def start_game(chat_id, msg):
    game = games[chat_id]

    if game["started"]:
        return

    game["started"] = True

    players = list(game["players"].keys())
    agent = random.choice(players)
    game["agent"] = agent
    game["map"] = random.choice(MAPS)

    for uid in players:
        if uid == agent:
            game["players"][uid]["role"] = "agent"
            await safe_dm(uid,
                "😈 Ты агент\nТвоя задача узнать карту и не спалиться!"
            )
        else:
            game["players"][uid]["role"] = "inspector"
            await safe_dm(uid,
                f"🕵️ Ты Инспектор\n🌍 {game['map'][0]}\n{game['map'][1]}"
            )

    await msg.answer(
        "🎮 Игра началась!\n\n"
        "/TalkToHim\n"
        "/ExtraVoting\n"
        "⏳ Голосование через 30 сек"
    )

    asyncio.create_task(vote_timer(chat_id, msg))

# =======================
# TALK
# =======================

@dp.message(Command("TalkToHim"))
async def talk(message: Message):
    chat_id = message.chat.id
    game = games.get(chat_id)

    if not game or game["talks"] <= 0:
        return

    game["talks"] -= 1

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Задать вопрос", callback_data="ask")]
    ])

    await message.answer("❗ Срочный разговор", reply_markup=kb)

@dp.callback_query(F.data == "ask")
async def ask(call: CallbackQuery):
    await call.message.answer("Напиши вопрос в ЛС бота")

# =======================
# ГОЛОСОВАНИЕ (БАЗА)
# =======================

async def vote_timer(chat_id, msg):
    await asyncio.sleep(30)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Голосовать", callback_data="vote")]
    ])

    await msg.answer("🗳️ Голосование началось", reply_markup=kb)

# =======================
# ЗАПУСК
# =======================

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
