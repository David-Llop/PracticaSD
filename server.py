from multiprocessing import Process, Lock
from xmlrpc.server import SimpleXMLRPCServer
from time import sleep
import logging
import os
import redis

WORKERS = {}
FREE_WORKERS = {}
WORKER_ID = 0
r = redis.Redis()

logging.basicConfig(level=logging.INFO)

server = SimpleXMLRPCServer(
    ('localhost', 9000),
    logRequests=True,
    allow_none=True)


def start_worker(id, lock):
    global r
    while True:
        task = r.blpop('cua')
        lock.acquire()
        print(task)
        lock.release()


def create_worker():
    global WORKERS
    global WORKER_ID
    global FREE_WORKERS

    lock = Lock()
    proc = Process(target=start_worker, args=(WORKER_ID, lock))
    proc.start()
    WORKERS[WORKER_ID] = proc
    FREE_WORKERS[WORKER_ID] = lock
    WORKER_ID += 1
    print(proc)
    return WORKER_ID - 1


def eliminate_worker(id):
    global WORKERS
    global WORKER_ID
    global FREE_WORKERS

    FREE_WORKERS[int(id)].acquire()
    WORKERS[int(id)].join()
    WORKERS.remove(WORKERS[int(id)])
    FREE_WORKERS.remove(FREE_WORKERS[int(id)])


def put_task(task):
    global r
    r.rpush('cua', task)

def main():
    server.register_function(put_task)
    server.register_function(eliminate_worker)
    server.register_function(create_worker)
    create_worker()
    try:
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')

if __name__ == "__main__":
    main()