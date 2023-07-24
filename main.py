import sys, os
import gensim, logging
import zipfile, wget
import pymorphy2
from pymorphy2 import MorphAnalyzer
import re
import random

def is_single_word(word: str) -> bool:
    if not re.match(r"^[a-zA-Zа-яА-Я]+$", word):
        return False
    return True

def load_model():
    model_url = 'http://vectors.nlpl.eu/repository/11/180.zip'
    archeive_file = model_url.split('/')[-1]
    if os.path.isfile("model.bin"):
        logging.info("Модель найдена")
    else:
        logging.info("Модель не найдена")
        logging.info("Архив с моделью загружается")
        m = wget.download(model_url)
        with zipfile.ZipFile(archeive_file, 'r') as archive:
            archive.extract('model.bin')
        os.remove(archeive_file)
    model = gensim.models.KeyedVectors.load_word2vec_format("model.bin", binary=True)
    return model

def morph_determine(word: str) -> str:
    if not hasattr(morph_determine, 'analyzer'):
        morph_determine.analyzer = pymorphy2.MorphAnalyzer()
    parsed_word = morph_determine.analyzer.parse(word)[0]
    return parsed_word.tag.POS

def append_morph(word: str) -> str:
    return word + '_' + morph_determine(word)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model = load_model()

words_pool = ['обезьяна_NOUN', 'космос_NOUN', 'клавиатура_NOUN', 'дыра_NOUN'] 

hidden_word = random.choice(words_pool)

print("Введите слово. Для выхода введите q")
word: str
while True:
    word = str(input())
    if word == 'q':
        exit() 
    if not is_single_word(word):
        print("Введите одно слово")
        continue
    else:
        word = append_morph(word)
        print("Введено слово", word)
        if word != hidden_word:
            try: 
                print(model.similarity(hidden_word, word))
            except KeyError:
                print("Слово не существует")
        else:
            print("Угадали!")