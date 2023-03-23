import cx_Oracle
import pandas as pd
import telebot
from telebot import types, TeleBot
import csv
from main import main


host = '91.241.13.241:1521'
sid = 'ORCL'
dsn = host + '/' + sid
conn = cx_Oracle.connect(user='ODS_STUDY2', password='ODS_STUDY2', dsn=dsn)

# sql_query_geo = 'SELECT t.TRASH_ID, t.TRASH_GEO_X, t.TRASH_GEO_Y FROM ODS_STUDY2.TRASH t order by t.TRASH_ID'
# sql_query_geo_base = 'SELECT b.BASE_ID, b.BASE_GEO_X, b.BASE_GEO_Y  FROM ODS_STUDY2.BASE b WHERE b.base_id = 1000'
# sql_query_geo_ground = 'SELECT g.GROUND_ID, g.GROUND_GEO_X, g.GROUND_GEO_Y  FROM ODS_STUDY2.GROUND g '
#
# df_trash = pd.read_sql(sql_query_geo, conn)
# df_trash_base = pd.read_sql(sql_query_geo_base, conn)
# df_trash_qround = pd.read_sql(sql_query_geo_ground, conn)
#
# df_trash.to_csv('all_geo.csv')
# df_trash_base.to_csv('begin_geo.csv')
# df_trash_qround.to_csv('ground_geo.csv')
#
# id_trash_list = df_trash['TRASH_ID'].values.tolist()
# x_geo_list = df_trash['TRASH_GEO_X'].values.tolist()
# y_geo_list = df_trash['TRASH_GEO_Y'].values.tolist()
# d = {}
# for a in range(0, len(id_trash_list), 3):
#     dict_geo = {id_trash_list[a]: (x_geo_list[a], y_geo_list[a]),
#                 id_trash_list[a + 1]: (x_geo_list[a + 1], y_geo_list[a + 1]),
#                 id_trash_list[a + 2]: (x_geo_list[a + 2], y_geo_list[a + 2])}
#     print(dict_geo)
#     print(len(id_trash_list))
# dict_geo_base = {df_trash_base['BASE_ID'][0]: (df_trash_base['BASE_GEO_X'][0], df_trash_base['BASE_GEO_Y'][0])}
# print(dict_geo_base)
# dict_geo_ground = {
#     df_trash_qround['GROUND_ID'][0]: (df_trash_qround['GROUND_GEO_X'][0], df_trash_qround['GROUND_GEO_Y'][0])}
# print(dict_geo_ground)

# HILLS = {
#     "Vartiovuori": (60.448722, 22.276455),
#     "Kakolanmäki": (60.442719, 22.243017),
#     "Samppalinnanmäki": (60.446271, 22.267700),
#     "Yliopistonmäki": (60.454736, 22.284642),
#     "Korppolaismäki": (60.431133, 22.236316),
#     "Puolalanmäki": (60.453881, 22.261886),
#     "Kerttulinmäki": (60.449977, 22.284414)
# }

# USE_SAVED_DISTANCES = True
#
# START_HILL = dict_geo_base
# END_HILL = dict_geo_ground

# b=10


bot: TeleBot = telebot.TeleBot('5519156942:AAFZpKt5QvHZ7YHfgDxaJvP-Lp3lxw21Ou8')


@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Здравствуйте, введите вашу фамилию и имя по примеру: "Иванов Иван"')
    bot.register_next_step_handler(m, full_name_begin)


# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def bag(message):
    bot.send_message(message.chat.id, 'Я не понимаю, что вы ввели, пожалуйста введите команду /help')
    bot.register_next_step_handler(message, help_button)


@bot.message_handler(content_types=["text"])
def full_name_begin(msg):
    global full_name
    full_name = msg.text
    request_full_name = (f"""SELECT NAME FROM ODS_STUDY2.STAFF s WHERE NAME = '{str(full_name)}'""")
    check_full_name = pd.read_sql(request_full_name, conn)
    check_full_name.to_csv('check_full_name.csv')
    if check_full_name.size == 0:
        bot.send_message(msg.chat.id, 'Вы ввели неверную фамилилию или имя, попробуйте еще раз')
        bot.register_next_step_handler(msg, full_name_begin)

    elif full_name == check_full_name['NAME'][0]:
        # bot.send_message(msg.chat.id, 'Ваша фамилия и имя: ' + full_name)
        bot.send_message(msg.chat.id, 'Введите пароль, который вам выдали')
        bot.register_next_step_handler(msg, pasword_begin)
    else:
        bot.send_message(msg.chat.id, 'Не прошло проверку')
        bot.register_next_step_handler(msg, full_name_begin)


