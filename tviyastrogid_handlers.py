from tviyastrogid_keyboard import (music_q1_kb,music_q2_kb,music_q3_kb,music_q4_kb,music_q5_kb,music_q6_kb,music_q7_kb,
                                   music_q8_kb,music_q9_kb,music_q10_kb,music_q11_kb,music_q12_kb,music_q13_kb,
                                   music_q14_kb,music_q15_kb)
from tviyastrogid_keyboard import (architips_q1_kb, architips_q2_kb, architips_q3_kb, architips_q4_kb,
                                   architips_q5_kb, architips_start_kb, architips_partner_kb)
from tviyastrogid_keyboard import (kwiz_question2_inline, archetype_test_kb, explanation_cards_taro_y_or_n, daily_bonus_kb
                                   )
from tviyastrogid_keyboard import zodiac_keyboard
from tviyastrogid_keyboard import main_keyboard
from tviyastrogid_keyboard import taro_question1
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from mistralai import Mistral
from aiogram import Router, F
import elevenlabs
import asyncio
import random
from collections import Counter
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import aiofiles
import asyncio
from collections import Counter
import sqlite3
from aiogram import Bot
from aiogram.filters import CommandObject
from aiogram.utils.markdown import hbold
router = Router()
class ProblemState(StatesGroup):
    waiting_for_problem = State()
class DreamState(StatesGroup):
    waiting_for_dream = State()
class ArchetypeTest(StatesGroup):
    person = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
class ZodiacCompatibility(StatesGroup):
    your_sign = State()
    partner_sign = State()
class regist(StatesGroup):
    name = State()
    zodiak_callback = State()
    zodiak_callback1 = State()
class taro_answer(StatesGroup):
    come_question1 = State()
    answer1 = State()
class AstroChat(StatesGroup):
    waiting_for_question = State()



