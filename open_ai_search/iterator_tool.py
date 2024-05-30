from threading import Thread
from typing import Iterable, List
from queue import Queue

END_FLAG: str = '<|eoq|>'


def enqueue_elements(q: Queue, iterator: Iterable, idx: int):
    for each in iterator:
        q.put((idx, each))
    q.put(END_FLAG)


def merge_iterators(iterators: List[Iterable]) -> Iterable:
    """
    Merge some iterators into one parallel iterator
    :param iterators: List of iterators
    :return: One iterators
    """
    q = Queue()

    thread_list: List[Thread] = []
    for idx, iterator in enumerate(iterators):
        thread_list.append(thread := Thread(target=enqueue_elements, args=(q, iterator, idx)))
        thread.start()

    sentinel_count = 0
    while sentinel_count < len(iterators):  # Wait for both iterators to be fully processed
        element = q.get()
        if element == END_FLAG:
            sentinel_count += 1
        else:
            yield element

    for t in thread_list:
        t.join()
