import os
import random
from database import Database

PATH = 'C:/Users/kajte/PycharmProjects/angielskiv2/data.csv'

database = Database(PATH)


def clear_console():
    """
    :return: None
    """
    os.system('cls')


def crate_list_with_remaining_word_indexes(dictionary):
    """
    Creates a list of indexes of the words that wasn't correctly translated even once.
    :param dictionary: dictionary where a key is a word index and a value is a number of how many times the word was
                       correctly translated
    :return: list of indexes of the words that wasn't correctly translated even once
    """
    return [key for key, value in dictionary.items() if value < 1]


def summarize_learning_session(scores, stage):
    """
    :param stage: (int) current stage of flashcards
    :param scores: dictionary of scores, where key is an index of a word and value is number that tells how many times
                   the word was translated
    :return: None
    """
    words_learned = [key for key, value in scores.items() if value == 2]
    database.move_to_higher_stage(words_learned, stage)
    number_of_words_learned = len(words_learned)
    total_number_of_words = len(scores)
    print('Good job!')
    print(f'Words learned: {number_of_words_learned}/{total_number_of_words} '
          f'({round(number_of_words_learned / total_number_of_words * 100, 2)}%)')

    input()


def summarize_revising_session(scores):
    """
    :param scores: dictionary of scores, where key is an index of a word and value is number that tells how many times
                   the word was translated
    :return: None
    """
    forgotten_words = [key for key, value in scores.items() if value == 0]
    database.move_to_first_stage_from_third_stage(forgotten_words)
    number_of_forgotten_words = len(forgotten_words)
    total_number_of_words = len(scores)
    print('Good job!')
    print(f'Forgotten words: {number_of_forgotten_words}/{total_number_of_words} '
          f'({round(number_of_forgotten_words / total_number_of_words * 100, 2)}%)')
    input()


def test_english_word(word_index, flashcards):
    """
    Displays english word and waits for a polish translation of the word.
    Instead of translation the user can type special letters:
    - 'l' to get a hint in a form of first letters of the expected answer
    - 's' to get example of the word used in a sentence
    - 'd' to get definition of the word
    After using one of these letters score of current word won't be increased
    :param word_index: (int) index of the word
    :param flashcards: list of Flashcards
    :return: (bool) True if answer was correct
    """
    clear_console()
    print(flashcards[word_index].english_word)
    letters_counter = 1  # How many letters should be displayed when a user submits the letter l
    while True:
        answer = input()
        if answer == 'l':  # Printing first letter_counter letters of the correct answer
            print(flashcards[word_index].polish_words[0][:letters_counter])
            letters_counter += 1
        elif answer == 's':  # Printing sentence with the word
            print(flashcards[word_index].example)
        elif answer == 'd':  # Printing definition of the word
            print(flashcards[word_index].definition)
        elif answer in flashcards[word_index].polish_words:  # if answer is correct
            print('Correct!')
            print(flashcards[word_index].definition)
            print(flashcards[word_index].example)
            input()
            if letters_counter == 1:
                return True
            else:
                return False

        else:  # if answer is wrong
            possible_answers = ' / '.join(flashcards[word_index].polish_words)
            print(possible_answers)
            print(flashcards[word_index].definition)
            print(flashcards[word_index].example)
            input()
            return False


def test_polish_word(word_index):
    """
    Displays polish word and waits for a english translation of the word.
    Instead of translation the user can type special letters:
    - 'l' to get a hint in a form of first letters of the expected answer
    - 's' to get example of the word used in a sentence
    - 'd' to get definition of the word
    After using one of these letters score of current word won't be increased
    :param word_index: (int) index of the word
    :return: (bool) True if answer was correct
    """
    clear_console()
    print(' / '.join(database.second_stage_flashcards[word_index].polish_words))
    letters_counter = 1  # How many letters should be displayed when a user submits the letter l
    while True:
        answer = input()
        if answer == 'l':  # Printing first letter_counter letters of the correct answer
            print(database.second_stage_flashcards[word_index].english_word[:letters_counter])
            letters_counter += 1
        elif answer == 's':  # Printing sentence with the word
            print(database.second_stage_flashcards[word_index].example)
        elif answer == 'd':  # Printing definition of the word
            print(database.second_stage_flashcards[word_index].definition)
        elif answer == database.second_stage_flashcards[word_index].english_word:  # if answer is correct
            print('Correct!')
            print(database.second_stage_flashcards[word_index].definition)
            print(database.second_stage_flashcards[word_index].example)
            input()
            if letters_counter == 1:
                return True
            else:
                return False

        else:  # if answer is wrong
            print(database.second_stage_flashcards[word_index].english_word)
            print(database.second_stage_flashcards[word_index].definition)
            print(database.second_stage_flashcards[word_index].example)
            input()
            return False


