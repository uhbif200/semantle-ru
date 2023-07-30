import grpc
from semantleru_pb2 import (
    Morph,
    Word,
    WordInitRequest,
    WordInitResponse,
    SimilarityResponse
)
import semantleru_pb2_grpc

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')

def plot_similar_words(original_word, similar_words):
    x = range(0, len(similar_words))
    y = []
    for word in similar_words:    
        y.append(word.similarity)
    plt.plot(x,y,label=original_word)

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        plt.figure()
        client = semantleru_pb2_grpc.MorphModelServiceStub(channel)
        i = 0
        while i < 20:
            print("_____WORD INIT_____")
            word_init_request = WordInitRequest(morph=Morph.NOUN, similar_words_count = 10)
            word_init_response = client.WordInit(word_init_request)
            print(f"Получено слово {word_init_response.word.text}, часть речи {word_init_response.word.morph}")
            plot_similar_words(word_init_response.word.text, word_init_response.similar_words)
            i += 1  
        plt.show()

if __name__ == "__main__":
    run()