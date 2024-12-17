from threading import Condition
from src.request import Request


class Scheduler:
    '''
        Escalonador de requisições.

        Ordena a fila de requisições de acordo com a prioridade.
    '''
    def __init__(self):
        self._queue : list[Request] = list()
        self._condition = Condition()

    def __reschedule(self):
        '''
            Reordenação da fila
        '''
        self._queue.sort(key=lambda r: r.getPriority(), reverse=True)

    def get(self) -> Request:
        '''
            Retorna uma requisição, caso exista na fila.
        '''
        with self._condition:
            while not self._queue:
                self._condition.wait()  # Espera até que a requisição esteja disponível
            return self._queue.pop(0)

    def put(self, request:Request):
        '''
            Adiciona uma requisição na fila de requisições
        '''
        with self._condition:
            self._queue.append(request)
            self.__reschedule()
            self._condition.notify_all() # Notifica que um novo item foi adicionado