import datetime

__author__ = 'Bassil Khatib and Michael Hundt'

from queue import Queue  # FIFO Queue
import time
from threading import Thread
from threading import Lock
import a3_3_db_manager as db_manager


class storage_thread(Thread):
    static_Queue = Queue()
    lock = Lock()
    interrupted = False

    def __init__ (self, db_connection, sleeping_time=4):
        Thread.__init__ (self)
        self._name = "storage_thread"
        self.db_connection = db_connection
        self.sleeping = sleeping_time


    def queue_is_empty(self):
        self.lock.acquire()
        empty = self.static_Queue.empty()
        self.lock.release()
        return empty

    def run(self):
        print("...started storage_thread")
        while not self.interrupted:
            if not self.queue_is_empty():
                self.dequeue(self.db_connection)
            else:
                print("\tQueue is empty")
                print("...sleep for {0} seconds".format(self.sleeping))
                time.sleep(self.sleeping)
                print("...woke up")
                print("\tQueue size: {}".format(self.static_Queue.qsize()))
                if (self.queue_is_empty()):
                    #still empty, interrupt
                    print("...still empty! Stop storage thread ...")
                    break

        print("storage_Thread stopped")



    def dequeue(self, connection):
        self.lock.acquire()
        values = self.static_Queue.get()
        self.lock.release()

        db_manager.store_to_db(self.db_connection.cursor(), "pages", values)
        self.db_connection.commit()
        print("...dequeued, Queue size: "+str(self.static_Queue._qsize()))


    def enqueue(self, data):
        print("Enqueue")
        self.lock.acquire()
        print("...queue locked")
        for i,val in enumerate(data):
            self.static_Queue.put(val)
        print("...{0} items were added to queue".format(i))
        self.lock.release()
        print("finished enqueue")


def main():

    db_manager.generate_test_data(15)
    try:
        connection = db_manager.connect_to_db()
    except:
        print("Could not connect to DB")

    t1 = storage_thread(connection)
    t1.start()
    t1.enqueue(data=db_manager.get_values())
    print()



if __name__ == '__main__':
    main()


