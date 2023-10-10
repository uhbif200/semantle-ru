from morph_model_handler import (
    WordAnalyser,
    MorphModelHandler,
    Word,
    Morph
)

import re

words_pool_file = "res/morph_service/russian_words.txt"
output_file = "res/morph_service/words_pool.txt"

class ErrorWord:
    def __init__(self, word: str, error_reason: str):
        self.word = word
        self.error_reason = error_reason
    def __str__(self):
        return '\"' + self.word + '\"' + " Причина ошибки: " + self.error_reason

# Прогресбар для красоты

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()       

def integral(points: list[float]) -> float:
    return sum(points) / len(points)    

if __name__ == "__main__":
    with open(words_pool_file, 'r', encoding='utf-8') as file:
        single_word_re = re.compile(r'^[а-яА-Я]+$')
        words = file.read().splitlines()
        print(f'Прочитано {len(words)} потенциальных слов')
        word_analyser = WordAnalyser()
        morph_model = MorphModelHandler()
        error_pool = []
        words_pool = []
        i = 0;
        for word in words:
            printProgressBar(i, len(words), prefix = 'Progress:', suffix = 'Complete', length = 50, printEnd="\r")
            i+=1
            word.lower()
            if not bool(single_word_re.match(word)):
                error_pool.append(ErrorWord(word, 'Слово не является одим словом'))
                continue

            converted_word = word_analyser.convert_to_word(word)
            if converted_word.morph == Morph.UNKN \
                or converted_word.morph == Morph.ANY \
                or converted_word.morph == Morph.X:
                error_pool.append(ErrorWord(converted_word.text, "Часть речи не определена"))
                continue
            
            if not morph_model.word_is_in_model(converted_word):
                error_pool.append(ErrorWord(converted_word.text, "Модель не содержит слова"))
                continue
            
            similar_words = morph_model.get_similar_words(converted_word, 100)
            points = [similarity for word, similarity in similar_words]
            difficulty = integral(points)
            words_pool.append([converted_word, difficulty])
        #Пропускаем строчку, а то прогресбар глючит
        print()
        words_pool.sort(key=lambda difficulty: difficulty[1], reverse=True)
        print(f"Прошло {len(words_pool)} слов")
        print(f"Число ошибок: {len(error_pool)}")
        with open(output_file, 'w', encoding='utf-8') as o_file:
            for word in words_pool:
                o_file.write(word[0].text + " " + word[0].morph.name + " " + str(word[1]) + "\n")