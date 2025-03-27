import spacy
import random
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.char as nac
import nltk
# nltk.download('averaged_perceptron_tagger_eng')
# import pyinflect

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")
random.seed(42)

# Rule 1.1 First-Word Variation: Using spaCy to detect the starting phrase.
# Tokanise the sentence to identify and change the starting phrase
def rule_1(sentence):
    # If sentence starts with "Write a function", replace using an alternative.
    alternatives = [
        "Develop a function", "Implement a function", "Create a function",
        "Design a function", "Construct a function", "Build a function",
        "Write a script", "Write a Python script", "Formulate a function", "Generate a function"
    ]
    if sentence.startswith("Write a function") or sentence.startswith("Write a python function"):
        # Replace the span using spaCy tokenization (more robust than plain replace)
        try:
            sentence = sentence.split('Write a function')[1]
        except:
            sentence = sentence.split('Write a python function')[1]
        return random.choice(alternatives) + sentence
    return sentence

def rule_3_1(sentence):
    return sentence.upper()

def rule_3_2(sentence, style="bold"):
    """
    Returns the sentence wrapped in Markdown formatting according to style.
    
    :param sentence: The input string to be formatted.
    :param style: The type of Markdown formatting: 'bold', 'italic',
                  'inline_code', or 'block_code'.
    :return: The sentence wrapped in the specified Markdown style.
    """
    if style == "bold":
        return f"**{sentence}**"
    elif style == "italic":
        return f"*{sentence}*"
    elif style == "inline_code":
        return f"`{sentence}`"
    elif style == "block_code":
        return f"```\n{sentence}\n```"
    else:
        # If the style is unrecognized, return the original sentence
        return sentence


# Rule 5.4 Extra Word Addition: Insert an extra clarifying word using spaCy noun chunks.
def rule_4(sentence, replace_word='Well-optimized'):
    doc = nlp(sentence)
    for chunk in doc.noun_chunks:
        # Insert "Well-optimized" before the first noun chunk.
        insert_point = chunk.root.idx
        return sentence[:insert_point] + replace_word + ' ' + sentence[insert_point:]
    return sentence

def rule_5(sentence, function_name='func()'):
    sentence = sentence.split(' ')
    if 'function' in sentence:
        sentence[sentence.index('function')] = function_name
    return ' '.join(sentence)

# Rule 4.1 Word Order Swap: Using spaCy to swap adjacent tokens.
# transformer and tokanesation to swap some words
def rule_6_1(sentence):
    doc = nlp(sentence)
    tokens = [token.text for token in doc]
    if len(tokens) >= 2:
        i = random.randint(0, len(tokens)-2)
        tokens[i], tokens[i+1] = tokens[i+1], tokens[i]
    return " ".join(tokens)

# Rule 3.1 Synonym Substitution: Using nlpaug with WordNet augmenter.
def rule_6_2(sentence):
    aug = naw.SynonymAug(aug_src='wordnet')
    augmented = aug.augment(sentence)
    return augmented[0] if augmented else sentence

# Rule 6.1 Introduce Spelling Error: Using nlpaug’s character augmenter.
# using nac to introduce errors
def rule_6_3(sentence):
    aug = nac.OcrAug()  # This augmenter simulates OCR errors (typos).
    augmented = aug.augment(sentence)
    return augmented[0] if augmented else sentence


# Rule 7.3 Unnecessary Punctuation: Insert an extra punctuation mark using nlpaug.
def rule_6_4(sentence):
    punctuation = ["!", "?", ",", ";"]
    pos = random.randint(0, len(sentence))
    return sentence[:pos] + random.choice(punctuation) + sentence[pos:]

# Generate independent mutations using the defined rules.
def generate_mutations(prompt):
    mutations = []
    mutations.append((rule_1(prompt)))
    mutations.append((rule_3_1(prompt)))
    mutations.append((rule_3_2(prompt, "bold")))
    mutations.append((rule_4(prompt, 'Well-optimized')))
    mutations.append((rule_5(prompt, 'func()')))
    mutations.append((rule_5(prompt, '')))
    mutations.append((rule_6_1(prompt)))
    mutations.append((rule_6_2(prompt)))
    mutations.append((rule_6_3(prompt)))
    mutations.append((rule_6_4(prompt)))
    return mutations


if __name__ == "__main__":
    # Example prompt
    input_prompt = "Write a python function to find the last digit when factorial of a divides factorial of b."

    mutated_outputs = generate_mutations(input_prompt)

    print("Original Prompt:")
    print(input_prompt)
    print("\nList of Mutated Outputs:")
    for label, mutation in mutated_outputs:
        print("-" * 80)
        print(f"{label}:")
        print(mutation)