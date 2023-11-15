from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import numpy
from datetime import datetime
import json


app = Flask(__name__)
conn=psycopg2.connect(database="postgres", user="postgres", password="1234", host="localhost", port=5432) #Вход в БД
#json_File_read="чтото.json" #имя файла в формате json


#cities=[["Москва", "Москва"],["Омск", "Омск"],["Нижний Новгород", "Нижний Новгород"],]

cities=[]

def JSON_reading():
    with open("Test.json", "r", encoding='utf-8') as file:
        capitals_json = file.read()
    book = json.loads(capitals_json)  # Превращение jsona  в словарь
    cities_json = book["cities"]
    counter = 0
    for rows in cities_json:
        buffer = cities_json[counter]["cityName"];
        cities.append(buffer)
        counter = counter + 1
    one_row=[]
    return counter


def Table_info():
    global Info
    global Peresadki #количество пересадок
    global Number_of_Rows

    #Тестовая попытка в динамически двумерный массив с чтением из json
    Full_Information=[] #пустой массив для  для всей информации
    Info=[]

    with open("Test.json", "r") as file:
        capitals_json = file.read()
    book = json.loads(capitals_json)  # Превращение jsona  в словарь
    cities_json = book["departures"]
    buffer =['','','','','','','','']
    counter = 0
    for rows in cities_json:
        buffer[0] = str(cities_json[counter]["transportType"]);#тип транспорта
        buffer[1] = (cities_json[counter]["departureDate"]);#Дата
        buffer[2] = cities_json[counter]["departureDate"]; #Дата прибытия через время в пути
        buffer[3] = cities_json[counter]["departureDate"];#Время прибытия через время в пути
        buffer[4] = cities_json[counter]["departureDate"];#
        buffer[5] = cities_json[counter]["departureCity"];
        buffer[6] = cities_json[counter]["arrivalCity"];
        buffer[7] = cities_json[counter]["price"];
        #print(buffer)
        #print(counter)
        Info.extend(buffer)
        counter = counter + 1
        Number_of_Rows = counter
        #Сделать for на блоки с билетами(или найти)
    #Конец попытки
    Peresadki = ['1', '2', '1', '1']#Массив для хранения пересадок


   # cur = conn.cursor()
   # cur.execute("SELECT date1 FROM Тестовая_таблица_расписания")


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        global depart
        global destination
        depart=request.form['depart']
        destination=request.form['destination']
        return redirect(url_for('res'))
    JSON_reading()
    return render_template('Главная.html', list_of_cities=cities, Cities=3)

@app.route('/res', methods=['GET', 'POST'])
def res():

    #Выбор из таблицы нужных строк
    Table_info()
    return render_template('Подбор транспорта.html', Depart=depart, Destination=destination, info=Info, Peresadki=Peresadki, Number=Number_of_Rows)
if __name__ == '__main__':
    app.run()