@bot.message_handler(content_types=["text"])
def pasword_begin(mes):
    global password
    password = mes.text
    request_full_name = (f"""SELECT STAFF_PASSWORD FROM ODS_STUDY2.STAFF s WHERE STAFF_PASSWORD = '{str(password)}'""")
    check_password = pd.read_sql(request_full_name, conn)
    check_password.to_csv('check_password.csv')
    if check_password.size == 0:
        bot.send_message(mes.chat.id, 'Вы ввели неверный пароль, попробуйте еще раз')
        bot.register_next_step_handler(mes, pasword_begin)
    elif password == check_password['STAFF_PASSWORD'][0]:
        # bot.send_message(mes.chat.id, 'Ваш пароль ' + password)
        bot.send_message(mes.chat.id, 'Введите команду /help')
        bot.register_next_step_handler(mes, help_button)
    else:
        bot.send_message(mes.chat.id, 'Не прошло проверку')
        bot.register_next_step_handler(get_staff_id())


def get_staff_id():
    check_flag_staff = (
        f"""SELECT s.user_acces_id FROM ODS_STUDY2.STAFF s WHERE NAME = '{str(full_name)}'AND STAFF_PASSWORD = '{str(password)}'""")
    df_flag_staff = pd.read_sql(check_flag_staff, conn)
    df_flag_staff.to_csv('check_flag_staff.csv')
    return df_flag_staff['STAFF_USER_ACCESS_ID'][0]


@bot.message_handler(commands=['help'])
def help_button(message):
    sql_update_tg_id = f"""UPDATE STAFF SET TELEGRAM_ID = '{str(message.from_user.id)}' WHERE NAME = '{str(full_name)}' AND STAFF_PASSWORD = '{str(password)}'"""
    with conn.cursor() as cursor:
        cursor.execute(sql_update_tg_id)
        conn.commit()
    # bot.send_message(message.chat.id, 'Зашел')
    check_flag_staff = (
        f"""SELECT USER_ACCES_ID FROM ODS_STUDY2.STAFF s WHERE NAME = '{str(full_name)}'AND STAFF_PASSWORD = '{str(password)}'""")
    df_flag_staff = pd.read_sql(check_flag_staff, conn)
    df_flag_staff.to_csv('check_flag_staff.csv')
    global role
    role = df_flag_staff['USER_ACCES_ID'][0]
    if role == 1:
        bot.send_message(message.chat.id, "Вы вошли под ролью водителя")
        bot.send_message(message.chat.id, "Введите какой маршрут вы хотите.\n"
                                          "Введите цифру от 1 до 29")
        bot.register_next_step_handler(message, choice_role_1)
    elif role == 2:
        bot.send_message(message.chat.id, "Вы вошли под ролью cотрудник отдела кадров")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,  row_width=1)
        item1 = types.KeyboardButton("Удалить сотрудника")
        item2 = types.KeyboardButton("Добавить нового сотрудника")
        item3 = types.KeyboardButton("Список сотрудников")
        item4 = types.KeyboardButton("Таблица пропусков")
        item5 = types.KeyboardButton("Остановить бота")
        markup.add(item1, item2, item3, item4, item5)
        bot.send_message(message.chat.id, 'Выберите, что вам нужно', reply_markup=markup)
        bot.register_next_step_handler(message, choice_role_2)
    elif role == 3:
        bot.send_message(message.chat.id, "Вы вошли под ролью оператор")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        item1 = types.KeyboardButton("Список всех мусорок")
        item2 = types.KeyboardButton("Номера сотрудников")
        item3 = types.KeyboardButton("Поставить пропуск")
        item4 = types.KeyboardButton("Остановить бота")
        markup.add(item1, item2, item3, item4)
        bot.send_message(message.chat.id, 'Выберите, что вам нужно', reply_markup=markup)
        bot.register_next_step_handler(message, choice_role_3)
    elif role == 4:
        bot.send_message(message.chat.id, "Вы вошли под ролью администратор")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        item1 = types.KeyboardButton("Список автотранспортных средств")
        item2 = types.KeyboardButton("Список сотрудников")
        item3 = types.KeyboardButton("Добавить запись в таблицу")
        item4 = types.KeyboardButton("Удалить запись из таблицы")
        item5 = types.KeyboardButton("Остановить бота")
        markup.add(item1, item2, item3, item4, item5)
        bot.send_message(message.chat.id, 'Выберите, что вам нужно', reply_markup=markup)
        bot.register_next_step_handler(message, choice_role_4)
    elif role == 5:
        bot.send_message(message.chat.id, "Вы вошли под ролью директор")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        item1 = types.KeyboardButton("Список автотранспортных средств")
        item2 = types.KeyboardButton("Список сотрудников")
        item3 = types.KeyboardButton("Остановить бота")
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, 'Выберите отчет', reply_markup=markup)
        bot.register_next_step_handler(message, choice_role_5)


