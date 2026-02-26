import os
import math
import pandas as pd
from collections import Counter


def get_ngrams(tokens, n):
    """
    Generate n-grams from a list of tokens.
    """
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def calculate_mmi_for_ngrams(segmented_text_string, min_n=3, max_n=5, min_freq=5):
    """
    Calculate Multi-character Mutual Information (MMI) for n-grams.
    Iterates through n-grams of length min_n to max_n, computes the probability
    of binary splits, and calculates the MMI score.
    """
    # Parse the space-delimited text into discrete tokens
    tokens = segmented_text_string.split()
    total_tokens = len(tokens)

    # Pre-calculate token and sub-gram frequencies to optimize speed
    print("Pre-calculating sub-gram frequencies...")
    sub_gram_counters = {}
    for k in range(1, max_n):
        sub_gram_counters[k] = Counter(get_ngrams(tokens, k))

    all_mmi_results = []

    # Iterate through specified n-gram lengths (e.g., 3 to 5)
    for n in range(min_n, max_n + 1):
        print(f"Calculating MMI for {n}-grams...")
        ngrams_list = get_ngrams(tokens, n)
        ngram_counts = Counter(ngrams_list)

        for gram_tuple, freq in ngram_counts.items():
            if freq < min_freq:
                continue  # Filter out low-frequency noise

            p_xyz = freq / total_tokens
            split_probs = []

            # Calculate probabilities for all possible binary splits of the n-gram
            for k in range(1, n):
                left_part = gram_tuple[:k]
                right_part = gram_tuple[k:]

                p_left = sub_gram_counters[k].get(left_part, 0) / total_tokens
                p_right = sub_gram_counters[n - k].get(right_part, 0) / total_tokens
                split_probs.append(p_left * p_right)

            # Calculate the arithmetic mean of the split probabilities
            avg_split_prob = sum(split_probs) / len(split_probs) if split_probs else 1

            # Calculate MMI: log2( P(whole) / avg_split_prob )
            mmi_value = math.log2(p_xyz / avg_split_prob) if avg_split_prob > 0 else 0

            if mmi_value > 0:
                all_mmi_results.append({
                    'n-gram_length': n,
                    'word': "".join(gram_tuple),
                    'frequency': freq,
                    'MMI': round(mmi_value, 4)
                })

    df = pd.DataFrame(all_mmi_results)
    if not df.empty:
        df = df.sort_values(by='MMI', ascending=False)
    return df

# Example Usage:
# with open('segmented_corpus.txt', 'r', encoding='utf-8') as f:
#     text_content = f.read()
# mmi_df = calculate_mmi_for_ngrams(text_content, min_n=3, max_n=5, min_freq=20)
# mmi_df.to_csv('MMI_Results.csv', index=False, encoding='utf-8-sig')