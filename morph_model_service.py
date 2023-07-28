import logging
import random
import grpc
import re
from concurrent import futures
import semantleru_pb2_grpc
import semantleru_pb2
from semantleru_pb2 import (
    Morph,
    WordInitResponse,
    SimilarityResponse
)
from morph_model.morph_model_handler import MorphModelHandler

class MorphModelService(semantleru_pb2_grpc.MorphModelService):
    def __init__(self) -> None:
        super().__init__()
        self._model_handler = MorphModelHandler()   
    def WordInit(self, request, context):
        logging.info("Получен запрос на слово %s", morph_to_str(request.morph))
        random_word = self._model_handler.get_random_word(morph = morph_to_str(request.morph))
        similar_words_gen = self._model_handler.get_similar_words_same_morph(random_word + '_' + morph_to_str(request.morph), 10)
        similar_words = []
        for (word, coef) in similar_words_gen:
            similar_words.append(word)
        return WordInitResponse(word = random_word, morph = request.morph, similar_words = similar_words)
    def Similarity(self, request, context):
        logging.info("Similarity")
        return SimilarityResponse(similarity = 0)

def morph_to_str(morph: Morph) -> str:
    return semantleru_pb2._MORPH.values_by_number[morph].name

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    semantleru_pb2_grpc.add_MorphModelServiceServicer_to_server(
        MorphModelService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    logging.info("Сервер запущен")
    server.wait_for_termination()
    
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    serve()