@bot.message_handler(content_types=["text"])
def choice_role_1(mes):
    number_route = mes.text

    if int(number_route) <= 0 or int(number_route) >= 30:
        bot.send_message(mes.chat.id, 'Вы ввели неверный маршрут\n'
                         'Введите еще раз /help')
        bot.register_next_step_handler(mes, help_button)

    check_trash_flag = f"""SELECT TRASH_FLAG  FROM TRASH t WHERE REGION = {int(number_route)} """
    df_check_trash_flag = pd.read_sql(check_trash_flag, conn)
    df_check_trash_flag.to_csv('csv_check_trash_flag.csv')
    # bot.send_message(mes.chat.id, df_check_trash_flag['TRASH_FLAG'][0])
    if df_check_trash_flag['TRASH_FLAG'][0] and df_check_trash_flag['TRASH_FLAG'][1] and df_check_trash_flag['TRASH_FLAG'][2] == 1:
        sql_region_0 = 'SELECT DISTINCT REGION FROM ODS_STUDY2.TRASH t WHERE TRASH_FLAG = 0 ORDER BY REGION'
        df_sql_region_0 = pd.read_sql(sql_region_0, conn)
        df_sql_region_0.to_csv('csv_sql_region_0.csv')
        bot.send_message(mes.chat.id, 'Этот маршрут уже занят, выберите любой другой \n'
                                      'Вот один из свободных маршрутов:')
        if df_sql_region_0.size == 0:
            bot.send_message(mes.chat.id, 'Все мусорки были выгружены, работа закончилась')
        else:
            bot.send_message(mes.chat.id,  df_sql_region_0['REGION'][0])
            bot.send_message(mes.chat.id,  'Введите еще раз /help и выберите этот маршрут ')
            bot.register_next_step_handler(mes, help_button)
    else:
        bot.send_message(mes.chat.id, number_route)

        sql_query_geo_region = f"""SELECT t.TRASH_ID, t.TRASH_GEO_X, t.TRASH_GEO_Y FROM ODS_STUDY2.TRASH t where region = '{str(number_route)}' order by t.TRASH_ID  """
        df_trash_region = pd.read_sql(sql_query_geo_region, conn)
        df_trash_region.to_csv('region_geo.csv')

        sql_query_geo_base = """SELECT b.BASE_ID, b.BASE_GEO_X, b.BASE_GEO_Y  FROM ODS_STUDY2.BASE b WHERE b.base_id = 1000"""
        df_trash_base = pd.read_sql(sql_query_geo_base, conn)
        df_trash_base.to_csv('begin_geo.csv')

        sql_query_geo_ground = """SELECT g.GROUND_ID, g.GROUND_GEO_X, g.GROUND_GEO_Y  FROM ODS_STUDY2.GROUND g """
        df_trash_qround = pd.read_sql(sql_query_geo_ground, conn)
        df_trash_qround.to_csv('ground_geo.csv')

        id_trash_list = df_trash_region['TRASH_ID'].values.tolist()
        x_geo_list = df_trash_region['TRASH_GEO_X'].values.tolist()
        y_geo_list = df_trash_region['TRASH_GEO_Y'].values.tolist()
        a = 0
        dict_geo = {str(df_trash_base['BASE_ID'][0]): ( df_trash_base['BASE_GEO_Y'][0], df_trash_base['BASE_GEO_X'][0]),
                    str(id_trash_list[a]): (y_geo_list[a], x_geo_list[a]),
                    str(id_trash_list[a + 1]): (y_geo_list[a + 1], x_geo_list[a + 1]),
                    str(id_trash_list[a + 2]): (y_geo_list[a + 2], x_geo_list[a + 2]),
                    str(df_trash_qround['GROUND_ID'][0]): (df_trash_qround['GROUND_GEO_X'][0], df_trash_qround['GROUND_GEO_Y'][0])}
        bot.send_message(mes.chat.id, id_trash_list[a])
        bot.send_message(mes.chat.id, id_trash_list[a+1])
        bot.send_message(mes.chat.id, id_trash_list[a+2])
        bot.send_message(mes.chat.id, 'Идет построение маршрута... ')
        print(dict_geo)
        main(True, dict_geo, str(df_trash_base['BASE_ID'][0]), str(df_trash_qround['GROUND_ID'][0]))
        bot.send_message(mes.chat.id, 'Ваш маршрут под номером ' + number_route)
        html_doc = open('results/optimal_route.html', 'rb')
        bot.send_document(mes.from_user.id, html_doc)

        sql_update_flag_trash = f"""UPDATE TRASH SET TRASH_FLAG = '{(a + 1)}'  WHERE TRASH_ID ='{int(id_trash_list[a])}'"""
        with conn.cursor() as cursor:
            print('1')
            cursor.execute(sql_update_flag_trash)
            conn.commit()
        sql_update_flag_trash = f"""UPDATE TRASH SET TRASH_FLAG = '{(a + 1)}'  WHERE TRASH_ID ='{int(id_trash_list[a + 1])}'"""
        with conn.cursor() as cursor:
            print('1')
            cursor.execute(sql_update_flag_trash)
            conn.commit()
        sql_update_flag_trash = f"""UPDATE TRASH SET TRASH_FLAG = '{(a + 1)}'  WHERE TRASH_ID ='{int(id_trash_list[a + 2])}'"""
        with conn.cursor() as cursor:
            print('1')
            cursor.execute(sql_update_flag_trash)
            conn.commit()



