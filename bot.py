import os
import threading
import telebot
from telebot import types
import subprocess
import style_transfer as st_t
import time


def time_to_send(user): #отслеживание появления файла из внешней нейросети
    timer[user] = time.time()
    while True:
        if (time.time() - timer[user]) >= 15:
            if os.path.exists(str(user)+"image3.jpg"):
                with open(str(user)+"image3.jpg", 'rb') as test_image:
                    bot.send_photo(user, test_image, caption='Представляю Вам своё творение. Понадобились недюжинные усилия, но я справился')
                    question_one(user)
                    break
            else:
                timer[user] = time.time()

def delete_user(user, n): #удаление отработанных файлов
    if n == 1: #удаляем начиная заново
        if user in im_name_1:
            im_name_1.pop(user) 
    if (n == 1) or (n == 2): #удаляем начиная заново или при смене стиля
        if user in im_name_2:    
            im_name_2.pop(user)
        if user in im_name_3:    
            im_name_3.pop(user) 

def delete_photo(user, n): #удаление отработанных файлов
    if n == 1: #удаляем начиная заново
        if os.path.exists(str(user)+"image1.jpg"):
            os.remove(str(user)+"image1.jpg") 
    if (n == 1) or (n == 2): #удаляем начиная заново или при смене стиля
        if os.path.exists(str(user)+"image2.jpg"):    
            os.remove(str(user)+"image2.jpg")
        if os.path.exists(str(user)+"image3.jpg"):    
            os.remove(str(user)+"image3.jpg")


bot = telebot.TeleBot('token') #адрес бота
im_name_1 = {} #картинка для обработки
im_name_2 = {} #картинки со стилем
im_name_3 = {} #результат
timer = {} #таймер

