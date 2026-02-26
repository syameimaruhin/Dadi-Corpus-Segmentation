def count_weight(segmented_list, reference_string):
    """
    Calculate the dynamic frequency weight of multi-character words
    in the provided reference string (str_doc or str_all).
    """
    weight = 0
    for word in segmented_list:
        if len(word) >= 2:
            # On-the-fly frequency counting using native string matching
            weight += reference_string.count(word)
    return weight


def bmm_tie_break(f_res, r_res, str_doc, str_all):
    """
    Bi-directional Maximum Matching (BMM) tie-breaking logic.
    Evaluates FMM and RMM results based on predefined heuristic rules.
    """
    # Rule 1: Return if identical
    if f_res == r_res:
        return f_res

    # Rule 2: Fewer total words
    if len(f_res) != len(r_res):
        return f_res if len(f_res) < len(r_res) else r_res

    # Rule 3: Longer maximum word length
    f_max_len = max([len(w) for w in f_res]) if f_res else 0
    r_max_len = max([len(w) for w in r_res]) if r_res else 0
    if f_max_len != r_max_len:
        return f_res if f_max_len > r_max_len else r_res

    # Rule 4: Higher frequency weight in the current document
    f_doc_weight = count_weight(f_res, str_doc)
    r_doc_weight = count_weight(r_res, str_doc)
    if f_doc_weight != r_doc_weight:
        return f_res if f_doc_weight > r_doc_weight else r_res

    # Rule 5: Higher frequency weight in the entire corpus
    f_all_weight = count_weight(f_res, str_all)
    r_all_weight = count_weight(r_res, str_all)
    if f_all_weight != r_all_weight:
        return f_res if f_all_weight > r_all_weight else r_res

    # Fallback to FMM
    return f_res