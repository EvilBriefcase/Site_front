from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import numpy
import datetime
import json


app = Flask(__name__)
conn=psycopg2.connect(database="postgres", user="postgres", password="1234", host="localhost", port=5432) #Вход в БД
#json_File_read="чтото.json" #имя файла в формате json


#cities=[["Москва", "Москва"],["Омск", "Омск"],["Нижний Новгород", "Нижний Новгород"],]

cities_name=[]
cities_name_id=[] #Массив id_имя
cities_full=[]

#Открытие json со списком городов и его чтение
with open("Test.json", "r", encoding='utf-8') as file:
    capitals_json = file.read()
book = json.loads(capitals_json)  # Превращение jsona  в словарь

#Открытие json со списком билетов
with open("Test.json", "r", encoding='utf-8') as file:
    capitals_json = file.read()
book = json.loads(capitals_json)  # Превращение jsona  в словарь



def JSON_reading(): #Функция сохранения списка городов для выдачи выпадающим списком

    cities_json = book["cities"] #
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
        counter = counter + 1
    return counter

def ID_NAME(id):
    counter=0
    while(cities_name_id[counter]!=id):
        counter=counter+2;
    name=cities_name_id[counter+1]
    return name



def Minutes_To_DateTime():
    cities_json = book["departures"]
    TimeTravel=[]
    counter=0
    for rows in cities_json:
        buffer = cities_json[counter]["travelTime"];
        counter=counter+1
        Hours = int(buffer / 60);  # Часы
        Minutes = buffer % 60  # Минуты

        time_str = str(Hours) + ':' + str(Minutes)#Превращение в строку формата %H:$M
        buffer_date_time = datetime.datetime.strptime(str(time_str), "%H:%M");#Превращение в формат datetime
        TimeTravel.append((buffer_date_time.time()))
    return TimeTravel

def Table_info(): #функция выборки и приведения информации к виду удобному для чтения пользователем на экране
    global Info
    global Peresadki #количество пересадок
    global Number_of_Rows

    Full_Information=[] #пустой массив для  для всей информации
    Info=[]


    cities_json = book["departures"]

    buffer =['','','','','','','','', '']

    TimeTravel=Minutes_To_DateTime(); #Время в дороге

    counter = 0
    for rows in cities_json:
        buffer[0] = str(cities_json[counter]["transportType"]);#тип транспорта

        buffer_date_time = datetime.datetime.strptime(str(cities_json[counter]["departureDate"]), "%Y-%m-%dT%H:%M:%S");
        #print(buffer_date_time)
        buffer[1] =str( buffer_date_time.date())
        buffer[2] = str(buffer_date_time.time()); #Дата прибытия через время в пути

        buffer[3] = cities_json[counter]["departureDate"];#Время прибытия через время в пути
        buffer[4] = cities_json[counter]["departureDate"];#

        #buffer[5]=cities_json[counter]["departureCity"];
        buffer[5] = ID_NAME(int(cities_json[counter]["departureCity"]))

        buffer[6] = ID_NAME(int(cities_json[counter]["arrivalCity"]));
        buffer[7] = cities_json[counter]["price"];

        buffer[8]=TimeTravel[counter];
        Info.extend(buffer)
        counter = counter + 1
        Number_of_Rows = counter
        #Сделать for на блоки с билетами(или найти)
    #Конец попытки
    Peresadki = ['1', '2', '1', '1']#Массив для хранения пересадок
    return


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        global depart
        global destination
        depart=request.form['depart']
        destination=request.form['destination']
        return redirect(url_for('res'))
    number_of_cities=JSON_reading()
    print(ID_NAME(int(29)))
    return render_template('Главная.html', list_of_cities=cities_name, Cities=number_of_cities)

@app.route('/res', methods=['GET', 'POST'])
def res():

    #Выбор из таблицы нужных строк
    Table_info()
    return render_template('Подбор транспорта.html', Depart=depart, Destination=destination, info=Info, Peresadki=Peresadki, Number=Number_of_Rows)
if __name__ == '__main__':
    app.run()

