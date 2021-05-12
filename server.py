import logging
import os
from multiprocessing import Process, Manager
from xmlrpc.server import SimpleXMLRPCServer
import redis
import requests
from plyer import notification

global COUNTERS
WORKERS = {}
WORKER_ID = 0
r = redis.Redis()


def newCount(value):
    global COUNTERS
    global COUNTERS_ID
    COUNTERS [COUNTERS_ID] = value
    WORKER_ID += 1


def decCount(id):
    global COUNTERS
    COUNTERS[id] -=1

def getCount(id):
    global COUNTERS
    return  COUNTERS[id]


logging.basicConfig(level=logging.INFO)

server = SimpleXMLRPCServer(
    ('localhost', 9000),
    logRequests=True,
    allow_none=True)

def start_worker(id):
    global r
    while True:
        task = r.blpop('cua')
        if task != None:
            aux = str(task).split("'")[3]
            file = aux.split(',')[1]
            if aux.split(',')[0] == 'CountingWords':
                countingWords(id, file)
            elif aux.split(',')[0] == 'WordCount' and len(aux.split(',')) == 2:
                wordCount(id, file)


def countingWords(id, file):
    global r
    paraules = 0
    resp = requests.get(file)
    with open(str(id) + "aux.txt", 'wb') as f:
        f.write(resp.content)
    with open(str(id) + "aux.txt", 'r') as f:
        for line in f:
            paraules += len(line.split(' '))
    notification.notify(
        title='Resultat CountingWords' + str(file).split('/')[1],
        message=str(paraules),
        app_name='Practica 1 SD',
        timeout=5000,
        toast=True
    )
    os.remove(str(id) + "aux.txt")


def wordCount(id, file):
    paraules = {}
    r = requests.get(file)
    with open(str(id) + "aux.txt", 'wb') as f:
        f.write(r.content)
    with open(str(id) + "aux.txt", 'r') as f:
        for line in f:
            for w in line.split(' '):
                try:
                    paraules[w] += 1
                except:
                    paraules.update({w: 1})

    notification.notify(
        title='Resultat WordCound' + str(file).split('/')[1],
        message=str(paraules),
        app_name='Practica 1 SD',
        timeout=5000,
        toast=True
    )
    os.remove(str(id) + "aux.txt")


def create_worker():
    global WORKERS
    global WORKER_ID

    proc = Process(target=start_worker, args=(WORKER_ID,))
    proc.start()
    WORKERS[WORKER_ID] = proc
    WORKER_ID += 1
    workersList()
    return WORKER_ID


def eliminate_worker(id):
    global WORKERS
    global WORKER_ID
    for aux in WORKERS:
        if WORKERS.get(aux).name == 'Process-' + str(id):
            WORKERS[int(id)].terminate()
            WORKERS.pop(aux)
            break


def put_task(task):
    global r
    r.rpush('cua', task)


def workersList():
    return [WORKERS.get(aux).name for aux in WORKERS]


def main():
    global r
    manager = Manager()
    global COUNTERS
    COUNTERS = manager.dict()
    server.register_function(put_task)
    server.register_function(eliminate_worker)
    server.register_function(create_worker)
    server.register_function(workersList)
    try:
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
    r.flushall()


if __name__ == "__main__":
    main()
