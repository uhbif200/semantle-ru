import gensim, logging
import zipfile, wget, os
import pymorphy2
import random
import re

word_generation_max_attempts = 100

class MorphModelHandler:
    def __init__(self):
        self.__model = self.__load_model()
        self.__morph_analyzer = pymorphy2.MorphAnalyzer()
        self.__russian_words = self.__read_words_from_file()
        
    def morph_determine(self, word: str) -> str:
        parsed_word = self.__morph_analyzer.parse(word)[0]
        return parsed_word.tag.POS 
    
    def append_morph(self, word: str) -> str:
        return word + '_' + self.morph_determine(word)
    
    def similarity(self, word, test_word) -> float:
        return self._model.similarity(word, test_word)
    
    def get_random_word(self, morph = "ANY"):
        attempts = 0
        word: str
        word_match = False
        while attempts < word_generation_max_attempts and not word_match:
            attempts += 1
            index = random.randint(0, len(self.__russian_words) - 1)
            word = self.__russian_words[index]
            word_morph = self.morph_determine(word)
            if not is_word_russian(word.split('_')[0]):
                continue
            if not (morph == "ANY" or morph == word_morph):
                continue
            if not self.word_is_in_model(word + '_' + word_morph):
                continue
            word_match = True
        logging.info("Сегенерировано слово: %s, попыток: %i", word, attempts)
        return word
    
    def get_similar_words(self, word: str, count: int = 1):
        return self.__model.most_similar(positive = [word], topn = count)
    
    def get_similar_words_same_morph(self, word: str, count: int = 1):
        splitted_word = word.split('_')
        candidates = self.__model.most_similar(positive = [word], topn = count * 2)
        filtered = [(similar_word, similarity) for similar_word, similarity in candidates if similar_word.endswith(splitted_word[1])]
        #обрезаем лишнее
        if len(filtered) > count:
            truncate = len(filtered) - count
            filtered = filtered[:-truncate]
        return filtered
    
    def word_is_in_model(self, word: str) -> bool:
        return word in self.__model.index_to_key
            
    def __read_words_from_file(self):
        with open('russian_words.txt', 'r', encoding='utf-8') as file:
            # Читаем содержимое файла и разделяем на строки
            lines = file.read().splitlines()

            # Возвращаем список слов из строк, удаляя лишние пробелы
            words_list = [word.strip() for word in lines]
        return words_list
        
    def __load_model(self):
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
        return gensim.models.KeyedVectors.load_word2vec_format("model.bin", binary=True)
        
def is_word_russian(word: str) -> bool:
    russian_letters_pattern = re.compile(r'^[а-яА-ЯёЁ]+$')
    return bool(russian_letters_pattern.match(word))