from string import punctuation, ascii_lowercase, whitespace
from unicodedata import category

def is_recipe_english(text):
    """
    Function that checks if text contains give percentage of an english alphabet chars (ascii)
    """
    symbols_cleaned_text = ''.join(c for c in text if category(c) not in ['P', 'S', 'C'])
    only_chars = [
        x for x in symbols_cleaned_text
        if x not in punctuation
           and x not in whitespace
           and not x.isdigit()
    ]

    if len(only_chars) == 0:
        return False

    english_chars = sum(1 for x in only_chars if x.lower() in ascii_lowercase)
    english_percentage = english_chars / len(only_chars) * 100

    #TODO: Adjust if needed this is fault tolerant for a couple of lines in non english alphabet (ascii)
    return english_percentage > 97