import os
import random
import pandas as pd


def proportional_stratified_sampling(metadata_excel_path, total_samples=100):
    """
    Perform proportional stratified sampling based on text category and century.
    Ensures the sampled texts represent the true distribution of the corpus.
    """
    print("Reading corpus metadata...")
    df = pd.read_excel(metadata_excel_path)

    # Extract century information from the sorting year (e.g., 1868 -> 19)
    if 'Century' not in df.columns:
        df['Century'] = (df['Sorting_Year'] // 100 + 1).astype(int)

    # Calculate the proportion of each (Category x Century) stratum
    strata_counts = df.groupby(['Category', 'Century']).size()
    strata_props = strata_counts / len(df)

    # Calculate target samples per stratum (minimum 1 to ensure coverage)
    samples_per_stratum = (strata_props * total_samples).round().astype(int)
    samples_per_stratum = samples_per_stratum.clip(lower=1)

    # Adjust total count if rounding caused it to exceed total_samples
    while samples_per_stratum.sum() > total_samples:
        max_stratum = samples_per_stratum.idxmax()
        samples_per_stratum[max_stratum] -= 1

    # Execute random sampling within each stratum
    sampled_dfs = []
    for (category, century), n in samples_per_stratum.items():
        stratum_df = df[(df['Category'] == category) & (df['Century'] == century)]
        if len(stratum_df) > 0:
            sampled_dfs.append(stratum_df.sample(min(n, len(stratum_df)), random_state=42))

    return pd.concat(sampled_dfs) if sampled_dfs else pd.DataFrame()


def extract_random_text_snippets(sampled_df, input_text_dir, snippet_length=100):
    """
    Extract a random continuous snippet of fixed length from the sampled files.
    """
    extracted_data = []

    for _, row in sampled_df.iterrows():
        # Construct filename based on metadata (adjust format as needed)
        filename = f"{row['Sorting_Year']}_{row['Document_Name']}_{row['Volume']}.txt"
        filepath = os.path.join(input_text_dir, filename)

        if not os.path.exists(filepath):
            print(f"File not found: {filename}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract random snippet
        if len(content) <= snippet_length:
            snippet = content  # Take whole text if shorter than required length
        else:
            start_idx = random.randint(0, len(content) - snippet_length)
            snippet = content[start_idx: start_idx + snippet_length]

        extracted_data.append({
            'Filename': filename,
            'Category': row['Category'],
            'Century': row['Century'],
            'Snippet': snippet
        })

    return pd.DataFrame(extracted_data)

# Example Usage:
# sampled_files_df = proportional_stratified_sampling('Corpus_Metadata.xlsx', total_samples=100)
# final_snippets_df = extract_random_text_snippets(sampled_files_df, './text_corpus', snippet_length=100)
# final_snippets_df.to_excel('Final_10000_Chars_Sample.xlsx', index=False)