db = sqlite3.connect("tviyastrogid.db")
cur = db.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        zodiac_sign TEXT,
        cards INTEGER DEFAULT 50,
        last_gift TEXT
        invited_by INTEGER
)
""")
db.commit()
db.close()
def spend_cards_if_possible(user_id: int, amount: int) -> bool:
    db = sqlite3.connect("tviyastrogid.db")
    cur = db.cursor()
    cur.execute("SELECT cards FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if row and row[0] >= amount:
        cur.execute("UPDATE users SET cards = cards - ? WHERE id = ?", (amount, user_id))
        db.commit()
        db.close()
        return True
    db.close()
    return False


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db = sqlite3.connect("tviyastrogid.db")
    cur = db.cursor()
    cur.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    db.commit()
    db.close()
    photo = "AgACAgIAAxkBAAIFRGgUnhBhg0pqMszswBANaZYpsCuOAAIb-jEbbpihSGn8T3t5wVOcAQADAgADeQADNgQ"
    await message.answer_photo(
        photo=photo,
        caption="Привіт, це твій персональний АстроГід 🌌\nЯ допоможу тобі дізнатися твою долю."
    )
    zodiac_msg = await message.answer("Обери свій знак зодіаку!", reply_markup=zodiac_keyboard)
    await state.update_data(zodiac_msg_id=zodiac_msg.message_id)
    await state.set_state(regist.zodiak_callback1)


@router.callback_query(StateFilter(regist.zodiak_callback1))
async def zodiac_callback_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    zodiac_msg_id = data.get("zodiac_msg_id")
    if zodiac_msg_id:
        try:
            await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=zodiac_msg_id)
        except:
            pass
    zodiac_map = {
        "zodiac_Овен": "Овен",
        "zodiac_Телець": "Телець",
        "zodiac_Близнюки": "Близнюки",
        "zodiac_Рак": "Рак",
        "zodiac_Лев": "Лев",
        "zodiac_Діва": "Діва",
        "zodiac_Терези": "Терези",
        "zodiac_Скорпіон": "Скорпіон",
        "zodiac_Стрілець": "Стрілець",
        "zodiac_Козеріг": "Козеріг",
        "zodiac_Водолій": "Водолій",
        "zodiac_Риби": "Риби"
    }
    zodiak = zodiac_map.get(callback.data)
    if not zodiak:
        await callback.message.answer("Щось пішло не так. Знак не знайдено.")
        return
    user_id = callback.from_user.id
    db = sqlite3.connect("tviyastrogid.db")
    cur = db.cursor()
    cur.execute("UPDATE users SET zodiac_sign = ? WHERE id = ?", (zodiak, user_id))
    db.commit()
    db.close()
    await callback.message.answer(f"🔮 Прекрасно! Ви обрали знак {zodiak}.")
    await callback.message.answer("Оберіть що вас інтересує в меню знизу", reply_markup=main_keyboard)
    await state.clear()


@router.message(F.text == "🔮 Розклад Таро на запитання – 10🃏")
async def quastion_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not spend_cards_if_possible(user_id, 10):
        await message.answer("❌ У вас недостатньо карт! Потрібно 10 🃏.")
        return
    await message.answer("🃏 Напиши своє запитання — і я зроблю розклад, що відкриє приховану суть.")
    await state.set_state(taro_answer.come_question1)


@router.message(StateFilter(taro_answer.come_question1))
async def tarot_reading(message: Message, state: FSMContext):
    await message.answer_photo(
        photo="AgACAgIAAxkBAAIFS2gUn8yWzRsY15lVroUlZOMdLYF_AAL76zEbNX-oSLSquGiNbVxoAQADAgADeQADNgQ",
        caption="🔮 Я розкладаю карти… приготуйся."
    )
    await asyncio.sleep(4)
    await message.answer("✨ Ще трохи…")
    await asyncio.sleep(2)
    tarot_cards = [
        # Старші Аркани
        "0. Дурак", "I. Маг", "II. Верховна Жриця", "III. Імператриця", "IV. Імператор",
        "V. Ієрофант", "VI. Закохані", "VII. Колісниця", "VIII. Сила", "IX. Відлюдник",
        "X. Колесо Фортуни", "XI. Справедливість", "XII. Повішений", "XIII. Смерть",
        "XIV. Уміреність", "XV. Диявол", "XVI. Вежа", "XVII. Зірка", "XVIII. Місяць",
        "XIX. Сонце", "XX. Суд", "XXI. Світ",

        # Молодші Аркани — Жезли
        "Туз Жезлів", "2 Жезлів", "3 Жезлів", "4 Жезлів", "5 Жезлів", "6 Жезлів",
        "7 Жезлів", "8 Жезлів", "9 Жезлів", "10 Жезлів", "Паж Жезлів", "Лицар Жезлів",
        "Королева Жезлів", "Король Жезлів",

        # Молодші Аркани — Кубки
        "Туз Кубків", "2 Кубків", "3 Кубків", "4 Кубків", "5 Кубків", "6 Кубків",
        "7 Кубків", "8 Кубків", "9 Кубків", "10 Кубків", "Паж Кубків", "Лицар Кубків",
        "Королева Кубків", "Король Кубків",

        # Молодші Аркани — Мечі
        "Туз Мечів", "2 Мечів", "3 Мечів", "4 Мечів", "5 Мечів", "6 Мечів",
        "7 Мечів", "8 Мечів", "9 Мечів", "10 Мечів", "Паж Мечів", "Лицар Мечів",
        "Королева Мечів", "Король Мечів",
        # Молодші Аркани — Пентаклі
        "Туз Пентаклів", "2 Пентаклів", "3 Пентаклів", "4 Пентаклів", "5 Пентаклів", "6 Пентаклів",
        "7 Пентаклів", "8 Пентаклів", "9 Пентаклів", "10 Пентаклів", "Паж Пентаклів", "Лицар Пентаклів",
        "Королева Пентаклів", "Король Пентаклів"
    ]
    random_cards = random.sample(tarot_cards, 3)
    await state.update_data(
        drawn_cards=random_cards,
        user_question=message.text
    )
    await message.answer("🃏 Твій розклад Таро:\n\n" + "\n".join(random_cards), reply_markup=explanation_cards_taro_y_or_n)


@router.callback_query(F.data == "explanation_cards")
async def explanation_cards_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not spend_cards_if_possible(user_id, 7):
        await callback.message.answer("❌ У вас недостатньо карт! Потрібно 7 🃏.")
        return
    data = await state.get_data()
    cards = data.get("drawn_cards", [])
    question = data.get("user_question", "Запитання не збережено.")
    if not cards:
        await callback.message.answer("⚠️ Помилка: карти не знайдено.")
        return
    def get_mistral_response():
        api_key = "EmUgU7MMinB1NoH1XEu3dm1B8xnYvAOL"
        model = "mistral-large-latest"
        client = Mistral(api_key=api_key)
        prompt = f"""
