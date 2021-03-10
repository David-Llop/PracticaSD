from multiprocessing import Process, Lock
import redis

WORKERS = {}
FREE_WORKERS = {}
WORKER_ID = 0
r = redis.Redis()

def start_worker(id, lock)
    global r
    while(True)
        tasca = r.blpop()
        lock.acquire()
        # fer tasca
        lock.release()


def create_worker()
    global WORKERS
    global WORKER_ID
    global FREE_WORKERS

    lock = Lock()
    proc = Process(target=start_worker, args=(WORKER_ID, lock))
    proc.start()
    WORKERS[WORKER_ID] = proc
    FREE_WORKERS[WORKER_ID] = lock

    WORKER_ID+=1

def eliminate_worker(id)
    global WORKERS
    global WORKER_ID
    global FREE_WORKERS

    FREE_WORKERS[id].acquire()
    WORKERS[WORKER_ID].join()
    FREE_WORKERS[id].release()

def put_task(task)
    global r
    r.rpush(cua, task)
 