@bot.message_handler(content_types=["text"])
def choice_role_2(message):
    if (message.text == 'Список сотрудников'):
        sql_query_staff = """SELECT * FROM ODS_STUDY2.STAFF s """
        df_staff_role_2 = pd.read_sql(sql_query_staff, conn)
        df_staff_role_2.to_excel('report_staff_role_2.xlsx', encoding='cp1251')
        csv_file_staff_role_2 = open('report_staff_role_2.xlsx', 'rb')
        bot.send_document(message.from_user.id, csv_file_staff_role_2)
        bot.register_next_step_handler(message, choice_role_2)
        bot.polling.abort = True
    elif (message.text == 'Добавить нового сотрудника'):
        bot.send_message(message.from_user.id,
                         'Напишите поочередно через запятую: айди, фамилию и имя, день рождение, роль, номер телефона, email, зарплату, пароль \n'
                         'Пример: "36, Николаев Алексей, 1993-12-21 , 1, 79659233211, dsjf@mail.ru, 35000, 12tab3"')
        bot.register_next_step_handler(message, add_staff)
        bot.polling.abort = True
    elif (message.text == 'Удалить сотрудника'):
        bot.send_message(message.chat.id, 'Напишите айди сотрудника, его фамилию и имя через запятую, чтобы удалить его из таблицы\n'
                                          'Пример: "37, Николаев Алексей"')
        bot.register_next_step_handler(message, del_staff)
        bot.polling.abort = True
    elif (message.text == 'Таблица пропусков'):
        sql_query_staff_abscence = """SELECT * FROM STAFF s JOIN ABSCENCE a ON a.ABSCENCE_ID = s.USER_ACCES_ID """
        df_staff_abscence = pd.read_sql(sql_query_staff_abscence, conn)
        df_staff_abscence.to_excel('report_staff_abscence.xlsx', encoding = 'cp1251')
        csv_file_staff_abscence = open('report_staff_abscence.xlsx', 'rb')
        bot.send_document(message.from_user.id, csv_file_staff_abscence)
        bot.register_next_step_handler(message, choice_role_2)
        bot.polling.abort = True

    elif (message.text == 'Остановить бота'):
        conn.close()
        bot.polling()
@bot.message_handler(content_types=["text"])
def del_staff(message):
    user_del_staff = message.text

    split_del_staff = user_del_staff.split(',')
    print(split_del_staff)
    staff_id_del = split_del_staff[0].strip()
    staff_name_del = split_del_staff[1].strip()

    sql_del_staff = f"""DELETE FROM ODS_STUDY2.staff where STAFF_ID = {staff_id_del} and NAME = '{staff_name_del}'"""
    with conn.cursor() as cursor:
        cursor.execute(sql_del_staff)
        conn.commit()
        bot.send_message(message.from_user.id, 'Успешно👍\n'
                                               '/help')
        bot.register_next_step_handler(message, help_button)

@bot.message_handler(content_types=["text"])
def add_staff(message):
    user_add_staff = message.text

    split_add_staff = user_add_staff.split(',')
    print(split_add_staff)
    staff_id = split_add_staff[0].strip()
    staff_name = split_add_staff[1].strip()
    staff_birth = split_add_staff[2].strip()
    staff_role = split_add_staff[3].strip()
    staff_phone = split_add_staff[4].strip()
    staff_email = split_add_staff[5].strip()
    staff_salary = split_add_staff[6].strip()
    staff_password = split_add_staff[7].strip()

    sql_insert_staff = f"""INSERT INTO ODS_STUDY2.STAFF 
(staff_id, NAME, BIRTH, USER_ACCES_ID, PHONE, EMAIL, SALARY, STAFF_DATE_CR, STAFF_ABSENCE_ID, STAFF_PASSWORD)
VALUES 
({staff_id}, '{staff_name}', to_date('{staff_birth}', 'YYYY-MM-DD'), {staff_role}, '{staff_phone}', '{staff_email}',
 {staff_salary}, CAST(sysdate as DATE), {int(1)}, '{staff_password}')"""
    with conn.cursor() as cursor:
        cursor.execute(sql_insert_staff)
        conn.commit()
        bot.send_message(message.from_user.id, 'Успешно👍\n'
                                               '/help')
        bot.register_next_step_handler(message, help_button)

