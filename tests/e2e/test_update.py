from multiprocessing import Process
import threading
from time import sleep
from flask import Flask, jsonify, request
import pytest
import json
from urllib.request import urlopen, Request
from uuid import uuid1
import requests


key = '12345'
event = threading.Event()
host_name = "0.0.0.0"
port = 6077

#сервер для принятия сообщений с клиента в тестовых целях
app = Flask(__name__)             # create an app instance
@app.route("/", methods=['POST'])
def data_receive():
    try:
        content = request.json
        #print(content['msg'])
        f = open('./temp.txt', 'a+')
        f.write(content['msg'] + "\n")
        f.close()
    except Exception as e:
        print(e)
        return "BAD DATA RESPONSE", 400
    return jsonify({"status": True})
    

#начало работы, загрузка, "включение тумблера"
def start():
    data = {
    }
    response = requests.post(
        "http://0.0.0.0:6064/start",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200

#авторизация ключа
def key_in(name):
    data = {
        "name": name
    }
    response = requests.post(
        "http://0.0.0.0:6064/key_in",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200

#извлечение указанного ключа
def key_out(name):
    data = {
        "name": name
    }
    response = requests.post(
        "http://0.0.0.0:6064/key_out",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200

#остановка всех процессов системы, "выключение тумблера"
def stop():
    data = {
    }
    response = requests.post(
        "http://0.0.0.0:6064/stop",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200
    

#def key_changing(event):
    #можно добавить, но это безопасность, по сути, тут она не нужна
    
###
### Functionally tests
###

def test_full_functionality():
    #поднимаем сервер для приемки сообщений
    server = Process(target = lambda: app.run(port = port, host=host_name))
    server.start()
    
    #вводим настройки для запуска
    f = open('./file_server/data/settings.txt', 'w')
    data = {
	"timeout": 2,
	"max": 20,
	"alarm_level": 15,
	"output": "http://172.17.0.1:" + str(port) + "/"
    }
    json.dump(data, f)
    f.close()

    start()

    #блок остался от изменения ключей, пока оставил
    # thread = threading.Thread(target=lambda: key_changing(event))
    # thread.start()
    #f = open('./file_server/data/key.txt', 'w')
    #f.write(key)
    #f.close()

    #вводим ключи, даем отработать, извлекаем ключи, завершая работу с обновлением
    sleep(2)
    key_in('T')
    key_in('S')
    sleep(15)
    key_out('T')
    key_out('S')
    sleep(2)
    stop()
    sleep(2)
    
    #освобождаем порт
    server.terminate()
    server.join()

    #читаем полученный лог
    f = open('./temp.txt', 'r')
    lines = f.readlines()
    f.close()

    #print(lines)
    assert 'Updates downloaded successfully\n' in lines

    #зачищаем полученный лог
    f = open('./temp.txt', 'w')
    f.write("")
    f.close()