def start_learning(stage):
    """
    Tests all the words in the given stage in a random order 2 times and then tests all the words again that wasn't
    correctly translated even once and saves the modified database.
    :param stage: (int) stage of learning (1 for learning English to Polish, 2 the other way around)
    :return: None
    """
    if stage == 1:
        flashcards = database.first_stage_flashcards
    else:
        flashcards = database.second_stage_flashcards
    # Dictionary that stores how many times each word was correctly guessed
    scores = {i: 0 for i in range(len(flashcards))}
    if len(scores) == 0:
        print('There are no words to learn!')
        input()
        return

    order = crate_list_with_remaining_word_indexes(scores)
    for i in range(2):  # Test all words 2 times
        random.shuffle(order)
        for word_index in order:
            if stage == 1:
                if test_english_word(word_index, flashcards):
                    scores[word_index] += 1
            else:
                if test_polish_word(word_index):
                    scores[word_index] += 1
    while True:
        order = crate_list_with_remaining_word_indexes(scores)
        random.shuffle(order)
        if not order:  # End learning when all the words was correctly translated 2 times
            clear_console()
            summarize_learning_session(scores, stage)
            break
        for word_index in order:  # Testing only words that wasn't guessed correctly even once
            if stage == 1:
                if test_english_word(word_index, flashcards):
                    scores[word_index] += 1
            else:
                if test_polish_word(word_index):
                    scores[word_index] += 1
    database.save_data()


def start_revising(number_of_words):
    """
    Tests all the words from the third stage in a random order 2 times and then tests all the words again that wasn't
    correctly translated even once and saves the modified database.
    :param number_of_words: (int) number of words to revise
    :return: None
    """
    # Dictionary that stores how many times each word was correctly guessed
    scores = {i: 0 for i in random.sample(range(len(database.third_stage_flashcards)), number_of_words)}
    if len(scores) == 0:
        print('There are no words to learn!')
        input()
        return

    order = crate_list_with_remaining_word_indexes(scores)
    for i in range(2):  # test all words 2 times
        random.shuffle(order)
        for word_index in order:
            if test_english_word(word_index, database.third_stage_flashcards):
                scores[word_index] += 1
    forgotten_words = crate_list_with_remaining_word_indexes(scores)  # Words that wasn't correctly translated even once
    while True:
        order = crate_list_with_remaining_word_indexes(scores)
        random.shuffle(order)
        if not order:  # End learning when all the words was correctly translated 2 times
            clear_console()
            for word_index in forgotten_words:
                scores[word_index] = 0
            summarize_revising_session(scores)
            break
        for word_index in order:  # Testing only words that wasn't translated correctly even once
            if test_english_word(word_index, database.third_stage_flashcards):
                scores[word_index] += 1
    database.save_data()


def ask_for_revising_details():
    """
    Asks a user for the number of words that they want to revise and starts revising.
    :return: None
    """
    print('How many words to revise:')
    number_of_words = input()
    is_number_correct = False
    while not is_number_correct:
        if not number_of_words.isdecimal():
            print('Wrong input!')
        elif int(number_of_words) > len(database.third_stage_flashcards):
            print('There are not that many words to revise!')
        else:
            start_revising(int(number_of_words))
            return
        input()
        clear_console()
        print('How many words to revise:')
        number_of_words = input()


def add_new_word_manually():
    """
    Asks and add a new flashcard to the database.
    :return: None
    """
    print('Type an English word:')
    english_word = input()
    print('Type a Polish translation:')
    polish_word = input()
    print('Type a definition:')
    definition = input()
    print('Type an example:')
    example = input()
    database.add_flashcard(english_word, polish_word, definition, example)
    print('Flashcard added!')
    input()


def add_new_word():
    """
    Displays menu and add a new flashcard to the database.
    :return: None
    """
    clear_console()
    print('Type new english word:')
    new_word = input()
    result = database.add_new_word(new_word)
    if result == 1:
        clear_console()
        print(database.get_flashcard(new_word).get_flashcard_summary())
        print(f'\nSuccessfully added a word {new_word}!')
        print('\nWould you like to modify anything?')
        display_modifying_menu(database.get_flashcard(new_word))
    elif result == 0:
        print(f'\nA flashcard with the word {new_word} already exists!')
        input()
    else:
        print(f'\nCannot add a word {new_word}!')
        print('\nWould you like to adda flashcard manually? (yes / no)')
        decision = input().lower()
        if decision == 'yes' or decision == 'y':
            add_new_word_manually()


def change_english_translation(flashcard):
    """
    :param flashcard: (Flashcard)
    :return: None
    """
    print('Enter new english translation:')
    new_word = input()
    if database.change_english_word(flashcard, new_word):
        print('\nEnglish translation changed!')
    else:
        print(f'\nA flashcard with the word {new_word} already exists!')
    input()