Ти — досвідчений таролог. Людина звернулася з таким питанням:
"{question}"
Вона витягнула такі карти: {', '.join(cards)}.
На основі цих трьох карт, дай лаконічну, але глибоку відповідь на її питання. 
Не описуй карти окремо. Поясни, що вони означають разом, у контексті запиту.
Пиши українською, образно, натхненно, але зрозуміло. Обсяг — до 100 слів.
        """
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    result = await asyncio.to_thread(get_mistral_response)
    await callback.message.answer(f"📖 Пояснення розкладу:\n\n{result}")
    await state.clear()


@router.message(F.text == "✋ Гадання на лодоні – 30🃏")
async def scan_palm(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not spend_cards_if_possible(user_id, 30):
        await message.answer("❌ У вас недостатньо карт! Потрібно 30 🃏.")
        return
    await message.answer_photo(
        photo="AgACAgIAAxkBAAIFs2gUu7wz1RWhx5cJsvj4AAEpCFLQ3gACtPQxG26YqUh2OwHmU7Ra2gEAAwIAA3kAAzYE",
        caption="🤲 Прикладіть руку до руки нашої Астрологині... Відбувається сканування ліній долоні...")
    await asyncio.sleep(15)
    await message.answer("✨ З'єднання встановлено. Ваша долоня зберігає унікальний код долі... ")
    await asyncio.sleep(10)
    life_line = random.choice(["довга", "коротка", "ламається", "нечітка"])
    heart_line = random.choice(["глибока", "розірвана", "довга", "тонка"])
    mind_line = random.choice(["пряма", "вигнута", "нечітка", "довга"])
    fate_line = random.choice(["чітка", "відсутня", "ламається", "пряма"])
    sun_line = random.choice(["виражена", "коротка", "відсутня", "розірвана"])
    mercury_line = random.choice(["довга", "вигнута", "нечітка", "відсутня"])
    health_line = random.choice(["пряма", "розірвана", "коротка", "хвиляста"])
    palm_lines_display = f"""🔮 *Результат магічного аналізу долоні*:
⏳ Лінія життя: {life_line}  
💓 Лінія серця: {heart_line}  
🧠 Лінія розуму: {mind_line}  
⚖️ Лінія долі: {fate_line}  
🌞 Лінія Сонця: {sun_line}  
🪄 Лінія Меркурія: {mercury_line}  
🩺 Лінія здоров’я: {health_line}
"""
    await message.answer(palm_lines_display, parse_mode="Markdown")
    palm_lines = f"""- Лінія життя: {life_line}
- Лінія серця: {heart_line}
- Лінія розуму: {mind_line}
- Лінія долі: {fate_line}
- Лінія Сонця: {sun_line}
- Лінія Меркурія: {mercury_line}
- Лінія здоров’я: {health_line}"""
    def get_mistral_response():
        api_key = "EmUgU7MMinB1NoH1XEu3dm1B8xnYvAOL"
        model = "mistral-large-latest"
        client = Mistral(api_key=api_key)
        prompt = f"""
