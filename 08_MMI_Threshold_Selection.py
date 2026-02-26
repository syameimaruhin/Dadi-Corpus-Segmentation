import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ================= Configuration =================
# MMI specific thresholds for robust elbow detection
MIN_NEW_WORDS_FOR_VALIDITY = 200
ABSOLUTE_DROP_FLOOR = 0.02
DROP_SENSITIVITY = 1.0
STEP_SIZE = 1.0

def normalize_word(word, variant_map):
    """Normalize a word by mapping variant characters to their standard forms."""
    if not isinstance(word, str):
        return str(word)
    return "".join([variant_map.get(c, c) for c in word])

def calculate_mmi_interval_statistics(candidate_df, ref_set, v_map, score_col='MMI', step_size=1.0):
    """
    Segment the MMI candidates into intervals and calculate the precision
    (coverage rate) against the reference dictionary.
    """
    max_val = math.ceil(candidate_df[score_col].max() / step_size) * step_size
    min_val = math.floor(candidate_df[score_col].min() / step_size) * step_size

    bins = np.arange(min_val, max_val + step_size, step_size)
    bins = sorted(bins, reverse=True)

    stats = []
    cumulative_count = 0

    for i in range(len(bins) - 1):
        high = bins[i]
        low = bins[i + 1]

        if i == 0:
            mask = (candidate_df[score_col] >= low) & (candidate_df[score_col] <= high + 0.001)
        else:
            mask = (candidate_df[score_col] >= low) & (candidate_df[score_col] < high)

        subset = candidate_df[mask]
        count = len(subset)

        if count == 0:
            continue

        in_ref_count = sum(1 for w in subset['word'] if normalize_word(w, v_map) in ref_set)
        coverage = in_ref_count / count if count > 0 else 0
        new_words = count - in_ref_count
        cumulative_count += count

        stats.append({
            'Interval_Start': low,
            'Interval_End': high,
            'Interval_Label': f"{high:.1f}-{low:.1f}", # High to low label format
            'Total_Words': count,
            'In_Ref_Count': in_ref_count,
            'New_Words': new_words,
            'Coverage_Rate': coverage,
            'Cumulative_Words': cumulative_count
        })

    return pd.DataFrame(stats)

def detect_mmi_elbow_point(df, absolute_floor=0.02, drop_sensitivity=1.0, min_new_words=200):
    """
    Automatically detect the MMI elbow point.
    Requires the derivative (drop) to exceed both the average baseline and an absolute floor.
    """
    df['Prev_Coverage'] = df['Coverage_Rate'].shift(1)
    df['Coverage_Drop'] = df['Prev_Coverage'] - df['Coverage_Rate']
    df['Coverage_Drop'] = df['Coverage_Drop'].fillna(0)

    # Calculate baseline average drop strictly on positive drops with sufficient sample size
    valid_drops = df[(df['New_Words'] > min_new_words) & (df['Coverage_Drop'] > 0)]['Coverage_Drop']
    avg_drop = valid_drops.mean() if not valid_drops.empty else 0.01

    elbow_index = None
    elbow_reason = ""

    for idx, row in df.iterrows():
        if row['New_Words'] <= min_new_words:
            continue

        drop = row['Coverage_Drop']
        # Pure mathematical condition
        is_huge_drop = (drop > avg_drop * drop_sensitivity) and (drop > absolute_floor)

        if is_huge_drop:
            elbow_index = idx
            elbow_reason = f"Substantial Drop ({drop:.1%} > Floor {absolute_floor:.0%})"
            break

    return df, elbow_index, elbow_reason

def plot_mmi_elbow_curve(df, elbow_index, elbow_reason, output_filename='MMI_Elbow_Curve.png'):
    """Generate the visualization for the MMI threshold sweep."""
    valid_df = df[df['New_Words'] > MIN_NEW_WORDS_FOR_VALIDITY].copy()
    if valid_df.empty:
        print("Not enough valid data for plotting.")
        return

    x = valid_df['Interval_Label']
    y_coverage = valid_df['Coverage_Rate']
    y_drop = valid_df['Coverage_Drop'].fillna(0)

    fig, ax1 = plt.subplots(figsize=(15, 9))
    sns.set_style("whitegrid")

    # Left Y-axis: Coverage Rate
    line, = ax1.plot(x, y_coverage, color='tab:blue', marker='o', linewidth=3, label='Coverage Rate (Precision)')
    ax1.set_ylabel('Coverage Rate', fontsize=14, color='tab:blue', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_xlabel('MMI Interval (High -> Low)', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, max(0.15, y_coverage.max() * 1.2)) # Adjusted dynamic limits for MMI

    # Right Y-axis: Drop Rate
    ax2 = ax1.twinx()
    bars = ax2.bar(x, y_drop, color='tab:red', alpha=0.4, label='Drop Rate (Derivative)', width=0.6)
    ax2.set_ylabel('Coverage Drop Speed', fontsize=14, color='tab:red', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax2.set_ylim(min(y_drop.min(), -0.01), max(y_drop.max() * 1.6, 0.05))

    # Annotate Elbow
    if elbow_index is not None and elbow_index in valid_df.index:
        elbow_row = valid_df.loc[elbow_index]
        bar_loc = valid_df.index.get_loc(elbow_index)
        elbow_val = elbow_row['Coverage_Drop']
        elbow_threshold = elbow_row['Interval_End']

        total_bars = len(x)
        if bar_loc < total_bars * 0.4:
            xytext_offset, connection_style, ha_align = (60, 40), "arc3,rad=-0.2", 'left'
        elif bar_loc > total_bars * 0.6:
            xytext_offset, connection_style, ha_align = (-60, 40), "arc3,rad=0.2", 'right'
        else:
            xytext_offset, connection_style, ha_align = (0, 50), "arc3,rad=0", 'center'

        text_label = f"Elbow Point\nThreshold >= {elbow_threshold}\n[{elbow_reason}]"

        ax2.annotate(text_label, xy=(bar_loc, elbow_val), xytext=xytext_offset,
                     textcoords='offset points',
                     arrowprops=dict(facecolor='darkred', shrink=0.05, width=2, connectionstyle=connection_style),
                     fontsize=11, fontweight='bold', ha=ha_align, color='white',
                     bbox=dict(boxstyle="round,pad=0.4", fc="darkred", ec="black", alpha=0.85))

        bars[bar_loc].set_color('darkred')
        bars[bar_loc].set_alpha(0.9)

    plt.title('MMI Optimal Threshold Analysis\n(First Substantial Drop)', fontsize=18, pad=20, fontweight='bold')
    ax1.set_xticks(range(len(x)))
    ax1.set_xticklabels(x, rotation=45, ha='right')

    lines_list = [line, bars]
    labels_list = [l.get_label() for l in lines_list]
    ax1.legend(lines_list, labels_list, loc='upper right', fontsize=12, frameon=True, facecolor='white', edgecolor='gray')

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved successfully: {output_filename}")

# Example Usage Template
if __name__ == '__main__':
    print("This module provides automated MMI threshold selection logic.")
    # df_stats = calculate_mmi_interval_statistics(candidate_df, ref_set, v_map, score_col='MMI', step_size=1.0)
    # df_elbow, e_idx, e_reason = detect_mmi_elbow_point(df_stats)
    # plot_mmi_elbow_curve(df_elbow, e_idx, e_reason)