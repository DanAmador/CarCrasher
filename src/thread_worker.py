import queue
import threading


class ThreadQueueWorker:
    def __init__(self, worker_function):
        self.threads = []
        self.work_q = queue.Queue()
        for t in range(10):
            worker = threading.Thread(target=worker_function)
            worker.daemon = True
            self.threads.append(worker)

    def start_execution(self, timeout=None):
        for thread in self.threads:
            thread.start()

        if timeout is not None:
            for thread in self.threads:  # iterates over the threads
                thread.join(timeout)  # waits until the thread has finished work

    def push_to_queue(self, to_add):
        self.work_q.put(to_add)