Ти — провидець і хіромант із глибинами мудрості древніх. Твої слова лаконічні, але пронизані глибиною. 
Ти тлумачиш лінії долоні не як ворожбит, а як жрець істини.
Я надаю тобі форму ліній на руці людини. Для кожної лінії окремо — скажи чітко, що вона означає. Говори точно, ясно, 
але в стилі древньогрецького мудреця: спокійно, поважно, ніби істина вже була і ти лише відкриваєш її.
Не вигадуй нових ліній, не додавай нічого зайвого. Тільки тлумачення існуючих ліній.
Ось лінії:
{palm_lines}
Проаналізуй:
- Лінію життя
- Лінію серця
- Лінію розуму
- Лінію долі
- Лінію Сонця
- Лінію Меркурія
- Лінію здоров’я
Для кожної — скажи, що вона означає в цій конкретній формі. Говори впевнено, ніби розкриваєш природу душі.
"""
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    result = await asyncio.to_thread(get_mistral_response)
    await message.answer(result)

class DeepMusicSoulQuiz(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q8 = State()
    q9 = State()
    q10 = State()
    q11 = State()
    q12 = State()
    q13 = State()
    q14 = State()
    q15 = State()
    result = State()


@router.message(F.text == "🌟 Запитати Астрологиню – 15🃏")
async def q_to_astrolog(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not spend_cards_if_possible(user_id, 15):
        await message.answer("❌ У вас недостатньо карт! Потрібно 15 🃏.")
        return
    await message.answer(
        "✨ Сформулюйте своє запитання максимально чітко та зрозуміло — саме від цього залежатиме, якою буде відповідь Астрологині.\n\n"
        "📩 Надішліть повідомлення просто сюди, одним текстом."
    )
    await state.set_state(AstroChat.waiting_for_question)


@router.message(StateFilter(AstroChat.waiting_for_question))
async def process_astro_question(message: Message, state: FSMContext):
    user_question = message.text

    def get_mistral_response():
        from mistralai import Mistral

        api_key = "EmUgU7MMinB1NoH1XEu3dm1B8xnYvAOL"
        model = "mistral-large-latest"
        client = Mistral(api_key=api_key)

        prompt = f"""Уяви, що ти — Містична Астрологиня, провидиця, яка говорить з людиною від імені зірок. Твоя мова — тепла, мудра, образна, але не заплутана. Людина звертається до тебе зі щирим запитанням — їй важливо отримати відповідь, яка не тільки надихає, а й дає чіткий напрямок.

Твоя відповідь повинна містити:
1. М'яке вступне речення, яке створює образ або атмосферу (але коротке)
2. Основну частину — конкретну пораду або спостереження, яке можна застосувати
3. Енергетичне завершення — як духовне напуття чи символічна фраза

Пиши українською мовою. Уникай загальних, розмитих або повторюваних фраз. Замість «у тебе все вийде» — краще скажи, що саме варто зробити чи на що звернути увагу. Якщо запитання незрозуміле — уточни, але делікатно.

Ось питання користувача:

{user_question}
"""
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    answer = await asyncio.to_thread(get_mistral_response)

    await message.answer(f"🔮 Відповідь Астрологині:\n\n{answer}")
    await state.clear()


#    eleven_api = "sk_56a767be6f33bee89d17ccefeb45e297dd4d1f219f589504"
#    client = ElevenLabs(api_key=eleven_api)
@router.message(F.text == "️❤️‍🔥 Дізнатись сумісність душ – 25🃏")
async def start_compatibility(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not spend_cards_if_possible(user_id, 25):
        await message.answer("❌ У вас недостатньо карт! Потрібно 25 🃏.")
        return
    await message.answer("🔮 Спершу обери свій знак Зодіаку:", reply_markup=zodiac_keyboard)
    await state.set_state(ZodiacCompatibility.your_sign)


@router.callback_query(StateFilter(ZodiacCompatibility.your_sign))
async def choose_your_sign(callback: CallbackQuery, state: FSMContext):
    user_sign = callback.data.replace("zodiac_", "")
    await state.update_data(your_sign=user_sign)
    await callback.message.answer("🧿 Тепер обери знак партнера або людини, з якою хочеш перевірити сумісність:",
                                  reply_markup=zodiac_keyboard)
    await state.set_state(ZodiacCompatibility.partner_sign)


@router.callback_query(StateFilter(ZodiacCompatibility.partner_sign))
async def choose_partner_sign(callback: CallbackQuery, state: FSMContext):
    partner_sign = callback.data.replace("zodiac_", "")
    data = await state.get_data()
    your_sign = data["your_sign"]
    def get_mistral_response(sign1, sign2):
        from mistralai import Mistral
        api_key = "EmUgU7MMinB1NoH1XEu3dm1B8xnYvAOL"
        model = "mistral-large-latest"
        client = Mistral(api_key=api_key)
        prompt = f"""
