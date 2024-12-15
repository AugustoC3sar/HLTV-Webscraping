from threading import Condition
from src.request import Request

class Storage:
    '''
        Classe responsável pelo armazenamento de requisições já realizadas.
    '''
    def __init__(self):
        self._data : list[Request] = list()
        self._condition = Condition()
    
    def put(self, request:Request):
        '''
            Adiciona uma requisição na lista.
        '''
        with self._condition:
            self._data.append(request)
            self._condition.notify_all()
    
    def get(self, url):
        '''
            Retorna a requisição realizada para uma dada url.
        '''
        with self._condition:
            # Aguardar enquanto a solicitação desejada não estiver na lista
            while True:
                request = next((r for r in self._data if r.getUrl() == url), None)
                if request:
                    self._data.remove(request)  # Remover o item quando encontrado
                    return request
                # Caso não tenha encontrado o item, aguardar até que algo seja adicionado
                self._condition.wait()