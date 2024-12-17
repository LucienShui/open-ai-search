import asyncio
from asyncio import Task, create_task
from typing import Any, Tuple, Dict, Union, Optional, AsyncIterable


class IterEnd:
    pass


class AsyncParallelIterator:
    def __init__(self, iterator_dict: Dict[str, Union[AsyncIterable[Any], Task]] = None,
                 iterator_cnt: Optional[int] = None, timeout: float = 0.1, return_done: bool = False):
        self.q: asyncio.Queue[Any] = asyncio.Queue()
        self.task_dict: Dict[str, Task] = {}

        self.end_count: int = 0
        self.iterator_cnt: Optional[int] = iterator_cnt
        self.timeout: float = timeout
        self.return_end: bool = return_done

        for name, iterator in (iterator_dict or {}).items():
            self.add(name, iterator)

    def __del__(self):
        for task in self.task_dict.values():
            task.cancel()

    @staticmethod
    async def enqueue_iterator(q: asyncio.Queue[Any], name: Union[int, str], iterator: AsyncIterable):
        try:
            async for each in iterator:
                await q.put((name, each))
            await q.put((name, IterEnd))
        except Exception as e:
            await q.put((name, e))

    @staticmethod
    async def enqueue_func(q: asyncio.Queue[Any], name: Union[int, str], task: Task):
        try:
            result = await task
            await q.put((name, result))
            await q.put((name, IterEnd))
        except Exception as e:
            await q.put((name, e))

    def add(self, name: str, iterator_or_coroutine: Union[AsyncIterable[Any], Task]):
        assert name not in self.task_dict, f"task {name} already exists"
        if isinstance(iterator_or_coroutine, Task) or asyncio.iscoroutine(iterator_or_coroutine):
            self.task_dict[name] = create_task(self.enqueue_func(self.q, name, iterator_or_coroutine))
        else:
            self.task_dict[name] = create_task(self.enqueue_iterator(self.q, name, iterator_or_coroutine))

    async def __anext__(self) -> Tuple[str, Any]:
        stop_count = (self.iterator_cnt or len(self.task_dict))
        while self.end_count < stop_count:
            name, value = await self.q.get()
            if isinstance(value, Exception):
                raise value
            if value == IterEnd:
                self.end_count += 1
                if not self.return_end:
                    continue
            return name, value
        raise StopAsyncIteration

    def __aiter__(self):
        return self
