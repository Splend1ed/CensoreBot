import datetime
import config
from telebot import telebot, types
from bad_words import foul_words
from cs.dateutils import datetime2unixtime

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text.title() == '🔙\nМеню')
def menu(message: types.Message):
    start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_keyboard.row('💬\nИнформация', '💸\nДонат', '✍\nДобавить слова')
    bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup=start_keyboard)


@bot.message_handler(func=lambda message: message.text.title() == '💬\nИнформация')
def info(message: types.Message):
    keyboard_info = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_info.row('🔙\nМеню')
    bot.send_message(message.chat.id, text='''
Примечание:
- Бот работает только в приватных группах!
Что бы я начал свою роботу тебе нужно:
- Добавить меня в группу.
- Дать права администратора.
Иии... Готово!    
Теперь я буду удалять сообщение в которых есть нецензурное выражение!
Если в пользователя будет замечено 5 сообщений с нецензурными выражениями его права будут ограничены на 10 минут
Но я пока что не идеален, если ты нашел слово 
которое я не удалил, ты можешь добавить его в главном меню.
Если вы заметили баг напишите письмо на korotenko.qndroid@gmail.com
    ''', reply_markup=keyboard_info)


@bot.message_handler(func=lambda message: message.text.title() == '💸\nДонат')
def donate(message: types.Message):
    keyboard_donate = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_donate.row('🔙\nМеню')
    bot.send_message(chat_id=message.chat.id, text='''
Если желаете поддержать автора 💶:
5167 9855 2007 1283''', reply_markup=keyboard_donate)


@bot.message_handler(func=lambda message: message.text == '✍\nДобавить слова')
def add_words_info(message: types.Message):
    keyboard_add_words = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_add_words.row('🔙\nМеню')
    bot.send_message(chat_id=message.chat.id, text='Напишите слова которые, хотите добавить в список:\n'
                                                   '"Меню" - чтобы вернуться назад',
                     reply_markup=keyboard_add_words)
    bot.register_next_step_handler(message, add_words)


def add_words(message: types.Message):
    if message.text.title() != '🔙\nМеню':
        check_words = [message.text]
        bot.send_message(chat_id=message.chat.id, text=f'После проверки эти слова будут добавлены в список:'
                                                       f'"{message.text}"')

        if len(check_words) > 0:
            bot.send_message(config.admin_id, text=f'''
Пользователь {message.from_user.full_name},
id:{message.from_user.id}
Добавил такие слова на проверку:{check_words}''')
    else:
        start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_keyboard.row('💬\nИнформация', '💸\nДонат', '✍\nДобавить слова')
        bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup=start_keyboard)


def return_filtered_msg(message: str, iter_index=0):
    if iter_index != len(foul_words):
        words = foul_words[iter_index]
        if words in message.lower():
            return return_filtered_msg(message.replace(words, '***').lower(), iter_index + 1)
        else:
            return return_filtered_msg(message.replace(words, '***').lower(), iter_index + 1)
    else:
        return message


users_id = []


@bot.message_handler(content_types=['text'])
def filter_message(message: types.Message):
    new_msg = return_filtered_msg(message.text)
    for w in foul_words:
        if w in message.text.lower():
            if message.from_user.id != int(config.admin_id):

                users_id.append(message.from_user.id)
                bot.delete_message(chat_id=message.chat.id, message_id=message.id)
                bot.send_message(chat_id=message.chat.id, text=f'{message.from_user.full_name} хотел написать:\n'
                                                               f'"{new_msg}"')
                foul_counter = dict((i, users_id.count(i)) for i in users_id)
                print(f"dict before delete - {foul_counter}")
                copy_foul_counter = foul_counter.copy()
                for id_, count in copy_foul_counter.items():
                    if count >= 5:
                        del foul_counter[id_]
                        print(f"dict after delete - {foul_counter}")
                        mute_time = datetime2unixtime(datetime.datetime.today()) - 10200
                        bot.send_message(message.chat.id, f'{message.from_user.full_name},'
                                                          f'использует плохие слова, он(она) не сможет пользоваться '
                                                          f'чатом 10 минут')
                        bot.restrict_chat_member(chat_id=message.chat.id,
                                                 user_id=id_,
                                                 can_send_messages=False,
                                                 can_pin_messages=False,
                                                 can_send_media_messages=False,
                                                 can_send_other_messages=False,
                                                 can_send_polls=False,
                                                 can_invite_users=False,
                                                 can_change_info=False,
                                                 can_add_web_page_previews=False,
                                                 until_date=mute_time)
                        continue
                    else:
                        pass
            else:
                bot.delete_message(chat_id=message.chat.id, message_id=message.id)
                bot.send_message(chat_id=message.chat.id, text=f'{message.from_user.full_name} хотел написать:\n'
                                                               f'"{new_msg}"')


bot.polling(none_stop=True)
