import pymorphy2

def transform_dislike_statement(input_statement):
    # Iнiцiалiзуємо аналiзатор морфологiї
    morph = pymorphy2.MorphAnalyzer(lang='uk')
    # Словник замiн для особових займенникiв
    replace_words = { 'я': 'ти', 'ти': 'я', 'мене': 'тебе', 'тебе': 'мене', 'мiй': 'твiй', 'твiй': 'мiй', 'менi': 'тобi', 'тобi': 'менi' }

    words = input_statement.split()
    transformed_words = []

    for word in words:
    # Лематизацiя слова
        parsed_word = morph.parse(word)[0]

        if parsed_word.normal_form in replace_words:
            transformed_words.append(replace_words[parsed_word.normal_form])
        else:
            transformed_words.append(word)
            transformed_statement = ' '.join(transformed_words)
    # Додатковi корекцiї
    transformed_statement = transformed_statement.replace(', що', ' що')
    transformed_statement = transformed_statement.replace('вас', 'тебе')
    transformed_statement = transformed_statement.replace('.?', '?')
    return f"Чому саме тебе не задовольняє, що {transformed_statement}?"
    
def switch_person(verb):
    morph = pymorphy2.MorphAnalyzer(lang='uk')
    parsed_verb = morph.parse(verb)[0]
    verb_inflected = None
    if parsed_verb.tag.person == '1per':
        verb_inflected = parsed_verb.inflect({'2per'}).word
    elif parsed_verb.tag.person == '2per':
        verb_inflected = parsed_verb.inflect({'1per'}).word
    else:
        verb_inflected = verb
    return verb_inflected
        
    # Приклад використання


user_input = "я знаю, що ти знаєш, що я знаю."
response = transform_dislike_statement(user_input)
    # Знаходимо дiєслова та перетворюємо їх
words = user_input.split()
transformed_words = []
for word in words:
    if 'знаю' in word or 'знаєш' in word:
        verb = word.split()[0] # Вiдокремлюємо дiєслово для перетворення
        transformed_verb = switch_person(verb)
        transformed_word = word.replace(verb, transformed_verb)
        transformed_words.append(transformed_word)
    else:
        transformed_words.append(word)


response_with_transformed_verbs = ' '.join(transformed_words)
print(response_with_transformed_verbs)