def change_polish_translation(flashcard):
    """
    :param flashcard: (Flashcard)
    :return: None
    """
    print('Enter new polish translation:')
    new_word = input()
    print('\nSelect polish translation you want to change:')
    for i, polish_translation in enumerate(flashcard.polish_words, start=1):
        print(f'{i}. {polish_translation}')
    while True:
        polish_translation_index = input()
        if polish_translation_index.isnumeric() and \
                database.change_polish_word(flashcard, int(polish_translation_index) - 1, new_word):
            print('\nPolish translation changed!')
            input()
            break
        else:
            print('Wrong input! Try again:')


def add_polish_translation(flashcard):
    """
    Adds a new Polish translation to the already existing ones.
    :param flashcard: (Flashcard)
    :return: None
    """
    print('Enter new polish translation:')
    new_word = input()
    if database.add_polish_translation(flashcard, new_word):
        print('\nPolish translation added!')
    else:
        print(f'\nThe translation {new_word} already exists for this flashcard!')
    input()


def delete_polish_translation(flashcard):
    """
    :param flashcard: (Flashcard)
    :return: None
    """
    if len(flashcard.polish_words) < 2:
        print('Cannot delete polish translation from flashcard with only one polish translation!')
    else:
        print('\nSelect polish translation you want to delete:')
        for i, polish_translation in enumerate(flashcard.polish_words, start=1):
            print(f'{i}. {polish_translation}')
        while True:
            polish_translation_index = input()
            if polish_translation_index.isnumeric() and \
                    database.delete_polish_word(flashcard, int(polish_translation_index) - 1):
                print('\nPolish translation deleted!')
                input()
                break
            else:
                print('Wrong input! Try again:')


def change_definition(flashcard):
    """
    :param flashcard: (Flashcard)
    :return: None
    """
    print('Enter new definition:')
    new_definition = input()
    database.change_definition(flashcard, new_definition)
    print('\nDefinition changed!')
    input()


def change_example(flashcard):
    """
    :param flashcard: (Flashcard)
    :return: None
    """
    print('Enter new example:')
    new_example = input()
    database.change_example(flashcard, new_example)
    print('\nExample changed!')
    input()


def delete_flashcard(flashcard):
    """
    :param flashcard: (Flashcard)
    :return: None
    """
    print('Are you sure?')
    print('1. Yes')
    print('2. No')
    decision = input()
    if decision == '1' or decision.lower() == 'yes':
        if database.delete_flashcard(flashcard):
            print('\nFlashcard deleted!')
        else:
            print('\nDeletion failed!')
        input()


def modify_word():
    """
    Asks for a word that a user want to modify and displays the modifying menu.
    :return: None
    """
    print('Type the english word you want to change:')
    flashcard = database.get_flashcard(input())
    if flashcard is None:
        print('There is no flashcard with this word in the database!')
        input()
    else:
        clear_console()
        print(flashcard.get_flashcard_summary())
        print('\nChoose an action to be performed:')
        display_modifying_menu(flashcard)


def display_modifying_menu(flashcard):
    """
    :param flashcard: (Flashcard)
    :return: None
    """
    print('1. Change the English translation')
    print('2. Change a Polish translation')
    print('3. Add a Polish translation')
    print('4. Delete a Polish translation')
    print('5. Change the definition')
    print('6. Change the example')
    print('7. Delete the flashcard')
    print('8. Go back')
    action = input()
    print()
    if action == '1':
        change_english_translation(flashcard)
    elif action == '2':
        change_polish_translation(flashcard)
    elif action == '3':
        add_polish_translation(flashcard)
    elif action == '4':
        delete_polish_translation(flashcard)
    elif action == '5':
        change_definition(flashcard)
    elif action == '6':
        change_example(flashcard)
    elif action == '7':
        delete_flashcard(flashcard)


def show_statistics():
    """
    Prints number of flashcards in each stage
    :return: None
    """
    clear_console()
    s1 = len(database.first_stage_flashcards)
    s2 = len(database.second_stage_flashcards)
    s3 = len(database.third_stage_flashcards)
    print(f'Number of flashcards in stage 1: {s1}')
    print(f'Number of flashcards in stage 2: {s2}')
    print(f'Number of flashcards in stage 3: {s3}')
    print(f'Total number of flashcards: {s1 + s2 + s3}')
    input()


while True:
    clear_console()
    print('\t\tMenu:')
    print('1. Learning (english to polish)')
    print('2. Learning (polish to english)')
    print('3. Revising already learned words')
    print('4. Add new word')
    print('5. Modify a word')
    print('6. Show statistics')
    print('7. Quit')
    action = input()

    clear_console()
    if '1' in action:
        start_learning(1)
    elif '2' in action:
        start_learning(2)
    elif '3' in action:
        ask_for_revising_details()
    elif '4' in action:
        add_new_word()
    elif '5' in action:
        modify_word()
    elif '6' in action:
        show_statistics()
    elif '7' in action:
        quit()