Ти — мудрий астролог, що бачить глибокі взаємозв’язки між знаками зодіаку. Я даю тобі два знаки.
Твоє завдання:
1. Опиши, яку енергію створює їхній союз (можна алегорією: вогонь і лід, туман і вітер тощо)
2. Назви сильні й слабкі сторони цього поєднання (чесно, але красиво)
3. Заверш — коротким поетичним афоризмом або пророцтвом
Пиши українською. Будь емоційним, мудрим, але конкретним. Не придумуй нових знаків.
Ось знаки: {sign1} і {sign2}
        """
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    answer = await asyncio.to_thread(get_mistral_response, your_sign, partner_sign)
    await callback.message.answer(f"🔮 Відповідь Астрологині:\n\n{answer}")
    await callback.message.answer(
        "✨ Хочеш дізнатися глибшу сумісність — *сумісність душ*?\nПройди короткий архетипний тест:",
        reply_markup=archetype_test_kb,
        parse_mode="Markdown"
    )
    await state.clear()


@router.callback_query(F.data == "start_archetype_test")
async def ask_who_first(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer_photo(photo="AgACAgIAAxkBAAIFU2gUoTefcGZ0po2z4W6FC_HcMNBvAAJB"
                                              "-jEbbpihSAqF0HHBk3poAQADAgADeQADNgQ")
    await callback.message.answer("✨ Для кого проходимо тест спочатку?", reply_markup=architips_start_kb)
@router.callback_query(F.data.in_(["person_you", "person_partner"]))
async def start_test(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ArchetypeTest.q1)
    await state.update_data(person=callback.data)
    await callback.message.answer("❓ Як ти зазвичай реагуєш на труднощі?", reply_markup=architips_q1_kb)


@router.callback_query(StateFilter(ArchetypeTest.q1, ArchetypeTest.q2, ArchetypeTest.q3, ArchetypeTest.q4, ArchetypeTest.q5))
async def next_question(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    current_state = await state.get_state()
    answers = state_data.get("answers", [])
    answers.append(callback.data)
    await state.update_data(answers=answers)

    if current_state == ArchetypeTest.q1.state:
        await state.set_state(ArchetypeTest.q2)
        await callback.message.answer("❓ Що ти найбільше цінуєш у житті?", reply_markup=architips_q2_kb)

    elif current_state == ArchetypeTest.q2.state:
        await state.set_state(ArchetypeTest.q3)
        await callback.message.answer("❓ У тебе вільний день. Що робиш?", reply_markup=architips_q3_kb)

    elif current_state == ArchetypeTest.q3.state:
        await state.set_state(ArchetypeTest.q4)
        await callback.message.answer("❓ Який твій головний страх?", reply_markup=architips_q4_kb)

    elif current_state == ArchetypeTest.q4.state:
        await state.set_state(ArchetypeTest.q5)
        await callback.message.answer("❓ Як ти сприймаєш інших людей?", reply_markup=architips_q5_kb)

    elif current_state == ArchetypeTest.q5.state:
        most_common = Counter(answers).most_common(1)[0][0]
        person = state_data["person"]
        await state.update_data(**{person: most_common}, answers=[])

        if person == "person_you":
            await callback.message.answer("✅ Твій архетип визначено. Тепер пройди тест для партнера:", reply_markup=architips_partner_kb)
        else:
            data = await state.get_data()
            you = data.get("person_you")
            partner = data.get("person_partner")
            await callback.message.answer(f"🔮 Ти — {you}, партнер — {partner}\nСкоро я скажу, як взаємодіють ваші душі...")
            await state.clear()

            def get_mistral_response(you, partner):
                from mistralai import Mistral
                api_key = "EmUgU7MMinB1NoH1XEu3dm1B8xnYvAOL"
                model = "mistral-large-latest"
                client = Mistral(api_key=api_key)

                prompt = f"""
            Уяви, що ти — мудра душа, яка відчуває енергетику стосунків. Я назву тобі два архетипи особистостей. 
            Опиши їхню сумісність як справжня людина — щиро, глибоко, без переліків, одним текстом. 

            Розкажи, що між ними відчувається: притягнення, напруга, гармонія чи виклик. 
            Якщо є світло — покажи його. Якщо є тінь — не ховай. 

            Заверш думкою, яка залишиться в серці.

            Ось архетипи: {you} і {partner}
                            """
                response = client.chat.complete(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content

            answer = await asyncio.to_thread(get_mistral_response, you, partner)

            await callback.message.answer(f"🔮 Відповідь Астрологині:\n\n{answer}")


@router.message(F.text == "💤 Мені наснився сон – 10🃏")
async def start_dream(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not spend_cards_if_possible(user_id, 10):
        await message.answer("❌ У вас недостатньо карт! Потрібно 10 🃏.")
        return
    await message.answer_photo(
        photo="AgACAgIAAxkBAAIFqGgUucN9O7420zzAQTsBq8oHsc_CAAKk9DEbbpipSLh5NoLFH6U6AQADAgADeQADNgQ",
        caption="🌙 Напиши свій сон одним повідомленням. Я відчую, що в ньому заховано..."
    )
    await state.set_state(DreamState.waiting_for_dream)


@router.message(StateFilter(DreamState.waiting_for_dream))
async def interpret_dream(message: Message, state: FSMContext):
    person_dream = message.text
    def get_mistral_response(person_dream):
        from mistralai import Mistral
        api_key = "EmUgU7MMinB1NoH1XEu3dm1B8xnYvAOL"
        model = "mistral-large-latest"
        client = Mistral(api_key=api_key)
        prompt = f"""
