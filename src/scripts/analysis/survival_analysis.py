import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib.pyplot as plt
import argparse
from difflib import get_close_matches
import os


def prepare_data(file_path, hi_list=None, hti_threshold=0.5):
    # Load the data
    data = pd.read_csv(file_path)

    # Define the columns for survival analysis
    time_col = 'Overall Survival (Months)'
    event_col = 'Overall Survival Status'

    # Convert the event column to binary (0 for living/censored, 1 for deceased/event occurred)
    data[event_col] = data[event_col].map(lambda x: 0 if x == '0:LIVING' else 1)
    potential_colnames_HTI = ['HI', 'HTI', 'HT-Index', 'HT - Index', 'heterogeneity index']
    hetero_index_colname = next((col for col in data.columns
                                 if any(get_close_matches(col.lower(), [s.lower()],cutoff=0.7)
                                    for s in potential_colnames_HTI)), None)
    if hetero_index_colname:
        hi_col = data[hetero_index_colname]
    elif hi_list is not None:
        # Use the provided HI list
        hi_col = pd.Series(hi_list)
        if len(hi_col) != len(data):
            raise ValueError("Length of HI list does not match the number of rows in the CSV")
    else:
        # no HI can be found, generate randomly for test purposes
        # np.random.seed(42)  # For reproducibility
        hi_col = np.random.normal(loc=0.5, scale=0.15, size=len(data))
        hi_col = np.clip(hi_col, 0, 1)

    # Add the HI column to the data
    data['HI'] = hi_col

    # Group data based on HI
    data['HI Group'] = data['HI'].apply(lambda x: f"HT-Index <= {hti_threshold}"
                                if x <= hti_threshold else f"HT-Index > {hti_threshold}")

    # Drop rows with missing values in the survival columns
    km_data = data[[time_col, event_col, 'HI Group']].dropna()

    return km_data


def plot_kaplan_meier(data, time_col, event_col, group_col, p_value, group_sizes, hti_threshold=0.5):
    kmf = KaplanMeierFitter()

    # Plot survival curves for each group
    for group in data[group_col].unique():
        group_data = data[data[group_col] == group]
        kmf.fit(group_data[time_col], event_observed=group_data[event_col], label=f'Group {group}')
        kmf.plot_survival_function()

    plt.title('Kaplan-Meier Survival Curve by Group')
    plt.xlabel('Time (Months)')
    plt.ylabel('Survival Probability')
    plt.legend()

    # Add text box with additional information
    textstr = '\n'.join((
        f'n ≤ {hti_threshold}: {group_sizes[0]}',
        f'n > {hti_threshold}: {group_sizes[1]}',
        "",
        f'p-value (Log-rank test): {p_value:.4f}'))
    plt.gca().text(0.05, 0.05, textstr, transform=plt.gca().transAxes, fontsize=9,
                   verticalalignment='bottom')

    plt.show()

def perform_logrank_test(data, time_col, event_col, group_col, hti_threshold=0.5):
    group1 = data[data[group_col] == f"HT-Index <= {hti_threshold}"]
    group2 = data[data[group_col] == f"HT-Index > {hti_threshold}"]

    # make sure data is correctly split by string match
    assert(not group1.empty)
    assert(not group2.empty)

    results = logrank_test(group1[time_col], group2[time_col], event_observed_A=group1[event_col], event_observed_B=group2[event_col])
    return results


def main(file_path, hi_file_path=None):
    hti_threshold = 0.7
    # Load HI list if provided
    hi_list = None
    if hi_file_path and os.path.exists(hi_file_path):
        with open(hi_file_path, 'r') as file:
            hi_list = [float(line.strip()) for line in file.readlines()]

    # Prepare the data
    km_data = prepare_data(file_path, hi_list, hti_threshold=hti_threshold)

    # Plot Kaplan-Meier curves
    # plot = plot_kaplan_meier(km_data, 'Overall Survival (Months)', 'Overall Survival Status',
    #                          'HI Group')

    # Perform log-rank test
    alpha = 0.05
    log_rank_results = perform_logrank_test(km_data, 'Overall Survival (Months)',
                                            'Overall Survival Status', 'HI Group',
                                            hti_threshold=hti_threshold)
    print(log_rank_results)
    if log_rank_results.p_value <= alpha:
        print(f"p value {log_rank_results.p_value} significant with significance level {alpha}")
    else:
        print(f"p value {log_rank_results.p_value} \033[1mnot\033[0m significant with significance level {alpha}.")

    # Plot Kaplan-Meier curves
    group_sizes = km_data['HI Group'].value_counts().sort_index().tolist()
    plot_kaplan_meier(km_data, 'Overall Survival (Months)', 'Overall Survival Status',
                      'HI Group', log_rank_results.p_value, group_sizes, hti_threshold=hti_threshold)


if __name__ == "__main__":
    # add filepaths as command line arguments or manipulate default strings further down
    # filepath 1: clinical data file holding survival information and optionally a column holding the heterogeneity
    # value
    # with a column name from 'potential_colnames_HTI'
    # filepath 2: if HTI is not present, you cn provide the value in a separate file containing the heterogeneity
    # index list in correct order according to clinical data CSV (one value per line).

    parser = argparse.ArgumentParser(description="Kaplan-Meier Survival Analysis")
    parser.add_argument("--file_path", type=str,
                        default='../../..//res/merged_clinical_mirna_data.csv',
                        help="Path to the CSV file containing the data.")
    parser.add_argument("--hi_file_path", type=str,
                        default=None,
                        help="Path to a file containing the heterogeneity index list in correct order according to "
                             "clinical data CSV (one value per line).")

    args = parser.parse_args()

    main(args.file_path, args.hi_file_path)
