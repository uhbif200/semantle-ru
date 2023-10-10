import gensim, logging
import zipfile, wget, os
import pymorphy2
import random
import enum

class Morph(enum.Enum):
    ANY = 0
    UNKN = 1
    VERB = 2
    NOUN = 3
    PROPN = 4
    ADJ = 5
    INFN = 5
    PRTF = 6
    NUM = 7,
    INTJ = 8,
    X = 9,
    SYM = 10,
    ADJF = 11,
    PREP = 12,
    ADVB = 13,
    PRCL = 14,
    NPRO = 15,
    CONJ = 16,
    PRED = 17,
    NUMR = 18,
    ADJS = 19,
    GRND = 20,
    ADV = 21

class Word:
    def __init__(self, text = "", morph: Morph = Morph.ANY):
        self.text = text
        self.morph = morph
    def __str__(self):
        return self.text + '_' + self.morph.name

class MorphModelHandler:
    def __init__(self):
        self.model = self.__load_model()

    def similarity(self, word: Word, test_word: Word) -> float:
        return self.model.similarity(str(word), str(test_word))
    
    def get_similar_words(self, word: Word, count: int = 1) -> list[Word]:
        similar_words = []
        for similar_word, similarity in self.model.most_similar(positive = [str(word)], topn = count):
            word, morph = similar_word.split('_')
            similar_words.append((Word(word, Morph[morph]), similarity))
        return similar_words
    
    def word_is_in_model(self, word: Word) -> bool:
        return word.text + '_' + word.morph.name in self.model.index_to_key
        
    def __load_model(self):
        model_url = 'http://vectors.nlpl.eu/repository/11/180.zip'
        archeive_file = model_url.split('/')[-1]
        if os.path.isfile("res/morph_service/model.bin"):
            logging.info("Модель найдена")
        else:
            logging.info("Модель не найдена")
            logging.info("Архив с моделью загружается")
            m = wget.download(model_url)
            with zipfile.ZipFile(archeive_file, 'r') as archive:
                archive.extract('model.bin', path="res/morph_service")
            os.remove(archeive_file)
        return gensim.models.KeyedVectors.load_word2vec_format("res/morph_service/model.bin", binary=True)
        
class WordAnalyser():
    def __init__(self):
        self.morph_analyser = pymorphy2.MorphAnalyzer()
        
    def convert_to_word(self, word: str) -> Word:
        parsed_word = self.morph_analyser.parse(word)[0]
        morph = Morph.UNKN
        if parsed_word.tag.POS in Morph.__members__:
            morph = Morph[parsed_word.tag.POS]
        return Word(parsed_word.normal_form, morph)
        
    def morph_determine(self, word: str) -> Morph:
        parsed_word = self.morph_analyser.parse(word)[0]
        morph = parsed_word.tag.POS
        if parsed_word.tag.POS in Morph.__members__:
            return Morph[parsed_word.tag.POS]
        return Morph.UNKN
    
    def normalize(self, word: str) -> str:
        return self.morph_analyser.parse(word)[0].normal_form
        
    def append_morph(self, word: str) -> str:
        return word + '_' + self.morph_determine(word)

    def append_morph(self, word: Word) -> Word:
        word.morph = self.morph_determine(word.text)
        return word

# формат файла для генератора слов:
# words_pool.txt
# слово, часть речи, сложность
# нож NOUN 1.0
# банан NOUN 0.4

class WordFromGenerator(Word):
    def __init__(self, word: str, morph: Morph, difficulty: float) -> None:
        super().__init__(word, morph)
        self.difficulty = difficulty

class WordGenerator():
    def __init__(self):
        self.__word_pool = self.__load_words()
        
    def __load_words(self) -> list[WordFromGenerator]:
        word_pool = []
        with open('res/morph_service/words_pool.txt', 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            for line in lines:
                word_data = line.split()
                if len(word_data) != 3:
                    continue
                word_pool.append(WordFromGenerator(word_data[0], Morph[word_data[1]], float(word_data[2])))
        logging.info("Загружено %i слов для генератора", len(word_pool))
        return word_pool
    
    def get_random_word(self, morph: Morph = Morph.ANY) -> WordFromGenerator:
        if morph == Morph.ANY:
            return random.choice(self.__word_pool)
        words_with_morph = [word for word in self.__word_pool if word.morph == morph]
        return random.choice(words_with_morph)
            
