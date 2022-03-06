from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import Array
import random

NPROD = 3   #Número de productores
N = 10      #Número de productos que va a producir cada productor antes de parar

#------------------------------------------------------------------------------
#Funciones auxiliares

def allNegative(storage):
    """
    Dada una lista de integers comprueba que ninguno de ellos sea -1
    """
    for cell in storage:
        if cell >= 0:
            return False
    return True

def firstNonNegative(storage):
    """
    Dada una lista de integers devuelve la primera posición en la que haya un número 
    no negativo. En caso de no haber, devuelve -1
    """
    for i,el in enumerate(storage):
        if el >= 0:
            return i
    return -1

#------------------------------------------------------------------------------
#Funciones que necesitan mutex

def add_data(storage, index, mutex):
    mutex.acquire()
    try:
        storage[index] = storage[index] + random.randint(1,20)
        print("Producer{} produced {}".format(index,storage[index]))
    finally:
        mutex.release()

def get_data(storage, empties, non_empties, mutex):
    mutex.acquire()
    pos = firstNonNegative(storage)
    minim = storage[pos]
    try:
        for i,el in enumerate(storage):
            if el < minim and (el != -1):
                minim = el
                pos = i
        print("Taking value {} from Producer{}".format(minim,pos))
    finally:
        mutex.release()
        empties[pos].release()
        for i,ne in enumerate(non_empties):
            if i != pos:
                ne.release()
    return minim

#------------------------------------------------------------------------------
#Productor y consumidor/merge

def producer(storage, index, empty, non_empty, mutex):
    for v in range(N+1):
        empty.acquire()
        add_data(storage, index, mutex)
        non_empty.release()
    storage[index] = -1


def merge(storage, empties, non_empties, mutex):
    results = []
    end = False
    while not(end):
        for ne in non_empties:
            ne.acquire()
        if not(allNegative(storage)):
            dato = get_data(storage, empties, non_empties, mutex)
            results.append(dato)
        else:
            end = True
    print(results)

#------------------------------------------------------------------------------

def main():
    storage = Array('i', NPROD)

    non_empties = [Semaphore(0) for i in range(NPROD)]
    empties = [BoundedSemaphore(1) for i in range(NPROD)]
    mutex = Lock()

    prodlst = [Process(target=producer,args=(storage, i, empties[i], non_empties[i], mutex)) for i in range(NPROD) ]
    m = [Process(target=merge,args=(storage, empties, non_empties, mutex))]

    for p in prodlst + m:
        p.start()

    for p in prodlst + m:
        p.join()

if __name__ == '__main__':
    main()
