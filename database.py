from flashcard import Flashcard
import pandas as pd
from flashcard_creation_error import FlashcardCreationError


class Database:
    def __init__(self, file_path):
        # fist stage is for learning polish translations of english words
        # second stage is for learning english translations of polish words
        # third stage is for revising already leaned words
        self.first_stage_flashcards, self.second_stage_flashcards, self.third_stage_flashcards \
            = self._load_data(file_path)
        self.flashcards = [self.first_stage_flashcards, self.second_stage_flashcards, self.third_stage_flashcards]

    def _load_data(self, file_path):
        """
        :param file_path: (str) path to
        :return: list of 3 list of Flashcards in a corresponding stage
        """
        data = None
        try:
            data = pd.read_csv(file_path, sep=';', encoding='utf8')
        except FileNotFoundError:
            print('File with given path does not exist!')
            exit()
        return self._split_data_to_stages(data)

    def _split_data_to_stages(self, data):
        """
        Splits data into 3 learning stages
        :param data: (DataFrame)
        :return: list of 3 list of Flashcards in a corresponding stage
        """
        flashcards = [[], [], []]
        for _, row in data.iterrows():
            row_stage = row['stage']
            if 0 <= row_stage <= 3:
                flashcards[row['stage'] - 1].append(self._create_flashcard_from_data(row))
            else:
                print('Stage cannot be smaller than 0 or higher than 3!')
                exit()
        return flashcards

    def _create_flashcard_from_data(self, data):
        """
        :param data: (DataFrame)
        :return: (Flashcard)
        """
        return Flashcard(data['english_word'], data['polish_words'], data['definition'], data['example'])

    def move_to_higher_stage(self, list_of_indexes, originate_stage):
        """
        :param list_of_indexes: list of indexes in one of the stages list
        :param originate_stage: (int)
        :return: None
        """
        list_of_indexes.sort(reverse=True)
        for i in list_of_indexes:
            if originate_stage == 1:
                self.second_stage_flashcards.append(self.first_stage_flashcards.pop(i))
            else:
                self.third_stage_flashcards.append(self.second_stage_flashcards.pop(i))

    def move_to_first_stage_from_third_stage(self, list_of_indexes):
        """
        :param list_of_indexes: list of indexes of third stage flashcards
        :return: None
        """
        list_of_indexes.sort(reverse=True)
        for i in list_of_indexes:
            self.first_stage_flashcards.append(self.third_stage_flashcards.pop(i))

    def save_data(self):
        data = []
        for i, stage in enumerate(self.flashcards, start=1):
            for flashcard in stage:
                data.append([flashcard.english_word, '/'.join(flashcard.polish_words), flashcard.example,
                             flashcard.definition, str(i)])
        df = pd.DataFrame(data, columns=['english_word', 'polish_words', 'example', 'definition', 'stage'])
        df.to_csv('data.csv', sep=';', index=False, encoding='utf8')

    def add_new_word(self, word):
        """
        Creates new Flashcard with the given word and saves it in self.first_stage_flashcards
        :param word: (str)
        :return: -1 when an error occurred when creating new Flashcard, 0 when there is already Flashcard with
                 the given english word in the database or 1 when there were no errors
        """
        if self.get_flashcard(word) is None:
            try:
                new_flashcard = Flashcard(word)
            except FlashcardCreationError:
                return -1
            self.first_stage_flashcards.append(new_flashcard)
            self.save_data()
            return 1
        else:
            return 0

    def get_flashcard(self, english_word):
        """
        Returns a Flashcard with given english word
        :param english_word: (str)
        :return: (Flashcard) if there is a Flashcard with given english_word in the database or None otherwise
        """
        for flashcard in self.first_stage_flashcards:
            if flashcard.english_word == english_word:
                return flashcard
        for flashcard in self.second_stage_flashcards:
            if flashcard.english_word == english_word:
                return flashcard
        for flashcard in self.third_stage_flashcards:
            if flashcard.english_word == english_word:
                return flashcard
        return None

    def change_english_word(self, flashcard, new_word):
        """
        :param flashcard: (Flashcard)
        :param new_word: (str)
        :return: 1 if a change was successful or 0 otherwise
        """
        if self.get_flashcard(new_word) is None:  # If there is no flashcard with this english word
            flashcard.english_word = new_word
            self.save_data()
            return 1
        else:
            return 0

    def change_polish_word(self, flashcard, polish_word_index, new_word):
        """
        :param polish_word_index: (int) index of the word that will be changed
        :param flashcard: (Flashcard)
        :param new_word: (str)
        :return: 1 if a change was successful or 0 otherwise
        """
        if 0 <= polish_word_index < len(flashcard.polish_words):
            flashcard.polish_words[polish_word_index] = new_word
            self.save_data()
            return 1
        else:
            return 0

    def add_polish_translation(self, flashcard, new_word):
        """
        :param flashcard: (Flashcard)
        :param new_word: (str)
        :return: 1 if an addition was successful or 0 otherwise
        """
        if new_word not in flashcard.polish_words:
            flashcard.polish_words.append(new_word)
            self.save_data()
            return 1
        else:
            return 0

    def delete_polish_word(self, flashcard, polish_word_index):
        """
        :param polish_word_index: (int) index of the word that will be changed
        :param flashcard: (Flashcard)
        :return: 1 if a deletion was successful or 0 otherwise
        """
        if 0 <= polish_word_index < len(flashcard.polish_words):
            flashcard.polish_words[polish_word_index].pop(polish_word_index)
            self.save_data()
            return 1
        else:
            return 0

    def change_definition(self, flashcard, new_definition):
        """
        :param flashcard: (Flashcard)
        :param new_definition: (str)
        :return: None
        """
        flashcard.definition = new_definition
        self.save_data()

    def change_example(self, flashcard, new_example):
        """
        :param flashcard: (Flashcard)
        :param new_example: (str)
        :return: None
        """
        flashcard.example = new_example
        self.save_data()

    def delete_flashcard(self, flashcard):
        """
        :param flashcard: (Flashcard)
        :return: 1 if a deletion was successful or 0 otherwise
        """
        for stage in self.flashcards:
            if flashcard in stage:
                stage.remove(flashcard)
                self.save_data()
                return 1
        return 0

    def add_flashcard(self, english_word, polish_word, definition, example):
        """
        Creates new Flashcard from given parameters and adds it to the database
        :param english_word: (str)
        :param polish_word: (str)
        :param definition: (str)
        :param example: (str)
        :return: None
        """
        self.flashcards[0].append(Flashcard(english_word, polish_word, definition, example))
        self.save_data()