Уяви, що до тебе звернулась людина й поділилась своїм сном. Не як аналітик, а як чутлива душа, 
ти намагаєшся відчути, що за цим сном стоїть насправді.
Прочитай його і скажи — що цей сон може означати? Як він пов’язаний з її станом, страхами, бажаннями? 
Не розбирай символи окремо — говори суцільно, як одне бачення, що залишає після себе емоцію й сенс.
Пиши так, ніби розповідаєш їй особисто. Без списків. Без «це означає…». Просто — що це за історія 
і яка її тінь, світло чи поклик.
Заверш однією сильною, короткою фразою — як післямовою, що залишиться в тиші.
Ось сон: {person_dream}
        """
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    answer = await asyncio.to_thread(get_mistral_response, person_dream)
    await message.answer(f"🔮 Тлумачення сну:\n{answer}")
    await state.clear()


@router.message(F.photo)
async def get_photo_id(message: Message):
    photo = message.photo[-1]
    await message.answer(f"file_id: {photo.file_id}")


@router.message(F.text == "🌙 Астральна звичка дня – 3🃏")
async def astroal_habit(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not spend_cards_if_possible(user_id, 3):
        await message.answer("❌ У вас недостатньо карт! Потрібно 3 🃏.")
        return
    await message.answer("🌕 Твоя астральна звичка дня:")
    def get_mistral_response():
        api_key = "EmUgU7MMinB1NoH1XEu3dm1B8xnYvAOL"
        model = "mistral-large-latest"
        client = Mistral(api_key=api_key)
        prompt = """
Вигадай одну унікальну астральну звичку дня (до 20 слів). Вона має звучати магічно, 
дивно, але виконувано. Без пояснень. Без свічок.
Формат:
[текст]
        """
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    answer = await asyncio.to_thread(get_mistral_response)
    await message.answer(answer)
    await state.clear()


def generate_daily_horoscope(sign: str) -> str:
    api_key = "EmUgU7MMinB1NoH1XEu3dm1B8xnYvAOL"
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)
    prompt = f"""
