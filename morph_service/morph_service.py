import logging
import grpc
from concurrent import futures
import re

import morph_pb2
from morph_pb2 import (
    MorphMsg,
    WordMsg,
    SimilarWordMsg,
    WordInitResponse,
    SimilarityResponse
)

import morph_pb2_grpc
from morph_pb2_grpc import MorphModelService

from morph_model_handler import (
    MorphModelHandler, 
    WordAnalyser, 
    WordGenerator,
    Word,
    Morph
)

def word_to_msg(word: Word) -> WordMsg:
    return WordMsg(text = word.text, morph = word.morph.value)

def word_from_msh(word_msg: WordMsg) -> Word:
    return Word(word_msg.text, Morph(word_msg.morph))

class MorphModelService(MorphModelService):
    def __init__(self) -> None:
        super().__init__()
        self.model_handler = MorphModelHandler()
        self.word_analyser = WordAnalyser()
        self.word_generator = WordGenerator()
         
    def WordInit(self, request, context):
        morph = Morph(request.morph)
        logging.info("Получен запрос на генерацию слова с частью речи %s", morph.name)
        gen_word = self.word_generator.get_random_word(morph)
        similar_words_gen = self.model_handler.get_similar_words(gen_word, request.similar_words_count)
        similar_words = []
        for (word, similarity) in similar_words_gen:
            similar_words.append(SimilarWordMsg(word = word_to_msg(word), similarity = similarity))
        response = WordInitResponse(word = word_to_msg(gen_word))
        response.similar_words.extend(similar_words)
        return response
    
    def Similarity(self, request, context):
        orig_word = word_from_msh(request.original_word)
        test_word = word_from_msh(request.test_word)
        if not (verify_word(orig_word) and verify_word(test_word)):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Введите одно слово на русском")
            return 
        if orig_word.morph == Morph.UNKN:
            self.word_analyser.append_morph(orig_word)
        if test_word.morph == Morph.UNKN:
            self.word_analyser.append_morph(test_word)
        logging.info("Получен запрос на определение схожести слова %s и %s", orig_word, test_word)
        try: 
            similarity = self.model_handler.similarity(orig_word, test_word)
        except KeyError as e:
            logging.info("Не удалось определить схожесть слова, возможно слова нет в базе")
            status_code = grpc.StatusCode.INVALID_ARGUMENT
            status_details = "Не удалось определить схожесть слова, возможно слова нет в базе"
            context.abort(status_code, status_details)
            return
        logging.info("Схожесть %f", round(similarity, 2))
        return SimilarityResponse(word = SimilarWordMsg(word = word_to_msg(test_word), similarity = similarity))

def morph_to_str(morph: Morph) -> str:
    return morph_pb2._MORPH.values_by_number[morph].name

def verify_word(word: Word) -> bool:
    return is_word_russian(word.text)

def is_word_russian(word: str) -> bool:
    russian_letters_pattern = re.compile(r'^[а-яА-ЯёЁ]+$')
    return bool(russian_letters_pattern.match(word))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    morph_pb2_grpc.add_MorphModelServiceServicer_to_server(
        MorphModelService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    logging.info("Сервер запущен")
    server.wait_for_termination()
    
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    serve()