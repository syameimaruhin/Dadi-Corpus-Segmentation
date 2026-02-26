import itertools


def load_variant_dict(file_path):
    """
    Load the variant character dictionary.
    Returns a list of variant character groups.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data_str = f.readlines()[0]
        return data_str.split("|")


def generate_combinations(variants_list):
    """
    Generate all possible combinations of variant characters for a given string.
    """
    for variant in itertools.product(*variants_list):
        yield ''.join(variant)


def fmm_segmentation(sentence, dictionary_set, variant_lst, max_word_length=5):
    """
    Forward Maximum Matching (FMM) segmentation with variant character handling.
    """
    words = list(sentence)
    result = []
    start = 0
    current_length = max_word_length

    while start < len(words):
        word = ''.join(words[start:start + current_length])
        word_variants_list = []

        # Build variant combinations for each character in the current substring
        for char in word:
            char_variants_list = []
            if any(char in s for s in variant_lst):
                pos = [idx for idx, lst in enumerate(variant_lst) if char in lst]
                for idx in pos:
                    variants = variant_lst[idx]
                    for v in variants.split():
                        char_variants_list.extend(v)
                char_variants_list = list(set(char_variants_list))
                word_variants_list.append("".join(char_variants_list))
            else:
                word_variants_list.append(char)

        combinations = list(generate_combinations(word_variants_list))

        # Check if any variant combination exists in the dictionary
        if any(combination in dictionary_set for combination in combinations):
            result.append(word)
            start += current_length
            current_length = max_word_length
        else:
            current_length -= 1
            # If length reduces to 1, treat it as a single-character word or punctuation
            if current_length <= 1:
                result.append(words[start])
                start += 1
                current_length = max_word_length
    return result