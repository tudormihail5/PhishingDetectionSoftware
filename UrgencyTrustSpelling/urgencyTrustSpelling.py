from bs4 import BeautifulSoup
import re
import pandas as pd
from textblob import TextBlob
from spellchecker import SpellChecker
import spacy
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import string
from concurrent.futures import ProcessPoolExecutor, as_completed

# Load the English language model from spaCy
nlp = spacy.load("en_core_web_sm")

def get_text_from_url(url):
    driver = None
    try:
        # Configure Selenium WebDriver
        options = Options()
        # Run in headless mode
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        # Determine the current working directory and set path for the Chrome driver
        current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        driver_path = os.path.join(current_directory, 'chromedriver')
        service = Service(executable_path=driver_path)
        # Initialize the Chrome WebDriver with the specified optionss
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        # Set a 10 seconds timeout and wait for page to load completely
        timeout = 10
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        sourcecode = driver.page_source
        soup = BeautifulSoup(sourcecode, 'lxml')
        # Add spaces between tags
        for tag in soup.find_all():
            tag.append(' ')
        # Extract the text
        text = soup.get_text(separator=' ')
        # Remove new line characters and other unwanted whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text, len(text)
    except Exception as e:
        return e
    finally:
        if driver is not None:
            driver.quit()

def detect_urgency_cues(text):
    urgency_keywords = ['urgent', 'immediate', 'action required', 'final notice', 'limited time', 'limited offer', 'hurry', 'act now', 'rush', 'last chance', 'final close-out', 'going out-of-business', 'one day only', 'clearance', 'pay now', 'don\'t delay', 'do not delay', 'now or never', 'don\'t miss', 'don\'t wait', 'do not wait', 'do not miss', 'offer expires', 'once in a lifetime', 'promptness bonus', 'prices going up', 'one time only', 'before is\'s gone', 'before it is gone', 'today only', 'act today', 'buy now', 'security threat alert', 'stop deductions now', 'take this opportunity', 'take the survey', 'act promptly', 'seize this', 'subscription has expired', 'expired subscription', 'subscription expired', 'time-sensitive', 'what are you waiting for', 'alert', 'join today', 'join us today', 'ends soon', 'now is the time', 'now or never', 'right now']
    negations = ['not', 'don\'t', 'never', 'no']
    # Number of words around the keyword to consider for context
    window_size = 3
    urgency_count = 0
    words = text.split()
    for keyword in urgency_keywords:
        # Find all whole word matches, ignoring case differences
        for match in re.finditer(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            # Get the start and the end positions of each found keyword in the text
            start, end = match.span()
            # Finding the indices of words around the keyword
            start_index = len(text[:start].split())
            end_index = len(text[:end].split())
            # Extracting a window of words around the found keyword; max and min ensure it does not go below 0 or exceed the length of text
            before_window = words[max(0, start_index - window_size):start_index]
            after_window = words[end_index:min(len(words), end_index + window_size)]
            # Checking if any negation word is a separate token in either window
            if not any(negation in before_window or negation in after_window for negation in negations):
                urgency_count += 1
    return urgency_count

def detect_trust_cues(text):
    trust_keywords = ['secure', 'verified', 'authentic', 'official', 'reliable source', 'trust', 'trustworthy', 'protect', 'suspend', 'warn', 'fraudulent', 'card', 'account', 'redeem your prize', 'offer you', 'give you', 'invite you', 'our appreciation', 'our gratitude', 'incredibly', 'undoubtedly', 'exclusive offer', 'claim', 'gift', 'special offer', 'thrilling', 'your loyalty', 'chance to win', 'incredible', 'our appreciation', 'our gratitude', 'are you interested', 'do you want', 'ultimate', 'unbeatable', 'unreal', 'exciting', 'outstanding', 'amazing', 'inheritance', 'inherit', 'congratulations', 'reward', 'you\'ve been selected', 'you have been selected', 'hottest', 'fabulous', 'unreal', 'take the survey', 'visit our website', 'appealing', 'are you interested', 'are you looking for', 'not a scam', 'not scam', 'click here', 'click below', 'guarantee', 'really', 'click the link', 'guarantees', 'guaranteed', 'opportunity', 'make money', 'makes money', 'use the link', 'incredible', 'unique', 'special']
    negations = ['not', 'don\'t', 'never', 'no']
    # Number of words around the keyword to consider for context
    window_size = 3
    trust_count = 0
    words = text.split()
    for keyword in trust_keywords:
        # Find all whole word matches, ignoring case differences
        for match in re.finditer(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            # Get the start and the end positions of each found keyword in the text
            start, end = match.span()
            # Finding the indices of words around the keyword
            start_index = len(text[:start].split())
            end_index = len(text[:end].split())
            # Extracting a window of words around the found keyword; max and min ensure it does not go below 0 or exceed the length of text
            before_window = words[max(0, start_index - window_size):start_index]
            after_window = words[end_index:min(len(words), end_index + window_size)]
            # Checking if any negation word is a separate token in either window
            if not any(negation in before_window or negation in after_window for negation in negations):
                trust_count += 1
    return trust_count

def load_names(csv_file):
    try:
        df = pd.read_csv(csv_file, low_memory=False)
        first_names = df.get('First names')
        second_names = df.get('Second Names')
        if first_names is not None:
            first_names_list = first_names.tolist()
        else:
            first_names_list = []
        if second_names is not None:
            second_names_list = second_names.tolist()
        else:
            second_names_list = []
        return set(first_names_list + second_names_list)
    except Exception as e:
        return e

def load_dictionary(txt_file):
    try:
        # Read the entire dictionary file once and store its content (both utf8 and latin1)
        with open(txt_file, 'r', encoding='utf-8') as file:
            dictionary_words = set(file.read().lower().split())
    except UnicodeDecodeError:
        try:
            with open(txt_file, 'r', encoding='latin-1') as file:
                dictionary_words = set(file.read().lower().split())
        except Exception as e:
            return e
    return dictionary_words

def is_excluded_entity(word, doc):
    # While the first character is a punctuation mark, slice it off
    while len(word) > 0 and word[0] in string.punctuation:
        word = word[1:]
    # While the last character is a punctuation mark, slice it off
    while len(word) > 0 and word[-1] in string.punctuation:
        word = word[:-1]
    # Check if the word is part of an excluded named entity
    excluded_labels = ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE', 'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']
    for ent in doc.ents:
        if word in ent.text and ent.label_ in excluded_labels:
            return True
    return False
    
def detect_spelling_errors1GB(text, language='en-GB'):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    names_path = os.path.join(current_directory, 'names.csv')
    names = load_names(names_path)
    # TextBlob library with UK English, also checking for names
    blob = TextBlob(text.lower())
    errors = []
    for word in blob.words:
        if word.upper() not in names:
            corrected_word = word.correct()
            if corrected_word != word:
                errors.append(word)
    return errors

def detect_spelling_errors1US(text, language='en-US'):
    # TextBlob library with US English
    blob = TextBlob(text.lower())
    errors = []
    for word in blob.words:
        corrected_word = word.correct()
        if corrected_word != word:
            errors.append(word)
    return errors

def detect_spelling_errors2(text):
    # SpellChecker library, also checking using the spaCy model
    spell = SpellChecker()
    doc = nlp(text)
    words = text.split()
    errors = []
    for word in words:
        # While the first character is a punctuation mark, slice it off
        while len(word) > 0 and word[0] in string.punctuation:
            word = word[1:]
        # While the last character is a punctuation mark, slice it off
        while len(word) > 0 and word[-1] in string.punctuation:
            word = word[:-1]
        # Exclude the words that contain digits, to exclude possible product models
        if not any(char.isdigit() for char in word):
            if not is_excluded_entity(word, doc) and word not in spell:
                errors.append(word)
    return errors

def detect_using_dictionary(text):
    words = text.split()
    errors = []
    current_directory = os.path.dirname(os.path.abspath(__file__))
    dictionary_path = os.path.join(current_directory, 'dictionary.txt')
    dictionary_words = load_dictionary(dictionary_path)
    for word in words:
        if word.lower() not in dictionary_words:
            errors.append(word)
    return errors

def urgency_trust_spelling(url):
    text, length = get_text_from_url(url)
    # Sum the 2 cues scores
    urgency_trust_score = detect_urgency_cues(text) + detect_trust_cues(text)
    # Apply all the spelling checkers and use parallel execution for speeding up the analysis
    with ProcessPoolExecutor(max_workers=4) as executor:
        # Submit tasks for execution
        future1GB = executor.submit(detect_spelling_errors1GB, text)
        future1US = executor.submit(detect_spelling_errors1US, text)
        future2 = executor.submit(detect_spelling_errors2, text)
        future_dictionary = executor.submit(detect_using_dictionary, text)
        # Collect results as they complete
        for future in as_completed([future1GB, future1US, future2, future_dictionary]):
            if future == future1GB:
                spelling_errors1GB = future.result()
            elif future == future1US:
                spelling_errors1US = future.result()
            elif future == future2:
                spelling_errors2 = future.result()
            elif future == future_dictionary:
                spelling_errors_dictionary = future.result()
    # Intersect all the errors lists to avoid the false positives
    intersection_set1 = set(spelling_errors1GB).intersection(set(spelling_errors1US))
    intersection_set2 = intersection_set1.intersection(set(spelling_errors2))
    intersection_set = intersection_set2.intersection(set(spelling_errors_dictionary))
    # Consider the unfinished words, e.g., beginning of news
    spelling_errors = [word for word in intersection_set if not word.endswith('…')]
    spelling_score = len(spelling_errors)
    if urgency_trust_score != 0 and length / urgency_trust_score < 320 or spelling_score > 0:
        return 'P'
    return 'L'

def cues_testing(text, parameter):
    length = len(text)
    urgency_trust_score = detect_urgency_cues(text) + detect_trust_cues(text)
    if urgency_trust_score != 0 and length / urgency_trust_score < parameter:
        return 'P'
    return 'L'
