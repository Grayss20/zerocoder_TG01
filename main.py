import random
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import TOKEN, OPENWEATHERMAP_API_KEY  # Store your OpenWeatherMap API key here
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import aiohttp

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Define a state class for the weather FSM
class WeatherState(StatesGroup):
    waiting_for_city = State()


@dp.message(Command("weather"))
async def weather(message: Message, state: FSMContext):
    await message.answer("Погода в каком городе вас интересует?")
    await state.set_state(WeatherState.waiting_for_city)  # Set state to wait for city name


@dp.message(WeatherState.waiting_for_city)
async def get_city_name(message: Message, state: FSMContext):
    city = message.text  # Get the city name provided by the user
    await fetch_weather(city, message)
    await state.clear()  # Clear state after handling the city input


async def fetch_weather(city: str, message: Message):
    """Fetch weather data from OpenWeatherMap API and send it to the user."""
    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=ru"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                city_name = data['name']
                weather_description = data['weather'][0]['description']
                temperature = data['main']['temp']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']

                # Send weather information back to the user
                weather_report = (f"Погода в {city_name}:\n"
                                  f"Описание: {weather_description.capitalize()}\n"
                                  f"Температура: {temperature}°C\n"
                                  f"Влажность: {humidity}%\n"
                                  f"Скорость ветра: {wind_speed} м/с")
                await message.answer(weather_report)
            else:
                await message.answer(
                    "Не удалось получить погоду для этого города. Пожалуйста, проверьте название города и попробуйте еще раз.")


@dp.message(Command("photo"))
async def photo(message: Message):
    photo_list = [
        'https://t3.ftcdn.net/jpg/09/41/44/72/360_F_941447278_Bh1lLtR1kaVP3lcNh11MDNrCBRcG3bu7.jpg',
        'https://media.istockphoto.com/id/93210320/photo/young-siamese-sable-ferret-kit.jpg?s=612x612&w=0&k=20&c=8-_kkouFkllyrsexTFo82su-GbrO_V3z_LbL7MX5hTU=',
        'https://media.gettyimages.com/id/97086548/photo/pet-ferret.jpg?s=612x612&w=gi&k=20&c=xp7Hs15_YVMeuRIJhbeB-09X7Hv85EIGQDWdknTu92M='
    ]
    rand_photo = random.choice(photo_list)
    await message.answer_photo(photo=rand_photo, caption="Вот такая фотка")


@dp.message(F.photo)
async def react_photo(message: Message):
    list = ['Ого, какая фотка!', 'Непонятно, что это такое', 'Не отправляй мне такое больше']
    rand_answ = random.choice(list)
    await message.answer(rand_answ)


@dp.message(F.text == "Что такое ИИ?")
async def aitext(message: Message):
    await message.answer(
        "Искусственный интеллект — это свойство искусственных интеллектуальных систем выполнять творческие функции, которые традиционно считаются прерогативой человека; наука и технология создания интеллектуальных машин, особенно интеллектуальных компьютерных программ")


@dp.message(Command("help"))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды: \n /start \n /help \n /weather \n /photo")


@dp.message(CommandStart())
async def start(message: Message):
    await message.reply("Hello! I am a bot")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
