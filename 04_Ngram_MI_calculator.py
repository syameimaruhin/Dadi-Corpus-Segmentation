import math
import pandas as pd
from collections import Counter


def calculate_mixed_element_mi(segmented_text_string):
    """
    Calculate Mutual Information (MI) for mixed elements based on preliminary segmented text.
    """
    # Parse the space-delimited text into a sequence of discrete tokens
    tokens = segmented_text_string.split()
    total_tokens = len(tokens)

    # Generate continuous 2-gram pairs from tokens
    bigrams = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
    bigram_counts = Counter(bigrams)

    df = pd.DataFrame.from_dict(bigram_counts, orient='index', columns=['f_xy'])
    df.index.rename('2-gram', inplace=True)
    df.reset_index(inplace=True)

    # Filter frequencies >= 20
    df = df[df['f_xy'] >= 20]

    # Split tuples into x and y columns
    df[['gram_x', 'gram_y']] = pd.DataFrame(df['2-gram'].tolist(), index=df.index)

    # Dynamic frequency counting for individual elements
    df['f_x'] = df['gram_x'].apply(lambda x: segmented_text_string.count(x))
    df['f_y'] = df['gram_y'].apply(lambda y: segmented_text_string.count(y))

    # Calculate Mutual Information
    df['MI'] = df.apply(
        lambda row: math.log((row['f_xy'] * total_tokens) / (row['f_x'] * row['f_y']), 2)
        if (row['f_x'] * row['f_y']) > 0 else 0,
        axis=1
    )

    return df