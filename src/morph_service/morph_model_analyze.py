from morph_model_handler import MorphModelHandler

model = MorphModelHandler()

morphs = []
for model_word in model.model.index_to_key:
    word, morph = model_word.split('_')
    if not morph in morphs:
        morphs.append(morph)
        print(morph + " " + word)
    