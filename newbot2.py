from settings import TOKEN

import telebot
from telebot import types

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from transliterate import translit
from langdetect import detect


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Найти песню')
    markup.add(btn1)
    bot.send_message(message.from_user.id, 'Я короче знаешь что умею?' '\n' 'Я могу устроить тебе караоке за твои нюдисы)', reply_markup=markup)
    bot.send_message(message.from_user.id, 'Внимание! Бот находится на ранней стадии разработки,' '\n' 
                                           'и поддерживает авторов и названия песен, только на английском языке!')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Найти песню" or message.text == 'Искать еще':
        keyboard = types.ReplyKeyboardMarkup()
        sent = bot.send_message(message.from_user.id, "Пришли исполнителя и название песни (artist - song)", reply_markup=keyboard)
        bot.register_next_step_handler(sent, review)


def review(message):
    try:
        def transl(name):
            slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
                      'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
                      'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
                      'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
                      'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
                      'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
                      'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
                      'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
                      'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
                      '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '=': '', '+': '',
                      ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
                      '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
                      'Є': 'e', '—': ''}

            for key in slovar:
                name = name.replace(key, slovar[key])

            return name

        def make_data():
            bot.send_message(message.from_user.id, text='Подождите несколько секунд..')
            message_to_save = message.text
            artist = message_to_save[0: message_to_save.find('-')]
            song = message_to_save[message_to_save.find('-') + 1: len(message_to_save)]
            all_param = list()

            if artist[len(artist) - 1] == ' ':
                artist = artist[:-1]

            if song[0] == ' ':
                song = song[1:len(song)]

            if ' ' in artist:
                artist = artist.replace(' ', '-')
            if ' ' in song:
                song = song.replace(' ', '-')

            if 'я' or 'Я' in song:
                song = song.replace('я', 'ya')
                song = song.replace('Я', 'ya')

            if 'я' or 'Я' in artist:
                artist = artist.replace('я', 'ya')
                artist = artist.replace('Я', 'ya')

            if detect(artist) == 'ru' or detect(song) == 'ru':
                artist = transl(artist)
                song = transl(song)

            link_to_text = f'https://txtsong.ru/{artist}/{artist}-{song}/'
            link_to_load = f'https://mp3store.net/get-music/{artist}-{song}/'
            all_param.append(artist)
            all_param.append(song)
            all_param.append(link_to_text)
            all_param.append(link_to_load)
            print(link_to_load)
            print(link_to_text)
            return all_param

        def parse_text(link1):
            r = requests.get(link1)
            if r.status_code == 200:
                bot.send_message(message.from_user.id, text='Ищу текст.. 📃📑')
            soup = BeautifulSoup(r.text, 'html.parser')
            quotes = soup.find(class_='the_content')
            data = ''
            data = data + quotes.get_text(separator='\n')

            data = data.splitlines()
            new_res = list(filter(lambda a: a != '', data))
            main_line = ''
            for elem in new_res:
                main_line += elem + '\n'
            return main_line

        def load_mp3(link, singer, composition):
            r = requests.get(link, headers={'User-Agent': UserAgent().chrome})
            if r.status_code == 200:
                bot.send_message(message.from_user.id, text='Загружаю вам песню.. 🎶🎵')
            soup = BeautifulSoup(r.text, 'html.parser')
            quotes = soup.find(class_="sound-download").find_all('a')
            url_to_file = quotes[0].get('href')
            res = requests.get('https://mp3store.net/' + url_to_file, headers={'User-Agent': UserAgent().chrome})
            path_to_file = fr'C:\Users\79149\PycharmProjects\bot\data\{singer}_{composition}.mp3'
            with open(path_to_file, 'wb') as f:
                f.write(res.content)
            return path_to_file

        full_data = make_data()
        text_song = parse_text(full_data[2])
        audio_file = load_mp3(full_data[3], full_data[0], full_data[1])
        audio = open(audio_file, 'rb')
        bot.send_audio(message.chat.id, audio)
        audio.close()

        if len(text_song) > 4095:
            for x in range(0, len(text_song), 4095):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn2 = types.KeyboardButton('Искать еще')
                markup.add(btn2)
                bot.send_message(message.from_user.id, text=text_song[x:x + 4095], reply_markup=markup)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn2 = types.KeyboardButton('Искать еще')
            markup.add(btn2)
            bot.send_message(message.from_user.id, text=text_song, reply_markup=markup)

    except AttributeError:
        bot.send_message(message.from_user.id, text='Ой, я такой песни рот шатал, я ее не знаю 🤬' '\n' 'Пиши по новой 👬')
        sent = bot.send_message(message.from_user.id, text='Пришли исполнителя и название песни (artist - song)')
        bot.register_next_step_handler(sent, review)


bot.polling()



