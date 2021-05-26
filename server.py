import logging
import os
from multiprocessing import Process, Manager
from xmlrpc.server import SimpleXMLRPCServer
import redis
import requests
from plyer import notification
import ast

global COUNTERS
WORKERS = {}
WORKER_ID = 0
r = redis.Redis()
TASK_ID =0


logging.basicConfig(level=logging.INFO)

server = SimpleXMLRPCServer(
    ('localhost', 9000),
    logRequests=True,
    allow_none=True)

def get_task():
    global TASK_ID
    return TASK_ID

def inc_task():
    global TASK_ID
    TASK_ID+=1


def conuting_sem(id, param):
    global r
    paraules = 0
    task=param.split(';')[0]
    file=param.split(';')[1]
    resp = requests.get(file)
    with open(str(id) + "aux.txt", 'wb') as f:
        f.write(resp.content)
    with open(str(id) + "aux.txt", 'r') as f:
        for line in f:
            paraules += len(line.split(' '))
    r.rpush(str(task), str(paraules))
    os.remove(str(id) + "aux.txt")


def conuting_ctl(id, param):
    global r
    paraules=0
    task = param.split(';')[0]
    file = int(param.split(';')[1])
    for i in range(file):
        aux=r.blpop(task)
        if aux is not None:
            aux = str(aux).split("'")[3]
            paraules+=int(aux)
    notification.notify(
        title='Resultat CountingWords diversos arxius',
        message=str(paraules),
        app_name='Practica 1 SD',
        timeout=5000,
        toast=True
    )


def word_sem(id, param):
    global r
    paraules={}
    task = param.split(';')[0]
    file = param.split(';')[1]
    resp = requests.get(file)
    with open(str(id) + "aux.txt", 'wb') as f:
        f.write(resp.content)
    with open(str(id) + "aux.txt", 'r') as f:
        for line in f:
            for w in line.split(' '):
                try:
                    paraules[w] += 1
                except:
                    paraules.update({w: 1})
    r.rpush(str(task), str(paraules))
    os.remove(str(id) + "aux.txt")

def word_ctl(id, param):
    global r
    paraules={}
    task = param.split(';')[0]
    file = param.split(';')[1]
    task = param.split(';')[0]
    file = int(param.split(';')[1])
    for i in range(file):
        aux = r.blpop(task)
        if aux is not None:
            aux=str(str(aux).split('"')[1])
            dict_aux=ast.literal_eval(aux)
            for i in dict_aux:
                if i in paraules:
                    paraules[i] += int(dict_aux[i])
                else:
                    paraules.update({i: int(dict_aux[i])})
    notification.notify(
        title='Resultat WordCound de diversos arxius',
        message=str(paraules),
        app_name='Practica 1 SD',
        timeout=5000,
        toast=True
    )


def start_worker(id):
    global r
    while True:
        task = r.blpop('cua')
        if task != None:
            aux = str(task).split("'")[3]
            op=aux.split(',')[0]
            if op == 'CountingWords':
                countingWords(id, aux.replace(op, ''))
            elif op == 'WordCount':
                wordCount(id, aux.replace(op, ''))
            elif op =='counting_sem':
                conuting_sem(id, aux.replace(op, ''))
            elif op =='counting_ctl':
                conuting_ctl(id, aux.replace(op, ''))
            elif op =='word_sem':
                word_sem(id, aux.replace(op, ''))
            elif op =='word_ctl':
                word_ctl(id, aux.replace(op, ''))


def countingWords(id, file):
    global r
    paraules = 0
    task = file.split(';')[0]
    file = file.split(';')[1]
    if len(file.split(',')) > 1:
        for f in file.split(','):
            r.rpush('cua', "counting_sem,"+str(task)+";"+str(f))
        r.rpush('cua', "counting_ctl," + str(task)+";"+str(len(file.split(','))))
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
    global r
    paraules = {}
    task = file.split(';')[0]
    file = file.split(';')[1]
    if len(file.split(',')) > 1:
        for f in file.split(','):
            r.rpush('cua', "word_sem," + str(task) + ";" + str(f))
        r.rpush('cua', "word_ctl," + str(task) + ";" + str(len(file.split(','))))
        return
    print(task)
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
    WORKERS[str(WORKER_ID)] = proc
    WORKER_ID += 1
    workersList()
    return WORKER_ID


def eliminate_worker(id):
    global WORKERS
    global WORKER_ID
    WORKERS[str(int(id)-1)].terminate()
    del WORKERS[str(int(id)-1)]


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
    server.register_function(get_task)
    server.register_function(inc_task)
    try:
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
    r.flushall()


if __name__ == "__main__":
    main()
