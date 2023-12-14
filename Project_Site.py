from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import numpy
import datetime
import json


app = Flask(__name__)
conn=psycopg2.connect(database="postgres", user="postgres", password="1234", host="localhost", port=5432) #Вход в БД
#json_File_read="чтото.json" #имя файла в формате json



cities_name=[] #Массив Имя города
cities_name_id=[] #Массив id_имя
cities_full=[] #

#Открытие json со списком городов и его чтение
with open("Test.json", "r", encoding='utf-8') as file:
    capitals_json = file.read()
book_cities = json.loads(capitals_json)  # Превращение jsona  в словарь

#Открытие json со списком билетов
with open("Test.json", "r", encoding='utf-8') as file:
    tickets_json = file.read()
book_tickets = json.loads(tickets_json)  # Превращение jsona  в словарь



def JSON_reading(): #Функция сохранения списка городов для выдачи выпадающим списком
    cities_json = book_cities["cities"] #Получсние словаря с имя_id  городов
    counter = 0
    for rows in cities_json:
        # тестовый вариант с id| город парой
        buffer = cities_json[counter]["id"];
        cities_name_id.append(buffer)

        buffer = cities_json[counter]["cityName"];

        cities_name.append(buffer)
        cities_name_id.append(buffer)

        buffer=cities_json[counter]
        cities_full.extend(buffer)
        counter = counter + 1 #Счетчик городов
    return counter

def ID_NAME(id): #функция сверки ID города и его имени
    counter=0
    while(cities_name_id[counter]!=id): #Сравнение id из списка городов и id из json
        counter=counter+2; #Так как в массиве id и имя идут рядом, то для следующего Id нужно "перешагнуть" имя
    name=cities_name_id[counter+1]
    return name



def Minutes_To_DateTime(): #Функция пересчета времени пути в часы/минуты
    global Summary_Travel_time
    Summary_Travel_time = datetime.datetime.strptime("0:0", "%H:%M") #обнуление счетчика времени в пути(часы и минуты)

    cities_json = book_tickets["departures"]
    TimeTravel=[]
    counter=0

    for rows in cities_json:
        buffer = cities_json[counter]["travelTime"];
        counter=counter+1  #Счетчик для перехода к следующей структуре с информацией по билету
        Hours = int(buffer / 60);  # Часы
        Minutes = buffer % 60  # Минуты

        time_str = str(Hours) + ':' + str(Minutes)#Превращение в строку формата %H:$M
        buffer_date_time = datetime.datetime.strptime(str(time_str), "%H:%M");#Превращение в формат datetime

        Summary_Travel_time=Summary_Travel_time + datetime.timedelta(hours=buffer_date_time.hour, minutes=buffer_date_time.minute)# подсчет общего времени в пути без пересадов для этого берем нулевой формат datetime и еще получаем timedelta

        TimeTravel.append((buffer_date_time.time())) #оздание списка с временем поездки
    return TimeTravel

def SummaryTime():
    #Подсчет времени с пересадками
    return

def Table_info(): #функция выборки и приведения информации к виду удобному для чтения пользователем на экране
    global Info #Массив всей информации о билете
    global Number_of_Rows
    global Peresadka #Массив времени на пересадку

    Peresadka=[]
    Info=[]#пустой массив для  для всей информации
    cities_json = book_tickets["departures"]

    buffer =['','','','','','','','', '']


    TimeTravel=Minutes_To_DateTime(); #Время в дороге


    counter = 0
    for rows in cities_json:

        buffer[0] = str(cities_json[counter]["transportType"]);#тип транспорта

        buffer_date_time = datetime.datetime.strptime(str(cities_json[counter]["departureDate"]), "%Y-%m-%dT%H:%M:%S");
        datetime_buffer = datetime.datetime.strptime(str(cities_json[counter]["departureDate"]),"%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=TimeTravel[counter].hour,minutes=TimeTravel[counter].minute)  # Буффер для datetime полного времени прибытия

        buffer[1] =str( buffer_date_time.date())  #Дата отправления
        buffer[2] = str(buffer_date_time.time()); #Время отправления


        buffer[3] = datetime_buffer.date();#Дата прибытия через время в пути
        buffer[4] = datetime_buffer.time();#Время прибытия через время в пути

        #buffer[5]=cities_json[counter]["departureCity"];
        buffer[5] = ID_NAME(int(cities_json[counter]["departureCity"]))

        buffer[6] = ID_NAME(int(cities_json[counter]["arrivalCity"]));
        buffer[7] = cities_json[counter]["price"];

        buffer[8]=TimeTravel[counter];
        Previous=datetime_buffer #переменная для хранения предыдущей даты прибытия
        if counter>=1:
            Peresadka.append((buffer_date_time - datetime.timedelta(hours=Previous.hour, minutes=Previous.minute)).time())
            #Summary_Travel_time=Summary_Travel_time + datetime.timedelta(hours=Peresadka[counter-1].hour, minutes=Peresadka[counter-1].minute)

        Info.extend(buffer)
        counter = counter + 1
        Number_of_Rows = counter
        #Сделать for на блоки с билетами(или найти)
    #Конец попытки
    return Info[counter+3]


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        global depart
        global destination
        global depart_date
        global Correct_date

        Correct_date=5
        depart=request.form['depart']   #Получение из формы города отправление
        destination=request.form['destination'] #Получение из формы города назначения
        depart_date=str((datetime.datetime.strptime(request.form['Date'], "%d.%m.%Y")).date())#считывание с формы даты отправления

        #Проверка введеный пользователем даты на актуальность текущей дате
        if datetime.datetime.strptime(request.form['Date'], "%d.%m.%Y").date() > datetime.datetime.now().date():
            Correct_date=""
            return redirect(url_for('res'))
        else:
            Correct_date="1" #
        #Конец

    number_of_cities=JSON_reading()
    return render_template('Главная.html', list_of_cities=cities_name, Cities=number_of_cities)

@app.route('/res', methods=['GET', 'POST'])
def res():

    #Выбор из таблицы нужных строк
    last_departure_date=Table_info() #Получение последней даты прибытия из билета для показания даты прибытия в общем

    return render_template('Подбор транспорта.html', Depart=depart, Destination=destination, info=Info,Peresadka=Peresadka, Number=Number_of_Rows, Date_Dep=depart_date, Date_Dest=last_departure_date, Travel_days=Summary_Travel_time.day, Travel_hours=Summary_Travel_time.hour)
if __name__ == '__main__':
    app.run()
