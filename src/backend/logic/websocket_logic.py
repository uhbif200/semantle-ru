from fastapi import WebSocket
import random
import logging
import grpc
from morph_pb2 import (
    MorphMsg,
    WordMsg,
    WordInitRequest,
    WordInitResponse,
    SimilarityRequest,
    SimilarityResponse
)
import morph_pb2_grpc

import enum

GAME_SERVICE_ADDRESS = "localhost:50051"

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebsocketGameSession] = {}

    async def connect(self, websocket: WebSocket) -> int:
        await websocket.accept()
        unique_id = self.gen_id()
        self.active_connections[unique_id] = WebsocketGameSession(websocket, unique_id)
        return unique_id
                
    def disconnect(self, id: int):
        logging.info(f"Отключение игровой сессии {id}")
        del self.active_connections[id]

    async def send_personal_message(self, message: str, id: int):
        await self.active_connections[id].websocket.send_text(message)

    async def broadcast(self, message: str):
        for session in self.active_connections.values():
            await session.websocket.send_text(message)

    def gen_id(self) -> int:
        unique_id = 0 
        while (unique_id == 0 or unique_id in self.active_connections.keys()):
            unique_id = random.randint(100000000, 999999999)
        return unique_id
    
class WebsocketGameSession:
    def __init__(self, websocket: WebSocket, id: int):
        self.websocket = websocket
        self.game_session = GameSession()
        self.id = id
        logging.info(f"Создана игровая сессия {self.id}")
        
    def __del__(self):
        logging.info(f"Удалена игровая сессия {self.id}")
        
#TODO наверное, стоит убрать логику игровой сессии отсюда вместе со всеми импортами
class GameState(enum.Enum):
    uninitialized = 0,
    gameplay = 1,
    win = 2
    
class NoConnection(Exception):
    "No connection with GRPC server"
    pass;

#TODO нормально реализовать обработку ошибок grpc    
#TODO разделить логику от обмена данными на два класса
class GameSession:
    def __init__(self) -> None:
        self.channel = grpc.insecure_channel(GAME_SERVICE_ADDRESS)
        self.client = morph_pb2_grpc.MorphModelServiceStub(self.channel)
        self.state = GameState.uninitialized
        self.word = ""
        self.similar_words = {str: float}
        self.history = {str: float}
        
    def __del__(self) :
        self.channel.close()
        
    def resetGame(self) : 
        self.word = ""
        self.similar_words = {}
        self.history = {}
        self.state = GameState.uninitialized
    
    def initWord(self):
        request = WordInitRequest(morph = MorphMsg.NOUN, similar_words_count = 20)
        try:
            response = self.client.WordInit(request)
        except Exception:
            raise NoConnection
            
        self.word = response.word.text
        self.similar_words = {wordSim.word.text: wordSim.similarity for wordSim in response.similar_words}
        self.state = GameState.gameplay

    def handleWord(self, word : str) -> float:
        if self.state == GameState.uninitialized or self.state == GameState.win:
            self.initWord()
            
        #Если слово уже было в истории, то вернем сразу
        if word in self.history:
            return self.history[word]
        
        result = self.__checkSimilarity(word)
        if not result:
            return None
        
        self.history[word] = result
        if result == 1.0:
            self.state = GameState.win
            #TODO тут можно праздновать победу
        return result
    
    def __checkSimilarity(self, word : str) -> float:
        similarity_request = SimilarityRequest(original_word = WordMsg(text = self.word, morph = MorphMsg.UNKN), test_word = WordMsg(text = word, morph = MorphMsg.UNKN))
        try:
            similarity_response = self.client.Similarity(similarity_request)
            return round(similarity_response.word.similarity, 4)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                logging.warning("Неверные аргументы запроса: " + e.details())
            else: 
                logging.warning("Произошла ошибка gRPC: " + e)
        return None
    
    def getHint(self) -> (str, float):
        for word, similarity in reversed(self.similar_words.items()):
            if not word in self.history:
                self.history[word] = similarity
                return (word, similarity)
        return None
            
if __name__ == "__main__":
    session = GameSession()
        
    while True:
        word = str(input())
        if word == "q":
            break
        if word == "h":
            hint = session.getHint()
            if hint == None:
                print("Подсказки закончились")
            else:
                print(hint[0] + " " + str(hint[1]) )
            continue
        result = session.handleWord(word)
        if result == None:
            continue
        print(f"{word} {result} {session.state.name}")
        if session.state == GameState.win:
            session.resetGame()