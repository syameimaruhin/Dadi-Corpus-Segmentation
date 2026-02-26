import itertools


# Note: load_variant_dict and generate_combinations are identical to 01_FMM_segmentation.py

def rmm_segmentation(sentence, dictionary_set, variant_lst, max_word_length=5):
    """
    Reverse Maximum Matching (RMM) segmentation with variant character handling.
    Matches from the end of the sentence to the beginning.
    """
    words = list(sentence)
    result = []
    end = len(words)
    current_length = max_word_length

    while end > 0:
        # Prevent index out of bounds
        if end < current_length:
            current_length = end

        word = ''.join(words[end - current_length:end])
        word_variants_list = []

        # Build variant combinations
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

        # Dictionary matching
        if any(combination in dictionary_set for combination in combinations):
            result.insert(0, word)  # Insert at the beginning for reverse matching
            end -= current_length
            current_length = max_word_length
        else:
            current_length -= 1
            if current_length <= 1:
                result.insert(0, words[end - 1])
                end -= 1
                current_length = max_word_length
    return result