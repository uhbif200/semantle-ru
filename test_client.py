import grpc
from semantleru_pb2 import (
    Morph,
    WordInitRequest,
    WordInitResponse,
    SimilarityResponse
)
import semantleru_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        client = semantleru_pb2_grpc.MorphModelServiceStub(channel)
        print("_____WORD INIT_____")
        word_init_request = WordInitRequest(morph=Morph.NOUN)
        word_init_response = client.WordInit(word_init_request)
        print(f"Получено слово {word_init_response.word}, часть речи {word_init_response.morph}, схожие слова {word_init_response.similar_words}")

if __name__ == "__main__":
    run()