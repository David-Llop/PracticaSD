import logging
import os
from multiprocessing import Process
from xmlrpc.server import SimpleXMLRPCServer
import redis
import requests
from plyer.utils import platform
from plyer import notification

WORKERS = {}
WORKER_ID = 0
SEMS = {}
SEMS_ID = 0
r = redis.Redis()

logging.basicConfig(level=logging.INFO)

server = SimpleXMLRPCServer(
    ('localhost', 9000),
    logRequests=True,
    allow_none=True)


def countingWords_sem(id, file, sem):
    global SEMS
    sem = int(sem)
    paraules = 0
    resp = requests.get(file)
    with open(str(id) + "aux.txt", 'wb') as f:
        f.write(resp.content)
    with open(str(id) + "aux.txt", 'r') as f:
        for line in f:
            paraules += len(line.split(' '))
    with open(str(sem) + "sem_aux.txt", 'a') as f:
        f.write(str(paraules)+'\n')
    SEMS[sem] -= 1
    os.remove(str(id) + "aux.txt")


def countingWords_ctl(sem):
    global SEMS
    paraules = int('0')
    sem = int(sem)
    if SEMS[sem] > 1:
        r.rpush('cua', 'CW_ctl,' + str(sem))
        return
    with open(str(sem) + "sem_aux.txt", 'r') as f:
        for line in f:
            paraules += int(line)

    notification.notify(
        title='Resultat CountingWords múltiples fitxers',
        message=str(paraules),
        app_name='Practica 1 SD',
        timeout=5000,
        toast=True
    )
    os.remove(str(sem) + "sem_aux.txt")


def start_worker(id):
    global r
    while True:
        task = r.blpop('cua')
        if task != None:
            aux = str(task).split("'")[3]
            file = aux.split(',')[1]
            if aux.split(',')[0] == 'CountingWords':
                if len(aux.split(',')) == 2:
                    countingWords(id, file)
                else:
                    countingWords(id, aux.replace(aux.split(',')[0] + ',', ''))
            elif aux.split(',')[0] == 'WordCount' and len(aux.split(',')) == 2:
                wordCount(id, file)
            elif aux.split(',')[0] == 'CW_sem':
                countingWords_sem(id, file, aux.split(',')[2])
            elif aux.split(',')[0] == 'CW_ctl':
                countingWords_ctl(file)


def countingWords(id, file):
    global SEMS
    global SEMS_ID
    global r
    paraules = 0
    if len(file.split(',')) > 1:
        SEMS[SEMS_ID] = len(file.split(',')) + 1
        for f in file.split(','):
            r.rpush('cua', 'CW_sem,' + f + ',' + str(SEMS_ID))
        r.rpush('cua', 'CW_ctl,' + str(SEMS_ID))
        SEMS_ID += 1
        return
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