Ти — астролог і поет. Напиши короткий (до 70 слів) персональний гороскоп для знаку зодіаку: {sign} на сьогодні.
Текст має бути теплим, мудрим і натхненним. Не повторюй шаблони. Не використовуй однакові речення.
Пиши українською. Не пиши “день буде складним” — заміни метафорою або м’яким образом.
    """
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


async def daily_broadcast(bot: Bot):
    db = sqlite3.connect("tviyastrogid.db")
    cur = db.cursor()
    cur.execute("SELECT id, zodiac_sign FROM users WHERE zodiac_sign IS NOT NULL")
    users = cur.fetchall()
    db.close()
    for user_id, sign in users:
        try:
            horoscope = await asyncio.to_thread(generate_daily_horoscope, sign)
            await bot.send_message(
                chat_id=user_id,
                text=f"🌟 Гороскоп для {sign}:\n\n{horoscope}",
                reply_markup=daily_bonus_kb
            )
        except Exception as e:
            print(f"❌ Не надіслано {user_id}: {e}")


@router.callback_query(F.data == "daily_bonus")
async def daily_bonus_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    amount = random.choice([10, 15, 20, 25, 30])
    db = sqlite3.connect("tviyastrogid.db")
    cur = db.cursor()
    cur.execute("SELECT cards FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if row is None:
        await callback.message.answer("⚠️ Помилка: користувача не знайдено.")
        db.close()
        return
    current_cards = int(row[0]) if row[0] else 0
    cur.execute("UPDATE users SET cards = ? WHERE id = ?", (current_cards + amount, user_id))
    db.commit()
    db.close()

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass
    await callback.message.answer(f"🎉 Ти отримав +{amount} 🃏. Завітай завтра ще!")


@router.message(F.text == "🌀 У мене проблема – 10🃏")
async def astroal_habit(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not spend_cards_if_possible(user_id, 10):
        await message.answer("❌ У вас недостатньо карт! Потрібно 3 🃏.")
        return
    await message.answer("💬 Напиши свою ситуацію в одному повідомленні. Астрологиня відчує суть і дасть пораду.")
    await state.set_state(ProblemState.waiting_for_problem)


@router.message(StateFilter(ProblemState.waiting_for_problem))
async def interpret_dream(message: Message, state: FSMContext):
    person_problem = message.text
    def get_mistral_response(person_dream):
        from mistralai import Mistral
        api_key = "EmUgU7MMinB1NoH1XEu3dm1B8xnYvAOL"
        model = "mistral-large-latest"
        client = Mistral(api_key=api_key)
        prompt = f"""
        Ти — мудра Астрологиня, яка прожила багато життів і бачила сотні людських історій. Людина поділилась з тобою своєю проблемою:
        "{person_problem}"
        Не намагайся її втішити. Не пиши «все буде добре» чи «тримайся». Ти не даєш ілюзій — ти даєш ясність.  
        Твоя порада має нести спокій, а не емоції. Вона має повернути людину до себе, показати, що вона може змінити, що прийняти, а що просто відпустити.

        Пиши українською. Говори спокійно, просто, але мудро — як та, хто бачить усе глибше, ніж інші.  
        Не аналізуй проблему — побач у ній суть. І назви її.

        **Заверш обов’язково однією короткою фразою**, яка звучить як істина:  
        це може бути стоїчний афоризм, філософський висновок або внутрішній орієнтир.  
        Не пояснюй його — просто скажи.  
        Це має бути фраза, яка залишиться з людиною в тиші.
        """
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    answer = await asyncio.to_thread(get_mistral_response, person_problem)
    await message.answer(f"{answer}")
    await state.clear()






from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.markdown import hbold

@router.message(CommandStart(deep_link=True))
async def cmd_start_with_ref(message: Message, command: CommandObject, state: FSMContext):
    user_id = message.from_user.id
    inviter_id = int(command.args) if command.args and command.args.isdigit() else None

    db = sqlite3.connect("tviyastrogid.db")
    cur = db.cursor()

    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_exists = cur.fetchone()

    if not user_exists:
        cur.execute("INSERT INTO users (id, cards, invited_by) VALUES (?, ?, ?)", (user_id, 0, inviter_id))


        if inviter_id and inviter_id != user_id:
            cur.execute("SELECT cards FROM users WHERE id = ?", (inviter_id,))
            inviter = cur.fetchone()
            if inviter:
                cur.execute("UPDATE users SET cards = ? WHERE id = ?", (inviter[0] + 25, inviter_id))

    db.commit()
    db.close()


    await message.answer_photo(
        photo="AgACAgIAAxkBAAIFRGgUnhBhg0pqMszswBANaZYpsCuOAAIb-jEbbpihSGn8T3t5wVOcAQADAgADeQADNgQ",
        caption="Привіт, це твій персональний АстроГід 🌌\nЯ допоможу тобі дізнатися свою долю."
    )
    zodiac_msg = await message.answer("Обери свій знак зодіаку!", reply_markup=zodiac_keyboard)
    await state.update_data(zodiac_msg_id=zodiac_msg.message_id)
    await state.set_state(regist.zodiak_callback1)


@router.message(F.text == "🤝 Запросити друга")
async def invite_friend(message: Message):
    bot_username = "tviyAstrogid_bot"
    ref_link = f"https://t.me/{bot_username}?start={message.from_user.id}"
    await message.answer(
        f"💌 Надішли це посилання другу:\n\n{hbold(ref_link)}\n\n"
        "🃏 Якщо він запустить бота — ти отримаєш 25 карт!"
    )

@router.message(F.text == "🛒Мої карти")
async def invite_friend(message: Message):
    user_id = message.from_user.id

    db = sqlite3.connect("tviyastrogid.db")
    cur = db.cursor()
    cur.execute("SELECT cards FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    db.close()

    cards = int(row[0]) if row and row[0] else 0

    await message.answer(f"💳 Баланс: {cards} 🃏")
#reply_markup=buy_cards_kb