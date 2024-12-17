from src.priority import Priority

class Request:
    '''
        Classe para representar uma requisição no sistema.
    '''
    def __init__(self, url:str, priority:Priority):
        self._url = url
        self._priority = priority
        self._response = None

    def getUrl(self):
        '''
            Retorna a url da requisição (sem o host)
        '''
        return self._url

    def getPriority(self) -> int:
        '''
            Retorna a prioridade da requisição (valor)
        '''
        return self._priority.value

    def getResponse(self):
        '''
            Retorna a resposta da requisição
        '''
        return self._response

    def addResponse(self, response):
        '''
            Adiciona uma resposta a requisição.
        '''
        self._response = response