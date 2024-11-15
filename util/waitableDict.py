from threading import Condition


class WaitableDict:
    def __init__(self):
        self._data = {}
        self._condition = Condition()

    def put(self, key, value):
        with self._condition:
            self._data[key] = value
            self._condition.notify_all()  # Notifica que um novo item foi adicionado

    def get(self, key):
        with self._condition:
            while key not in self._data:
                self._condition.wait()  # Espera até que a chave esteja disponível
            return self._data[key]
