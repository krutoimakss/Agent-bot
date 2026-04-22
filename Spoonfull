import asyncio
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8760493717:AAFYyw8sEYozXlpteQTKGYjomHXLMizedYE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# =======================
# ДАННЫЕ
# =======================

games = {}

MAPS = [
    ("Банк", "💰 Ограбление века..."),
    ("Школа", "🏫 Обычный день..."),
    ("Космос", "🚀 Миссия на Марс..."),
    ("Больница", "🏥 Что-то не так..."),
    ("Военная база", "🪖 Секретный объект...")
]

# =======================
# FSM
# =======================

class QuestionState(StatesGroup):
    waiting_question = State()

class AnswerState(StatesGroup):
    waiting_answer = State()

class VoteState(StatesGroup):
    voting = State()

# =======================
# УТИЛИТЫ
# =======================

async def safe_dm(user_id, text):
    try:
        await bot.send_message(user_id, text)
        return True
    except:
        return False

def is_group(msg: Message):
    return msg.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]

# =======================
# /start
# =======================

@dp.message(Command("start"))
async def start(message: Message):
    if not is_group(message):
        await message.answer("👋 Напиши /start в группе чтобы начать игру")
        return

    chat_id = message.chat.id

    games[chat_id] = {
        "players": {},
        "started": False,
        "agent": None,
        "map": None,
        "talks": 3
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Зайти", callback_data="join")]
    ])

    await message.answer(
        "❗ Набор на игру в агента!\n\n👤 Игроки:",
        reply_markup=kb
    )

# =======================
# JOIN
# =======================

@dp.callback_query(F.data == "join")
async def join(call: CallbackQuery):
    chat_id = call.message.chat.id
    user = call.from_user

    game = games.get(chat_id)
    if not game:
        return

    ok = await safe_dm(user.id, "💌 Вы присоединились к игре!")

    if not ok:
        await call.message.answer(f"⚠️ @{user.username} открой ЛС с ботом")
        return

    game["players"][user.id] = {
        "name": user.full_name,
        "alive": True
    }

    text = "👤 Игроки:\n"
    for p in game["players"].values():
        text += f"- {p['name']}\n"

    await call.message.edit_text(text)

    if len(game["players"]) >= 3 and not game["started"]:
        await start_game(chat_id, call.message)

# =======================
# СТАРТ ИГРЫ
# =======================

async def start_game(chat_id, msg):
    game = games[chat_id]
    game["started"] = True

    players = list(game["players"].keys())
    agent = random.choice(players)
    game["agent"] = agent

    game["map"] = random.choice(MAPS)

    # Роли
    for uid in players:
        if uid == agent:
            await safe_dm(uid, "😈 Ты агент")
        else:
            await safe_dm(uid,
                f"🕵️ Ты инспектор\n🌍 {game['map'][0]}\n{game['map'][1]}"
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

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Задать вопрос", callback_data="ask")]
    ])

    await message.answer("❗ Срочный разговор", reply_markup=kb)

@dp.callback_query(F.data == "ask")
async def ask(call: CallbackQuery, state: FSMContext):
    await call.message.answer("😄 Напиши вопрос")
    await state.set_state(QuestionState.waiting_question)

@dp.message(QuestionState.waiting_question)
async def process_question(message: Message, state: FSMContext):
    await message.answer(f"📚 Вопрос:\n{message.text}")
    await state.clear()

# =======================
# ГОЛОСОВАНИЕ
# =======================

async def vote_timer(chat_id, msg):
    await asyncio.sleep(30)
    await start_vote(chat_id, msg)

async def start_vote(chat_id, msg):
    game = games[chat_id]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Голосовать", callback_data="vote")]
    ])

    await msg.answer("🗳️ Голосование началось", reply_markup=kb)

@dp.callback_query(F.data == "vote")
async def vote(call: CallbackQuery):
    chat_id = call.message.chat.id
    game = games.get(chat_id)

    buttons = []

    for uid, p in game["players"].items():
        if p["alive"]:
            buttons.append([InlineKeyboardButton(
                text=p["name"],
                callback_data=f"vote_{uid}"
            )])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_message(call.from_user.id, "🌴 Вы голосуете", reply_markup=kb)

@dp.callback_query(F.data.startswith("vote_"))
async def vote_pick(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call.message.answer("Голос принят")

# =======================
# НОЧЬ
# =======================

async def night(chat_id, msg):
    await msg.answer("🌃 Ночь")
    await asyncio.sleep(7)

# =======================
# ЗАПУСК
# =======================

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
