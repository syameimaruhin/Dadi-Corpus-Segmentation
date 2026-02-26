import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ================= Configuration =================
# Sensitivity coefficient: Detects an elbow when the drop in coverage
# exceeds the average drop by this multiplier.
DROP_SENSITIVITY = 2.0
MIN_NEW_WORDS = 20
STEP_SIZE = 0.5


def normalize_word(word, variant_map):
    """Normalize a word by mapping variant characters to their standard forms."""
    if not isinstance(word, str):
        return str(word)
    return "".join([variant_map.get(c, c) for c in word])


def calculate_interval_statistics(candidate_df, ref_set, v_map, score_col='MI', step_size=0.5):
    """
    Segment the candidates into intervals based on their MI scores and
    calculate the precision (coverage rate) against the reference dictionary.
    """
    max_val = math.ceil(candidate_df[score_col].max() / step_size) * step_size
    min_val = math.floor(candidate_df[score_col].min() / step_size) * step_size

    bins = np.arange(min_val, max_val + step_size, step_size)
    bins = sorted(bins, reverse=True)  # Order from highest score to lowest

    stats = []
    cumulative_count = 0

    for i in range(len(bins) - 1):
        high = bins[i]
        low = bins[i + 1]

        # Include max value in the first bin
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
            'Interval_Label': f"{low:.1f}-{high:.1f}",
            'Total_Words': count,
            'In_Ref_Count': in_ref_count,
            'New_Words': new_words,
            'Coverage_Rate': coverage,
            'Cumulative_Words': cumulative_count
        })

    return pd.DataFrame(stats)


def detect_elbow_point(df, drop_sensitivity=2.0, min_new_words=20):
    """
    Automatically detect the elbow point by calculating the derivative (coverage drop).
    An elbow is identified when the drop is substantially larger than the average drop.
    """
    df['Prev_Coverage'] = df['Coverage_Rate'].shift(1)
    df['Coverage_Drop'] = df['Prev_Coverage'] - df['Coverage_Rate']
    df['Coverage_Drop'] = df['Coverage_Drop'].fillna(0)

    # Filter out extremely sparse intervals for robust mean calculation
    valid_data = df[df['New_Words'] > min_new_words]
    avg_drop = valid_data['Coverage_Drop'].mean() if not valid_data.empty else 0.01

    elbow_index = None
    elbow_reason = ""

    for idx, row in valid_data.iterrows():
        drop = row['Coverage_Drop']
        # Pure mathematical detection: no manual forcing
        if pd.notna(drop) and drop > avg_drop * drop_sensitivity:
            elbow_index = idx
            elbow_reason = f"Substantial Drop ({drop:.1%} > Avg * {drop_sensitivity})"
            break

    return df, elbow_index, elbow_reason


def plot_elbow_curve(df, elbow_index, elbow_reason, output_filename='MI_Elbow_Curve.png'):
    """Generate a dual-axis chart to visualize the threshold sweep and elbow point."""
    valid_df = df[df['New_Words'] > MIN_NEW_WORDS].copy()
    if valid_df.empty:
        print("Not enough valid data for plotting.")
        return

    x = valid_df['Interval_Label']
    y_coverage = valid_df['Coverage_Rate']
    y_drop = valid_df['Coverage_Drop'].fillna(0)

    fig, ax1 = plt.subplots(figsize=(15, 9))
    sns.set_style("whitegrid")

    # Left Y-axis: Coverage Rate (Precision)
    line, = ax1.plot(x, y_coverage, color='tab:blue', marker='o', linewidth=3, label='Coverage Rate (Precision)')
    ax1.set_ylabel('Coverage Rate', fontsize=14, color='tab:blue', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_xlabel('MI Interval (High -> Low)', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 1.15)

    # Right Y-axis: Drop Rate (Derivative)
    ax2 = ax1.twinx()
    bars = ax2.bar(x, y_drop, color='tab:red', alpha=0.4, label='Drop Rate (Derivative)', width=0.6)
    ax2.set_ylabel('Coverage Drop Speed', fontsize=14, color='tab:red', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    max_drop = y_drop.max()
    ax2.set_ylim(min(y_drop.min(), -0.01), max(max_drop * 1.6, 0.08))

    # Annotate Elbow Point dynamically
    if elbow_index is not None and elbow_index in valid_df.index:
        elbow_row = valid_df.loc[elbow_index]
        bar_loc = valid_df.index.get_loc(elbow_index)
        elbow_val = elbow_row['Coverage_Drop']
        elbow_threshold = elbow_row['Interval_End']

        # Smart positioning to prevent text overlap
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

    plt.title('MI Optimal Threshold Analysis\n(First Substantial Drop)', fontsize=18, pad=20, fontweight='bold')
    ax1.set_xticks(range(len(x)))
    ax1.set_xticklabels(x, rotation=45, ha='right')

    lines_list = [line, bars]
    labels_list = [l.get_label() for l in lines_list]
    ax1.legend(lines_list, labels_list, loc='upper right', fontsize=12, frameon=True, facecolor='white',
               edgecolor='gray')

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved successfully: {output_filename}")


# Example Usage Template
if __name__ == '__main__':
    print("This module provides automated MI threshold selection logic.")
    # To execute, provide candidate_df, ref_set, and variant_map
    # df_stats = calculate_interval_statistics(candidate_df, ref_set, variant_map, score_col='MI', step_size=0.5)
    # df_elbow, e_idx, e_reason = detect_elbow_point(df_stats)
    # plot_elbow_curve(df_elbow, e_idx, e_reason)