def help(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Приветствую! Я талантлвый художник в изгнании.\
    Я отказался от известности, но тоскую по своему ремеслу, и не хочу, чтобы мой прекрасный талант прозябал\
    в безделии и унынии.')
    bot.send_message(user_id, 'Да, я подделывал работы других мастеров, известнейших художников.\
    Но с каким упоением и ни с чем несравнимой радостью я это делал!')
    bot.send_message(user_id, 'Вот пришлите мне совершенно любую картинку, которую хотите изменить.\
    А вслед за нею картину того художника, чей стиль я должен подделать. Уверяю, вы будете удивлены.')
    
    
@bot.message_handler(func=lambda message: True, content_types=['text'])
def send_text(message):
    user_id = message.chat.id
    if ('привет' or 'здравствуй') in message.text.lower():
        bot.send_message(user_id, 'Приветствую, пришлите мне картину, которую вы хотите изменить')       
    elif ('пока') in message.text.lower():
        bot.send_message(user_id, 'Наши встречи очень много для меня значат. Прощайте.....')
        delete_photo(user_id, 1)
        delete_user(user_id, 1)
        #bot.stop_polling()
    elif ('сотри' or 'удали') in message.text.lower():
        delete_photo(user_id, 1)
        delete_user(user_id, 1)
        bot.send_message(user_id, 'Все следы уничтожены')
    elif ('как дела'or 'как ты') in message.text.lower():
        bot.send_message(user_id, 'Кто-то может сказать, что я счастливчик, но  тем не менее, всё могло быть куда лучше...')
    elif ('вопрос' or 'проблема') in message.text.lower():
        with open('QA.txt', 'a') as bot_feedback:
            bot_feedback.write(str(user_id) + ' ' + message.text + '\n')
        bot.send_message(user_id, 'Отлично, я положил вашу записку в странное приспособление, оставленное  высшими силами.\
        Кто знает, что может произойти?')
    else:
        bot.send_message(user_id, 'Всё-таки, я достаточно занятой человек, чтобы отвечать на вопросы не по моей работе.\
        Но если написать в сообщении слово "вопрос", то силы, что несоизмеримо выше меня, услышат вас\
        А ещё можно написать /help')


@bot.message_handler(func=lambda message: True, content_types=['photo'])
def photo(message):
    user_id = message.chat.id
    fileID = message.photo[-1].file_id
    #если пользователь ещё не отсылал картинок, записываем адрес первой картинки
    if user_id not in im_name_1:
        im_name_1[user_id] = message.photo[-1].file_id       
        bot.send_message(message.chat.id, 'У вас отличный вкус!\
        А сейчас пришлите мне картину того художника, чей стиль я должен подделать')
    else:
    	#если пользователь что-то отослал, записываем адрес второй картинки
        im_name_2[user_id] = message.photo[-1].file_id 
        #хендлер для выбора способа обработки
        chose_one(user_id)

@bot.callback_query_handler(func=lambda call: True)      
def user_answer(call):
    user = call.message.chat.id
    if ((call.data == "0") or (call.data =="1")):
        delete_or_no(user, call.data)
    else:
        convert_image(user, call.data)
    
def question_one(user):
    if user in im_name_3:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Изменить", callback_data= "0"))
        keyboard.add(types.InlineKeyboardButton(text="Следующая картина", callback_data="1"))
        bot.send_message(user, 'Хотите изменить стилистику, либо изменить следующую картину?', reply_markup=keyboard)

def chose_one(user):
    if user not in im_name_3:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Хочу быстрее", callback_data= "fst"))
        keyboard.add(types.InlineKeyboardButton(text="Могу и подождать", callback_data="slw"))
        bot.send_message(user, 'Хотите результат побыстрее, либо дадите время на детальную проработку?', reply_markup=keyboard)

def convert_image(user, answer):
    if answer == "fst": #быстрый алгоритм
        if len(im_name_1[user]) <= 150: #при повторном запуске в ячейке может быть картинка, а не id файла
            im_name_1[user] = bot.download_file(bot.get_file(im_name_1[user]).file_path)
        im_name_2[user] = bot.download_file(bot.get_file(im_name_2[user]).file_path)
        #запускаем через thread для обеспецения асинхронности
        threading.Thread(target=st_t.photo_connect(im_name_1[user], im_name_2[user], user, im_name_3)).start()
        bot.send_photo(user, im_name_3[user]\
                           , caption='Представляю Вам своё творение. Понадобились недюжинные усилия, но я справился')
        question_one(user)
    elif answer == "slw": #медленный но каественный алгоритм
        with open(str(user)+"image1.jpg", 'wb') as new_file:
            if len(im_name_1[user]) <= 150:
                #при повторном запуске в ячейке может быть картинка, а не id файла
                new_file.write(bot.download_file(bot.get_file(im_name_1[user]).file_path))
            else:
                new_file.write(im_name_1[user])
        with open(str(user)+"image2.jpg", 'wb') as new_file:
            new_file.write(bot.download_file(bot.get_file(im_name_2[user]).file_path))
        im_name_3[user] = str(user)+"image3.jpg"
        bot.send_message(user, 'Тогда я погружаюсь в творческий процесс, на несколько  минут, обычно от двух до пяти.')
        #команда для запуска нейросети. Для снижения нагрузки на память использует cudnn, оптимизатор lbfgs\
        #выдаёт наилучший результат по качеству, хоть и проигрывает adam-у в скорости (порядка 60 секунд)  
        command = "python neural_style.py -style_image {} -content_image {} -output_image {}\
         -backend cudnn -optimizer lbfgs".format(str(user)+"image2.jpg", str(user)+"image1.jpg", im_name_3[user])
        p = subprocess.Popen(command) #запускаем сторонний процесс, может одновременно выполняться для нескольких пользователей
        threading.Thread(target=time_to_send(user)).start() #отслеживаем появление результата в папке
        
def delete_or_no(user, answer): 
    if answer == "1":
        delete_photo(user, 1) #удаляем все файлы
        delete_user(user, 1) #очищаем память
        bot.send_message(user, 'Пришлите мне картину, которую вы хотите изменить')
    elif answer == "0":
        delete_user(user, 2) #удаляем всё кроме первого файла
        delete_photo(user, 2) #очищаем память кроме первого файла
        bot.send_message(user, 'Пришлите мне иную картину для вдохновения')            

        
#т.к. возникли проблемы с запуском webhook на локальной машине,
# а времени на веб-сервер из-за загруженности не хватило, обход ошибок телеги выполняем при помощи try/except
while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except: 
        time.sleep(5)
"""neural_networks:
    fast: TensorFlow tutorial https://www.tensorflow.org/tutorials/generative/style_transfer
    qualitative: Johnson, Justin, https://github.com/jcjohnson/neural-style
    bot: c-stone studio, Gleb Yakimovich, https://github.com/kolovrado"""