@bot.message_handler(content_types=["text"])
def choice_role_3(message):
    if (message.text == 'Список всех мусорок'):
        sql_query_trash = """SELECT * FROM ODS_STUDY2.TRASH t """
        df_trash = pd.read_sql(sql_query_trash, conn)
        df_trash.to_excel('report_trash.xlsx', encoding = 'cp1251')
        csv_file_trash = open('report_trash.xlsx', 'rb')
        bot.send_document(message.from_user.id, csv_file_trash)
        bot.register_next_step_handler(message, choice_role_3)
        bot.polling.abort = True

    elif (message.text == "Поставить пропуск"):
        sql_query_abscence = """SELECT * FROM ABSCENCE a """
        df_abscence = pd.read_sql(sql_query_abscence, conn)
        df_abscence.to_excel('select_abscence.xlsx', encoding='cp1251')
        csv_file_abscence = open('select_abscence.xlsx', 'rb')
        bot.send_message(message.from_user.id, 'Посмотрите как правильно выставлять пропуска')
        bot.send_document(message.from_user.id, csv_file_abscence)
        bot.send_message(message.from_user.id, 'Напишите фамилию и имя, кому хотите поставить пропуск и введите ABSCENSE_ID \n'
                                                'Пример: "Иванов Иван, 3"')
        bot.register_next_step_handler(message, put_a_pass)
        bot.polling.abort = True
    elif (message.text == 'Номера сотрудников'):
        sql_query_staff_phone = """SELECT s.NAME, s.BIRTH, s.PHONE FROM ODS_STUDY2.STAFF s """
        df_staff_phone = pd.read_sql(sql_query_staff_phone, conn)
        df_staff_phone.to_excel('report_staff_phone.xlsx', encoding = 'cp1251')
        csv_file_staff_phone = open('report_staff_phone.xlsx', 'rb')
        bot.send_document(message.from_user.id, csv_file_staff_phone)
        bot.register_next_step_handler(message, choice_role_3)
        bot.polling.abort = True
    elif (message.text == 'Остановить бота'):
        conn.close()
        bot.polling()

@bot.message_handler(content_types=["text"])
def put_a_pass(message):
    user_update_staff = message.text

    split_abscence = user_update_staff.split(',')
    if len(split_abscence) == 2 and ' ' in split_abscence[0]:
        name_staff = split_abscence[0]
        abscence_in_staff = split_abscence[1]
        print(name_staff)
        print(abscence_in_staff)
        try:
            sql_update_staff_abscence = f"""UPDATE ODS_STUDY2.STAFF SET STAFF_ABSENCE_ID = '{int(abscence_in_staff)}' WHERE
            NAME = '{str(name_staff)}' """
            with conn.cursor() as cursor:
                cursor.execute(sql_update_staff_abscence)

        except:
            bot.send_message(message.from_user.id, 'Произошла ошибка, запрос не вывелся❌\n'
                                                   '/help')
            bot.register_next_step_handler(message, help_button)
        else:
            conn.commit()
            bot.send_message(message.from_user.id, 'Успешно👍\n'
                                                   '/help')
            bot.register_next_step_handler(message, help_button)
    else:
        bot.send_message(message.from_user.id, 'Вы ввели не по примеру\n'
                                                '/help')
        help_button(message)
                     #Если будет время дописать всплывающуюся кнопку back

