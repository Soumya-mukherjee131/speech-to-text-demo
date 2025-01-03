from nltk.corpus import cmudict

# Load CMU Pronouncing Dictionary
pronouncing_dict = cmudict.dict()
# print(pronouncing_dict["example"])
# Output: [['IH0', 'G', 'Z', 'AE1', 'M', 'P', 'L']]

def get_phonemes(text):
    """
    Converts input text into a sequence of phonemes using the CMU Pronouncing Dictionary.
    Words not in the dictionary are replaced with placeholders.
    """
    words = text.lower().split()  # Split text into words and convert to lowercase
    phoneme_sequence = []

    for word in words:
        if word in pronouncing_dict:
            # Join phonemes for the word
            phoneme_sequence.append(" ".join(pronouncing_dict[word][0]))
        else:
            # Placeholder for words not found in the dictionary
            phoneme_sequence.append(f"[{word}]")

    return " | ".join(phoneme_sequence)  # Separate words with a pipe for readability
sample_text = "I want to learn coding"
phonemes = get_phonemes(sample_text)
print(phonemes)
# Example Output: 'AY1 | W AO1 N T | T UW1 | L ER1 N | K OW1 D IH0 NG'
