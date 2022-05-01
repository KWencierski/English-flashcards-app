from flashcard_creation_error import FlashcardCreationError
from bs4 import BeautifulSoup
import requests
import os


def _split_polish_words_with_comma(polish_words):
    """
    :param polish_words:
    :return: list of separated polish words
    """
    return polish_words.replace(', ', ';').split(';')


class Flashcard:
    def __init__(self, new_word, polish_words=None, definition=None, example=None):
        self.english_word = new_word
        if polish_words is None:  # creating a flashcard with getting data from online dictionary
            try:
                self._get_data_from_online_dictionary()
            except:
                raise FlashcardCreationError(f'Error! Flashcard with word {self.english_word} cannot be created.')

        else:
            self._load_polish_words(polish_words)
            self.definition = definition
            self.example = example

    def _get_data_from_online_dictionary(self):
        """
        Gets polish_words, definition and examples from online dictionary and stores them in corresponding attributes
        :return: None
        """
        source = requests.get('https://dictionary.cambridge.org/dictionary/english-polish/' + self.english_word,
                              headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(source, 'html.parser')
        self.polish_words = _split_polish_words_with_comma(soup.find('span', class_='dtrans-se').text.strip())
        self.definition = soup.find('div', class_='db').text.strip()
        examples = []
        for i, example in enumerate(soup.find_all('div', class_='dexamp')):
            if i == 3:
                break
            examples.append(example.text.strip())

        self.example = ''
        if len(examples) == 0:
            self.example = '---'
            print('Unfortunately there are no examples available for this word, '
                  'but you can add yours in the modifying section of the main menu')
            input()
        else:
            self._choose_example(examples)

    def _censor_example(self):
        """
        Replaces self.english_word in example with *** and stores it in self.example
        :return: None
        """
        self.example = self.example.replace(self.english_word, '***')
        self.example = self.example.replace(self.english_word[:-1], '***')

    def _choose_example(self, examples):
        """
        Prints 3 examples of sentences containing self.english_word and asks the user to choose one of them to save
        :param examples: list of 3 examples (str)
        :return: nothing
        """
        print("Choose an example to save:")
        for i, example in enumerate(examples, start=1):
            print(f'{i}. {example}')
        while True:
            choice = input()
            if '1' in choice:
                self.example = examples[0]
                break
            elif '2' in choice:
                self.example = examples[1]
                break
            elif '3' in choice:
                self.example = examples[2]
                break
            else:
                print('Incorrect input! Try again:')
        self._censor_example()

    def _load_polish_words(self, polish_words):
        """
        Splits polish_words using a '/' sign and saves them to self.polish_words as a list of strings
        :param polish_words: (str)
        :return: nothing
        """
        self.polish_words = polish_words.split('/')

    def get_flashcard_summary(self):
        """
        Returns all the attributes of the flashcard
        :return: (str)
        """
        summary = self.english_word + '\n'
        summary += ' / '.join(self.polish_words) + '\n'
        summary += self.definition + '\n'
        summary += self.example
        return summary
