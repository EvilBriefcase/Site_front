from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import numpy
from datetime import datetime



app = Flask(__name__)



def Table_info():
    global Info
    global Peresadki
    Peresadki = [['', ''], ['', '']]
    Info = [['', '', '', '', '', '', ''], ['', '', '', '', '', '', ''], ['', '', '', '', '', '', '']]
    Time=[['',''], ['',''],['','']]

    transport_code='Поезд'
    date_time_dep='23.09.2023'
    dep_point='Москва'
    date_time_dest='23.09.2023'
    dest_point='Казань'
    Number_of_Peresadki=1
    #Ввод данных от пользователя + прогресс Notion, разделение по людям с
    test="19:00:00"
    #Первая таблица
    Time[0][0]=datetime.strptime(test, "%H:%M:%S")
    Time[0][1]=datetime.strptime("20:00:00", "%H:%M:%S")
    Info[0][0] = transport_code
    Info[0][1] = date_time_dep
    Info[0][2] = dep_point
    Info[0][3] = date_time_dest
    Info[0][4] = dest_point
    Info[0][5] = Time[0][0]
    Info[0][6] = Time[0][1]

    #Вторая таблица
    Time[1][0]=datetime.strptime("20:30:00", "%H:%M:%S")
    Time[1][1]=datetime.strptime("21:00:00", "%H:%M:%S")
    Info[1][0] = "Самолет"
    Info[1][1] = date_time_dep
    Info[1][2] = "Казань"
    Info[1][3] = date_time_dest
    Info[1][4] = "Омск"
    Info[1][5] = Time[1][0]
    Info[1][6] = Time[1][1]

    #Третья таблицы

    #Пересадки
    if (Number_of_Peresadki ==1):
        Peresadki[0][0]="Время на пересадку: "
        Peresadki[0][1]=Time[1][0]-Time[0][1]
    if (Number_of_Peresadki == 2):
        Peresadki[1][0] = "Время на пересадку: "
        Peresadki[1][1] = Time[2][0]-Time[1][1]

    return Number_of_Peresadki

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        global depart
        global destination
        depart=request.form['depart']
        destination=request.form['destination']
        return redirect(url_for('res'))
    return render_template('Главная.html')

@app.route('/res', methods=['GET', 'POST'])
def res():

    #Выбор из таблицы нужных строк
    Table_info()

    return render_template('Подбор транспорта.html', Depart=depart, Destination=destination, info=Info, Peresadki=Peresadki, peresadok=1)
if __name__ == '__main__':
    app.run()

#    Time = Time, Date_Dep = '23.09.2023', Date_Dest = '23.09.2023', Transport = transport_code, Date_Time_Dep = date_time_dep, Dep_Point = dep_point, Date_Time_Dest = date_time_dest, Dest_Point = dest_point)
