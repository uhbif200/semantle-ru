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

def get_new_word(grpc_client) -> WordMsg:
    print("_____WORD INIT_____")
    word_init_request = WordInitRequest(morph=MorphMsg.NOUN, similar_words_count = 10)
    word_init_response = grpc_client.WordInit(word_init_request)
    print(f"Получено слово {word_init_response.word.text}, часть речи {word_init_response.word.morph}")
    return word_init_response.word

def check_similarity(grpc_client, original_word: WordMsg, test_word: WordMsg) -> float:
    similarity_request = SimilarityRequest(original_word = original_word, test_word = test_word)
    try:
        similarity_response = grpc_client.Similarity(similarity_request)
        return similarity_response.word.similarity
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            print("Неверные аргументы запроса:", e.details())
        else: 
            print("Произошла ошибка gRPC:", e)
    return 0

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        client = morph_pb2_grpc.MorphModelServiceStub(channel)
        original_word = get_new_word(client)
        while True:
            word = str(input())
            if word == 'q':
                break
            
            similarity = round(check_similarity(client, original_word, WordMsg(text = word, morph = MorphMsg.UNKN)), 2)
            if similarity == 1:
                print("Угадали.")
                original_word = get_new_word(client)
            else:
                print("Схожесть ", similarity)
if __name__ == "__main__":
    run()