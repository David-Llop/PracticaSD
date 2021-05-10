import logging
from multiprocessing import Process
from xmlrpc.server import SimpleXMLRPCServer
import redis
import os
import urllib.request

WORKERS = {}
WORKER_ID = 0
r = redis.Redis()

logging.basicConfig(level=logging.INFO)

server = SimpleXMLRPCServer(
    ('localhost', 9000),
    logRequests=True,
    allow_none=True)


def start_worker():
    global r
    while True:
        task = r.lpop('cua')
        if task != None:
            aux = str(task).split("'")[1]
            file = aux.split(',')[1]
            if aux.split(',')[0] == 'CountingWords':
                countingWords(file)
            elif aux.split(',')[0] == 'WordCount':
                wordCount(file)


def countingWords(file):


    for line in urllib.request.urlopen(file):
        print (line)

def wordCount(file):
    return


def create_worker():
    global WORKERS
    global WORKER_ID

    proc = Process(target=start_worker, args=())
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
    server.register_function(put_task)
    server.register_function(eliminate_worker)
    server.register_function(create_worker)
    server.register_function(workersList)
    try:
        print('Use Control-C to exit')
        os.system('cmd /k "py -m http.server" &')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')


if __name__ == "__main__":
    main()
