import os
import numpy as np
from collections import Counter


# ==============================================================================
# Script 09: Fleiss' Kappa Calculation & Majority-Voting Adjudication
# Description: Calculates the Inter-Annotator Agreement (IAA) at the character
#              boundary level for multiple annotators (n > 2) and generates a
#              draft gold standard using majority voting. Tie conflicts (e.g., 2:2)
#              are marked with "[?]" for subsequent manual adjudication.
# ==============================================================================

def load_variant_dict(dict_path):
    """
    Reads the variant character dictionary file.
    Format requirement: Groups of variant characters separated by '|'.
    """
    variant_groups = []
    if not os.path.exists(dict_path):
        print(f"Warning: Dictionary file '{dict_path}' not found. Variant normalization will be skipped.")
        return variant_groups

    with open(dict_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Split into different variant groups using '|'
        parts = content.split('|')
        for part in parts:
            group = part.strip()
            if len(group) > 1:
                variant_groups.append(list(group))
    return variant_groups


def build_frequency_based_map(variant_groups, global_char_counts):
    """
    Builds an optimal mapping table based on global single-character frequencies.
    Identifies the most frequent character in each variant group to serve as the
    standard (Target), and maps the rest of the characters in the group to it.
    """
    variant_map = {}
    if not variant_groups:
        return variant_map

    for group in variant_groups:
        # Find the character with the highest frequency in the current annotated texts
        best_char = max(group, key=lambda x: global_char_counts.get(x, 0))
        for char in group:
            if char != best_char:
                variant_map[char] = best_char
    return variant_map


def extract_boundaries(segmented_text, variant_map):
    """
    Converts segmented text into a character sequence (with variant normalization applied)
    and a sequence of boundary labels.
    Label '1' indicates the end of a word (boundary), '0' indicates within a word.
    """
    tokens = segmented_text.split()
    chars = []
    boundaries = []

    for token in tokens:
        for i, char in enumerate(token):
            # Apply variant character normalization mapping
            normalized_char = variant_map.get(char, char)
            chars.append(normalized_char)

            # If it's the last character of the token, mark as a boundary (1)
            if i == len(token) - 1:
                boundaries.append(1)
            else:
                boundaries.append(0)

    return "".join(chars), boundaries


def fleiss_kappa(ratings_matrix):
    """
    Calculates Fleiss' Kappa for inter-annotator agreement.
    Formula: \kappa = \frac{\bar{P} - P_e}{1 - P_e}
    """
    N, k = ratings_matrix.shape
    n = np.sum(ratings_matrix[0])  # Number of annotators

    p_j = np.sum(ratings_matrix, axis=0) / (N * n)
    P_e = np.sum(p_j ** 2)
    P_i = (np.sum(ratings_matrix ** 2, axis=1) - n) / (n * (n - 1))
    P_bar = np.mean(P_i)

    # Prevent division by zero if there's perfect agreement by chance
    if P_e == 1.0:
        return 1.0

    return (P_bar - P_e) / (1 - P_e)


def process_annotations(file_paths, dict_path):
    """
    Main pipeline: Reads annotations, normalizes characters, aligns sequences,
    calculates Fleiss' Kappa, and generates the adjudicated text.
    """
    # 1. Pre-read all texts and calculate global character frequencies
    all_raw_texts = []
    global_counter = Counter()

    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            t = f.read()
            all_raw_texts.append(t)
            # Remove spaces and line breaks for accurate character frequency counting
            global_counter.update(t.replace(" ", "").replace("\n", "").replace("\r", ""))

    # 2. Build the variant character mapping table
    variant_groups = load_variant_dict(dict_path)
    variant_map = build_frequency_based_map(variant_groups, global_counter)
    print(f"Loaded {len(variant_groups)} variant groups, constructed {len(variant_map)} mapping rules.")

    # 3. Extract boundaries and check for character alignment across annotators
    all_boundaries = []
    base_chars = None

    for i, text in enumerate(all_raw_texts):
        chars, boundaries = extract_boundaries(text, variant_map)

        if base_chars is None:
            base_chars = chars
        else:
            # Strictly verify that all annotators segmented the exact same raw text
            if base_chars != chars:
                # Find the first mismatched index for debugging purposes
                diff_idx = next((j for j, (a, b) in enumerate(zip(base_chars, chars)) if a != b), -1)
                context = chars[max(0, diff_idx - 5): diff_idx + 5]
                raise ValueError(
                    f"Text misalignment detected! File '{file_paths[i]}' differs from the base file at character index {diff_idx} (Context: ...{''.join(context)}...). Please ensure raw texts are identical.")

        all_boundaries.append(boundaries)

    all_boundaries = np.array(all_boundaries)
    n_annotators, N_chars = all_boundaries.shape
    print(f"Detected {n_annotators} annotators, totaling {N_chars} characters.")

    # 4. Construct the Ratings Matrix for Kappa calculation
    # ratings_matrix shape: (N_chars, 2) -> [votes for '0' (no split), votes for '1' (split)]
    ratings_matrix = np.zeros((N_chars, 2), dtype=int)
    for i in range(N_chars):
        split_votes = np.sum(all_boundaries[:, i])
        ratings_matrix[i][0] = n_annotators - split_votes
        ratings_matrix[i][1] = split_votes

    # Calculate and output Fleiss' Kappa
    kappa = fleiss_kappa(ratings_matrix)
    print(f"==> Fleiss' Kappa: {kappa:.4f}")

    # 5. Generate Gold Standard Draft using Majority Voting
    adjudicated_text = []
    conflict_count = 0

    for i in range(N_chars):
        adjudicated_text.append(base_chars[i])
        split_votes = ratings_matrix[i][1]

        # Absolute majority agrees to split
        if split_votes > n_annotators / 2:
            adjudicated_text.append(" ")
        # Tie conflict (e.g., 2 vs 2), requires manual adjudication
        elif split_votes == n_annotators / 2:
            conflict_count += 1
            adjudicated_text.append("[?]")

    # Clean up double spaces if any, and strip trailing spaces
    final_text = "".join(adjudicated_text).replace("  ", " ").strip()
    print(f"Identified {conflict_count} instances of tie conflicts (marked with '[?]').")

    return final_text


# ================= Execution Block =================
if __name__ == "__main__":
    # Configuration: Replace with your actual file paths
    # Ensure these files are located in the same directory or provide absolute paths.
    file_list = ["anno1.txt", "anno2.txt", "anno3.txt", "anno4.txt"]
    dictionary_file = "Dadi_Corpus_Variant_Dictionary(ver1.0).txt"

    try:
        majority_result = process_annotations(file_list, dictionary_file)

        output_file = "gold_standard_draft.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(majority_result)

        print(f"\n✅ Adjudicated draft successfully exported to: {output_file}")
    except Exception as e:
        print(f"An error occurred during processing: {e}")