@bot.message_handler(content_types=["text"])
def choice_role_4(message):
    if (message.text == 'Список автотранспортных средств'):
        sql_query_car = """SELECT * FROM ODS_STUDY2.CAR c """
        df_car = pd.read_sql(sql_query_car, conn)
        df_car.to_excel('report_car.xlsx', encoding = 'cp1251')
        csv_file_car = open('report_car.xlsx', 'rb')
        bot.send_document(message.from_user.id, csv_file_car)
        bot.register_next_step_handler(message, choice_role_4)
        bot.polling.abort = True
    elif (message.text == 'Список сотрудников'):
        sql_query_staff = """SELECT s.NAME, s.BIRTH, s.SALARY, s.PHONE FROM ODS_STUDY2.STAFF s """
        df_staff = pd.read_sql(sql_query_staff, conn)
        df_staff.to_excel('report_staff.xlsx', encoding = 'cp1251')
        csv_file_staff = open('report_staff.xlsx', 'rb')
        bot.send_document(message.from_user.id, csv_file_staff)
        bot.register_next_step_handler(message, choice_role_4)
        bot.polling.abort = True
    elif (message.text == 'Добавить запись в таблицу'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        item1 = types.KeyboardButton("Добавить сотрудника")
        item2 = types.KeyboardButton("Добавить автотранспортное средство")
        item3 = types.KeyboardButton("Добавить мусорку")
        item4 = types.KeyboardButton("Добавить полигон")
        item5 = types.KeyboardButton("Добавить базу")
        item6 = types.KeyboardButton("Назад")
        markup.add(item1, item2, item3, item4, item5, item6)
        bot.send_message(message.chat.id, 'Выберите, что вам нужно', reply_markup=markup)
        bot.register_next_step_handler(message, add_entry)
    elif (message.text == 'Удалить запись из таблицы'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        item1 = types.KeyboardButton("Удалить сотрудника")
        item2 = types.KeyboardButton("Удалить автотранспортное средство")
        item3 = types.KeyboardButton("Удалить мусорку")
        item4 = types.KeyboardButton("Удалить полигон")
        item5 = types.KeyboardButton("Удалить базу")
        item6 = types.KeyboardButton("Назад")
        markup.add(item1, item2, item3, item4, item5, item6)
        bot.send_message(message.chat.id, 'Выберите, что вам нужно', reply_markup=markup)
        bot.register_next_step_handler(message, delete_entry)
    elif (message.text == 'Остановить бота'):
        conn.close()
        bot.polling()

@bot.message_handler(content_types=["text"])
def add_entry(message):
    if (message.text == 'Добавить сотрудника'):
        bot.send_message(message.from_user.id, 'Напишите поочередно через знак "/": айди, фамилию и имя, день рождение, роль, номер телефона, email, зарплату, пароль \n'
                         'Пример: "36/ Николаев Алексей/ 1993-12-21/ 1/ 79659233211/ dsjf@mail.ru/ 35000/ 12tab3"')
        bot.register_next_step_handler(message, add_entry_staff)
    elif (message.text == 'Добавить автотранспортное средство'):
        bot.send_message(message.from_user.id, 'Напишите поочередно через знак "/": айди, модель, номер машины, дату тех обслуживания, объем машины, емкость бака, дата смены шин, вид топлива, расход топлива\n'
                         'Пример: "21/ ГАЗон NEXT Мусоровоз/ А390ВВ777/ 2022-12-01/ 9.3/ 105/ 2022-09-30/ дизель/ 22.6"')
        bot.register_next_step_handler(message, add_entry_car)
    elif (message.text == 'Добавить мусорку'):
        bot.send_message(message.from_user.id, 'Напишите поочередно через знак "/": адрес, гео х, гео у, айди, объем мусорки, время очистки мусорки, номер региона\n'
                         'Пример: "город Москва, 3-я Сокольническая улица, дом 4/ 37.685315/ 55.786779/ 88/ 3/ 10/ 30"')
        bot.register_next_step_handler(message, add_entry_trash)
    elif (message.text == 'Добавить полигон'):
        bot.send_message(message.from_user.id, 'Напишите поочередно через знак "/": айди, адрес, гео х, гео у, название полигона\n'
                         'Пример: "1001/ Московская обл, Мытищи, Коргашино, ул.Нагорная, 1/ 55.970297/ 37.751772/ Коргашино_1"')
        bot.register_next_step_handler(message, add_entry_ground)
    elif (message.text == 'Добавить базу'):
        bot.send_message(message.from_user.id, 'Напишите поочередно через знак "/": айди, название базы, адрес, гео х, гео у\n'
                         'Пример: "2/ Автопарк №2/ Москва, 2-я Боевская улица, 6Ас1/ 37.69127/ 55.790393"')
        bot.register_next_step_handler(message, add_entry_base)
    elif (message.text == 'Назад'):
         help_button(message)
@bot.message_handler(content_types=["text"])
def add_entry_base(message):
    add_base_entry = message.text
    split_add_base = add_base_entry.split('/')
    print(split_add_base)
    if len(split_add_base) == 5:
        base_id = split_add_base[0].strip()
        base_name = split_add_base[1].strip()
        base_address = split_add_base[2].strip()
        base_geo_x = split_add_base[3].strip()
        base_geo_y = split_add_base[4].strip()

        sql_insert_base = f"""INSERT INTO ODS_STUDY2.BASE  
                    (BASE_ID, BASE_NAME, BASE_ADRESS, BASE_GEO_X, BASE_GEO_Y, BASE_DATE_CR)
                    VALUES 
                    ({int(base_id)}, '{base_name}', '{(base_address)}', {float(base_geo_x)}, {float(base_geo_y)}, CAST(sysdate AS DATE) )"""
        with conn.cursor() as cursor:
            cursor.execute(sql_insert_base)
            conn.commit()
            bot.send_message(message.from_user.id, 'Успешно👍\n'
                                                   '/help')
            help_button(message)
    else:
        bot.send_message(message.from_user.id, 'Вы ввели не по примеру\n'
                                               '/help')
        help_button(message)

@bot.message_handler(content_types=["text"])
def add_entry_ground(message):
    add_ground_entry = message.text
    split_add_ground = add_ground_entry.split('/')
    print(split_add_ground)
    if len(split_add_ground) == 5:
        ground_id = split_add_ground[0].strip()
        ground_address = split_add_ground[1].strip()
        ground_geo_x = split_add_ground[2].strip()
        ground_geo_y = split_add_ground[3].strip()
        name_ground = split_add_ground[4].strip()

        sql_insert_ground = f"""INSERT INTO ODS_STUDY2.GROUND  
            (GROUND_ID, GROUND_ADRESS, GROUND_GEO_X, GROUND_GEO_Y, GROUND_DATA_CR, NAME_GROUND)
            VALUES 
            ({int(ground_id)}, '{ground_address}', {float(ground_geo_x)}, {float(ground_geo_y)}, CAST(sysdate AS DATE), '{(name_ground)}')"""
        with conn.cursor() as cursor:
            cursor.execute(sql_insert_ground)
            conn.commit()
            bot.send_message(message.from_user.id, 'Успешно👍\n'
                                                   '/help')
            help_button(message)
    else:
        bot.send_message(message.from_user.id, 'Вы ввели не по примеру\n'
                                               '/help')
        help_button(message)
@bot.message_handler(content_types=["text"])
def add_entry_trash(message):
    add_trash_entry = message.text
    split_add_trash = add_trash_entry.split('/')
    print(split_add_trash)
    if len(split_add_trash) == 7:
        trash_address = split_add_trash[0].strip()
        trash_geo_x = split_add_trash[1].strip()
        trash_geo_y = split_add_trash[2].strip()
        trash_id = split_add_trash[3].strip()
        trash_volume = split_add_trash[4].strip()
        time_clean_trash = split_add_trash[5].strip()
        region = split_add_trash[6].strip()

        sql_insert_trash = f"""INSERT INTO ODS_STUDY2.TRASH  
        (TRASH_ADDRESS, TRASH_GEO_X, TRASH_GEO_Y, TRASH_ID, TRASH_VOLUME, TIME_CLEAN_TRASH, TRASH_DATA_CR, REGION, TRASH_FLAG)
        VALUES 
        ('{trash_address}', {float(trash_geo_x)}, {float(trash_geo_y)}, {int(trash_id)}, {int(trash_volume)},
         {int(time_clean_trash)}, CAST(sysdate AS DATE), {int(region)}, {0})"""
        with conn.cursor() as cursor:
            cursor.execute(sql_insert_trash)
            conn.commit()
            bot.send_message(message.from_user.id, 'Успешно👍\n'
                                                   '/help')
            help_button(message)
    else:
        bot.send_message(message.from_user.id, 'Вы ввели не по примеру\n'
                                               '/help')
        help_button(message)

@bot.message_handler(content_types=["text"])
def add_entry_car(message):
    add_car_entry = message.text

    split_add_staff = add_car_entry.split('/')
    print(split_add_staff)

    car_id = split_add_staff[0].strip()
    car_model = split_add_staff[1].strip()
    car_number = split_add_staff[2].strip()
    date_mainten = split_add_staff[3].strip()
    car_volume = split_add_staff[4].strip()
    tank_capcity = split_add_staff[5].strip()
    date_tire_change = split_add_staff[6].strip()
    gasoline = split_add_staff[7].strip()
    expence = split_add_staff[8].strip()
    for i in range (0, 9):
        print(split_add_staff[i].strip())
    sql_insert_car = f"""INSERT INTO ODS_STUDY2.CAR
    (CAR_ID, MODEL, CAR_NUMBER, DATE_MAINTENANCE, СAR_VOLUME, TANK_CAPACITY, DATE_TIRE_CHANGE, GASOLINE, EXPENSE)
    VALUES 
    ({car_id}, '{car_model}', '{car_number}', to_date('{date_mainten}', 'YYYY-MM-DD'), {car_volume}, {tank_capcity},
     to_date('{date_tire_change}', 'YYYY-MM-DD'), '{gasoline}', {expence})"""
    with conn.cursor() as cursor:
        cursor.execute(sql_insert_car)
        conn.commit()
        bot.send_message(message.from_user.id, 'Успешно👍\n'
                                               '/help')
        help_button(message)


@bot.message_handler(content_types=["text"])
def add_entry_staff(message):
    user_add_staff = message.text

    split_add_staff = user_add_staff.split('/')
    print(split_add_staff)

    staff_id = split_add_staff[0].strip()
    staff_name = split_add_staff[1].strip()
    staff_birth = split_add_staff[2].strip()
    staff_role = split_add_staff[3].strip()
    staff_phone = split_add_staff[4].strip()
    staff_email = split_add_staff[5].strip()
    staff_salary = split_add_staff[6].strip()
    staff_password = split_add_staff[7].strip()

    sql_insert_staff = f"""INSERT INTO ODS_STUDY2.STAFF 
    (staff_id, NAME, BIRTH, USER_ACCES_ID, PHONE, EMAIL, SALARY, STAFF_DATE_CR, STAFF_ABSENCE_ID, STAFF_PASSWORD)
    VALUES 
    ({staff_id}, '{staff_name}', to_date('{staff_birth}', 'YYYY-MM-DD'), {staff_role}, '{staff_phone}', '{staff_email}',
     {staff_salary}, CAST(sysdate as DATE), {int(1)}, '{staff_password}')"""
    with conn.cursor() as cursor:
        cursor.execute(sql_insert_staff)
        conn.commit()
        bot.send_message(message.from_user.id, 'Успешно👍\n'
                                               '/help')
        help_button(message)

@bot.message_handler(content_types=["text"])
def delete_entry(message):
    if (message.text == 'Удалить сотрудника'):
        bot.send_message(message.from_user.id, 'Введите айди сотрудника, фамилию и имя через знак "/", кого хотите удалить из таблицы\n'
                         'Пример: "36/ Николаев Алексей"')
        bot.register_next_step_handler(message, delete_entry_staff)
    elif (message.text == 'Удалить автотранспортное средство'):
        bot.send_message(message.from_user.id, 'Введите название машины и номер машины чрезе знак "/", которую вы хотите удалить из таблицы\n'
                         'Пример: "ГАЗон NEXT Мусоровоз/ А390ВВ777"')
        bot.register_next_step_handler(message, delete_entry_car)
    elif (message.text == 'Удалить мусорку'):
        bot.send_message(message.from_user.id, 'Введите адрес мусорки как в таблице\n'
                         'Пример: "город Москва, 3-я Сокольническая улица, дом 4"')
        bot.register_next_step_handler(message, delete_entry_trash)
    elif (message.text == 'Удалить полигон'):
        bot.send_message(message.from_user.id, 'Введите адрес полигона как в таблице\n'
                         'Пример: "Московская обл, Мытищи, Коргашино, ул.Нагорная, 1"')
        bot.register_next_step_handler(message, delete_entry_ground)
    elif (message.text == 'Удалить базу'):
        bot.send_message(message.from_user.id, 'Введите адрес базы как в таблице\n'
                         'Пример: "Москва, 2-я Боевская улица, 6Ас1"')
        bot.register_next_step_handler(message, delete_entry_base)
    elif (message.text == 'Назад'):
         help_button(message)

@bot.message_handler(content_types=["text"])
def delete_entry_ground(message):
    ground_table_del = message.text
    sql_del_ground = f"""DELETE FROM ODS_STUDY2.trash where TRASH_ADDRESS = '{str(ground_table_del)}' """
    with conn.cursor() as cursor:
        cursor.execute(sql_del_ground)
        conn.commit()
        bot.send_message(message.from_user.id, 'Успешно👍\n'
                                                       '/help')
        help_button(message)
@bot.message_handler(content_types=["text"])
def delete_entry_base(message):
    trash_table_del = message.text
    sql_del_trash = f"""DELETE FROM ODS_STUDY2.trash where TRASH_ADDRESS = '{str(trash_table_del)}' """
    with conn.cursor() as cursor:
        cursor.execute(sql_del_trash)
        conn.commit()
        bot.send_message(message.from_user.id, 'Успешно👍\n'
                                                       '/help')
        help_button(message)


@bot.message_handler(content_types=["text"])
def delete_entry_trash(message):
    trash_table_del = message.text
    sql_del_trash = f"""DELETE FROM ODS_STUDY2.trash where TRASH_ADDRESS = '{str(trash_table_del)}' """
    with conn.cursor() as cursor:
        cursor.execute(sql_del_trash)
        conn.commit()
        bot.send_message(message.from_user.id, 'Успешно👍\n'
                                                       '/help')
        help_button(message)
@bot.message_handler(content_types=["text"])
def delete_entry_car(message):
    car_table_del = message.text
    split_del_car_table = car_table_del.split('/')
    if len(split_del_car_table) == 2:
        print(split_del_car_table)
        car_name_del_table = split_del_car_table[0].strip()
        car_number_del_table = split_del_car_table[1].strip()
        sql_del_car = f"""DELETE FROM ODS_STUDY2.CAR where MODEL = '{str(car_name_del_table)}' and CAR_NUMBER = '{str(car_number_del_table)}'"""
        with conn.cursor() as cursor:
            cursor.execute(sql_del_car)
            conn.commit()
            bot.send_message(message.from_user.id, 'Успешно👍\n'
                                                       '/help')
            bot.register_next_step_handler(message, help_button)
    else:
        bot.send_message(message.from_user.id, 'Вы ввели не по примеру\n'
                                                '/help')
        help_button(message)

@bot.message_handler(content_types=["text"])
def delete_entry_staff(message):
    staff_table_del = message.text
    split_del_staff_table = staff_table_del.split(',')
    if len(split_del_staff_table) == 2:
        print(split_del_staff_table)
        staff_id_del_table = split_del_staff_table[0].strip()
        staff_name_del_table = split_del_staff_table[1].strip()
        sql_del_staff = f"""DELETE FROM ODS_STUDY2.staff where STAFF_ID = {staff_id_del_table} and NAME = '{staff_name_del_table}'"""
        with conn.cursor() as cursor:
            cursor.execute(sql_del_staff)
            conn.commit()
            bot.send_message(message.from_user.id, 'Успешно👍\n'
                                                       '/help')
            help_button(message)
    else:
        bot.send_message(message.from_user.id, 'Вы ввели не по примеру\n'
                                                '/help')
        help_button(message)
@bot.message_handler(content_types=["text"])
def choice_role_5(message):
    if (message.text == 'Список автотранспортных средств'):
        sql_query_car = """SELECT * FROM ODS_STUDY2.CAR c """
        df_car = pd.read_sql(sql_query_car, conn)
        df_car.to_excel('report_car.xlsx', encoding = 'cp1251')
        csv_file_car = open('report_car.xlsx', 'rb')
        bot.send_document(message.from_user.id, csv_file_car)
        bot.register_next_step_handler(message, choice_role_5)
        bot.polling.abort = True
    elif (message.text == 'Список сотрудников'):
        sql_query_staff = """SELECT s.NAME, s.BIRTH, s.SALARY, s.PHONE FROM ODS_STUDY2.STAFF s """
        df_staff = pd.read_sql(sql_query_staff, conn)
        df_staff.to_excel('report_staff.xlsx', encoding = 'cp1251')
        csv_file_staff = open('report_staff.xlsx', 'rb')
        bot.send_document(message.from_user.id, csv_file_staff)
        bot.register_next_step_handler(message, choice_role_5)
        bot.polling.abort = True
    elif (message.text == 'Остановить бота'):
        conn.close()
        bot.polling()

bot.infinity_polling(timeout=10, long_polling_timeout = 5)

