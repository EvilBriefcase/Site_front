from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import numpy
import datetime
import json
import heapq

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

#Сделать функцию превращение NAME в ID

def NAME_ID(name):
    counter = 1
    while (cities_name_id[counter] != name):  # Сравнение id из списка городов и id из json
        counter = counter + 2;  # Так как в массиве id и имя идут рядом, то для следующего Id нужно "перешагнуть" имя
    id = cities_name_id[counter -1]
    return id

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

def Table_info(ID_Ticket): #функция выборки и приведения информации к виду удобному для чтения пользователем на экране
    global Info #Массив всей информации о билете
    global Number_of_Rows
    global Peresadka #Массив времени на пересадку

    Peresadka=[]
    Info=[]#пустой массив для  для всей информации
    cities_json = book_tickets["departures"]

    buffer =['','','','','','','','', '']


    TimeTravel=Minutes_To_DateTime(); #Время в дороге

    counter = 0
    counter_tickets=0
    print(len(ID_Ticket[2]))
    for counter_tickets in range(0,len(ID_Ticket[2]) ):
        for rows in cities_json:
            #print(ID_Ticket[2][counter_tickets])
            #print(str(cities_json[counter]["id"]))
            if(ID_Ticket[2][counter_tickets] ==  str(cities_json[counter]["id"])):

               # counter_tickets = counter_tickets + 1;  # Счетчик билетов найденных алгоритмом

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
            counter = counter + 1#Счетчик прохода по строкам
            Number_of_Rows = counter_tickets
        #Сделать for на блоки с билетами(или найти)
        Info.reverse()
        counter=0
    #Конец попытки
    return Info[counter_tickets+3]

#
def find_paths(graph, tickets_info, start, end):
    # Инициализация расстояний
    distances = {city: float('infinity') for city in graph}
    distances[start] = 0

    # Инициализация приоритетной очереди
    priority_queue = [(0, start)]

    # Словарь для отслеживания предыдущего города на пути
    previous_city = {city: None for city in graph}

    # Словарь для отслеживания стоимости пути
    path_cost = {city: 0 for city in graph}

    # Словарь для отслеживания id билета на пути
    path_tickets = {city: None for city in graph}

    while priority_queue:
        current_distance, current_city = heapq.heappop(priority_queue)
        # Проверка, не посещен ли текущий город
        if current_distance > distances[current_city]:
            continue

        # Проверка достижения конечного города
        if current_city == end:
            # Восстановление пути, стоимости и id билетов
            path = []
            total_cost = 0
            ticket_ids = []
            while current_city is not None:
                path.insert(0, current_city)
                total_cost += path_cost[current_city]
                ticket_ids.append(path_tickets[current_city])
                current_city = previous_city[current_city]
            return path, total_cost, ticket_ids

        # Обновление расстояний до соседних городов, если сосед существует
        if current_city in graph:
            for neighbor, weight, ticket_id in graph[current_city]:
                distance = current_distance + weight

                # Если найден более короткий путь, обновляем расстояние, стоимость и id билета
                if distance < distances.get(neighbor, float('infinity')):
                    distances[neighbor] = distance
                    previous_city[neighbor] = current_city
                    path_cost[neighbor] = weight
                    path_tickets[neighbor] = ticket_id
                    heapq.heappush(priority_queue, (distance, neighbor))

    return None, 0, None


def find_direct_route(city_connections, start_city, end_city):
    # Проверяем, есть ли города в словаре
    if start_city not in city_connections.keys():
        return '-1'
    # Ищем прямое сообщение между городами
    connections_from_start = city_connections[start_city]
    for connected_city, cost, id in connections_from_start:
        if connected_city == end_city:
            return cost

    return '100000'

# Функция для вычисления разницы во времени в минутах
def calculate_time_difference(departure_date, travel_time):
    datetime.departure_datetime = datetime.datetime.fromisoformat(departure_date)
    datetime.arrival_datetime = datetime.departure_datetime + datetime.timedelta(minutes=travel_time)
    return (datetime.arrival_datetime - datetime.departure_datetime).seconds // 60

# Заполнение графа
def filling_graph(data):
    graph = {}
    tickets_info = {}  # Добавим словарь для хранения информации о билетах

    for departure in data['departures']:
        departure_city = str(departure['departureCity'])
        arrival_city = str(departure['arrivalCity'])

        time_difference = calculate_time_difference(departure['departureDate'], departure['travelTime'])

        if departure_city not in graph:
            graph[departure_city] = []
        graph[departure_city].append((arrival_city, int(time_difference), departure['id']))  # Добавляем id билета
        tickets_info[departure['id']] = {
            'transportType': departure['transportType'],
            'departureDate': departure['departureDate'],
            'travelTime': departure['travelTime'],
            'price': departure['price']
        }

    return graph, tickets_info

def Algotitm(source, destination):
    with open('test.json', 'r') as fp:
        data = json.load(fp)
    graph, tickets_info = filling_graph(data)

   # source = '30'
  #  destination = '35'

    eta = find_direct_route(graph, source, destination)  # Эталонное время

  #  print('Время прямого пути', eta)

    result = find_paths(graph, tickets_info, source, destination)
    print(result)

    if result:
        return result
        #print('Путь', '->'.join(result[0]), 'Время в пути ', result[1])
    else:
        return (-1)
#


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
   # print(Algotitm(NAME_ID(depart), NAME_ID(destination))[2][1])
    #Выбор из таблицы нужных строк
    last_departure_date=Table_info(Algotitm(str(NAME_ID(depart)), str(NAME_ID(destination)))) #Получение последней даты прибытия из билета для показания даты прибытия в общем
    return render_template('Подбор транспорта.html', Depart=depart, Destination=destination, info=Info,Peresadka=Peresadka, Number=Number_of_Rows, Date_Dep=depart_date, Date_Dest=last_departure_date, Travel_days=Summary_Travel_time.day, Travel_hours=Summary_Travel_time.hour)

if __name__ == '__main__':
    app.run()