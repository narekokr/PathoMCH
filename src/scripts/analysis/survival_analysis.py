import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib.pyplot as plt
import argparse
from difflib import get_close_matches
import os

def create_group_string_from_data_row(row, hti_threshold, stratify_by):
    pass

def create_km_data(data, time_col, event_col, hi_list, hti_threshold, split_mode, stratify_group=None):
    # Convert the event column to binary (0 for living/censored, 1 for deceased/event occurred)
    data[event_col] = data[event_col].map(lambda x: 0 if x == '0:LIVING' else 1)

    # Identify heterogeneity index column
    potential_colnames_HTI = ['heterogeneity']

    hetero_index_colnames = []
    for col in data.columns:
        if any([s.lower() in col.lower() for s in potential_colnames_HTI]):
            hetero_index_colnames.append(col)

    km_data_collector = []
    print(f"{data.columns.name}: Found heterogeneity indexes in columns:\n", "\n".join(hetero_index_colnames))
    for hetero_index_colname in hetero_index_colnames:
        if hetero_index_colname:
            hi_col = data[hetero_index_colname]
        elif hi_list is not None:
            print("Use the provided HI list")
            hi_col = pd.Series(hi_list)
            if len(hi_col) != len(data):
                raise ValueError("Length of HI list does not match the number of rows in the CSV")
        else:
            # Generate HI values randomly for test purposes
            # np.random.seed(42)  # For reproducibility
            print("Warning: No HTI Values found. Generating.")
            hi_col = np.random.normal(loc=0.5, scale=0.15, size=len(data))
            hi_col = np.clip(hi_col, 0, 1)

        # Determine the group based on HI thresholds
        if isinstance(hti_threshold, list) and len(hti_threshold) == 2:
            # two thresholds
            lower, upper = sorted(hti_threshold)
            if split_mode == 'ternary':
                group_string = hi_col.apply(lambda x:
                                            f'HT-Index ≤ {lower}' if x <= lower
                                            else
                                            (f'{lower} < HT-Index ≤ {upper}' if x <= upper
                                             else
                                             f'HT-Index > {upper}'))
            else:
                group_string = hi_col.apply(lambda x:
                                            f'HT-Index ≤ {lower}' if x <= lower
                                            else
                                            (f'HT-Index > {upper}' if x > upper
                                             else
                                             'Excluded'))
        else:
            # one threshold
            threshold = hti_threshold[0]
            group_string = hi_col.apply(lambda x:
                                        f'HT-Index ≤ {threshold}' if x <= threshold
                                        else f'HT-Index >{threshold}')
        data['HI Group'] = group_string
        # merged plots for stratification case, currently not wanted
        # if stratify_by == "Sex":
        #     for index, row in data.iterrows():
        #         if row['Sex'] == "Female":
        #             data.at[index, 'HI Group'] = "Fem.: " + row['HI Group']
        #         elif row["Sex"] == "Male":
        #             data.at[index, 'HI Group'] = "Male: " + row['HI Group']
        #

        # Drop rows with missing values in the survival columns
        km_data = data[[time_col, event_col, hetero_index_colname, 'HI Group']].copy().dropna()
        if stratify_group:
            km_data.columns.name = ";X;".join([stratify_group.capitalize(), hetero_index_colname])
        else:
            km_data.columns.name = ";X;"+hetero_index_colname
        km_data_collector.append(km_data)
    return km_data_collector


def get_age_boundaries(age_list, k=1):
    min_age = min(age_list)
    max_age = max(age_list)

    # Calculate the step size
    step = (max_age - min_age) / (k + 1)
    # Calculate the boundary values
    boundaries = [round(min_age + (i + 1) * step, 0) for i in range(k)]

    return boundaries
def prepare_data(file_path, time_col, event_col, hi_list=None, hti_threshold=[0.5], split_mode='binary',
                 stratify_by=None):

    # Load the data
    dataset = pd.read_csv(file_path)

    #stratify, if wanted
    if stratify_by:
        if stratify_by.lower() == "sex":
            fem_data = dataset[dataset["Sex"] == "Female"].copy()
            fem_data.columns.name = "female"
            male_data = dataset[dataset["Sex"] == "Male"].copy()
            male_data.columns.name = "male"
            data_collector = [fem_data, male_data]
        elif stratify_by.lower().startswith("age"):
            if stratify_by[-1].isdigit():
                # number of age bins given, so we use it.
                bins = int(stratify_by[-1])
                if bins == 2:
                    pass
                else:
                    boundaries = get_age_boundaries(dataset["Diagnosis Age"], bins-1)
                    data_collector = []
                    last_bound = 0
                    for bound in boundaries:
                        if not last_bound == max(boundaries):
                            this_bin_data = dataset[(dataset["Diagnosis Age"] >= last_bound) |
                                                    (dataset["Diagnosis Age"] < bound)].copy()
                            this_bin_data.columns.name = f"Age >= {last_bound} < {bound}"
                            data_collector.append(this_bin_data)
                            last_bound = bound
                        # else:
                    this_bin_data = dataset[dataset["Diagnosis Age"] >= last_bound]
                    this_bin_data.columns.name = f"Age >= {bound}"
                    data_collector.append(this_bin_data)

                    pass
            try:
                data_collector
            except NameError:
                # above derivation of bins did not work, so we split into two bin with the mean as the middle
                age_median = int(dataset["Diagnosis Age"].median())
                bin1_data = dataset[(dataset['Diagnosis Age'] >= 0) | (dataset['Diagnosis Age'] < age_median)].copy()
                bin1_data.columns.name = f"Age >= 0 < {age_median}"
                bin2_data = dataset[dataset['Diagnosis Age'] >= age_median].copy()
                bin2_data.columns.name = f"Age >= {age_median}"

                data_collector = [bin1_data, bin2_data]
        else:
            print(f"Warning: Stratification parameter {stratify_by} not recognized. Using whole dataset).")
            stratify_by = None

    if not stratify_by:
        data_collector = [dataset]

    km_data_collector=[]
    for data in data_collector:
        if data.columns.name:
            km_data = create_km_data(data, time_col, event_col, hi_list, hti_threshold, split_mode,
                                     stratify_group=data.columns.name)
        else:
            km_data = create_km_data(data, time_col, event_col, hi_list, hti_threshold, split_mode)
        km_data_collector.extend(km_data)

    return km_data_collector

def make_hti_colname_easy_to_read(hti_colname):
    transformed_str = hti_colname.replace("_mrna_", " mRNA ")
    transformed_str = transformed_str.replace("_mir_", " miR ")

    parts = transformed_str.split('_')
    result_parts = []
    for part in parts:
        # Check if the part starts with "hsa_"
        if part.startswith('hsa'):
            # Extract the part after "hsa_"
            mir_part = part[4:].replace(' ', '-')
            result_parts.append(mir_part)
        elif part.startswith('baseline'):
            result_parts.append(part)

    final_result = ' and '.join(result_parts)

    return final_result

def plot_kaplan_meier(data, time_col, event_col, group_col, p_value, group_sizes, hti_threshold):
    kmf = KaplanMeierFitter()
    if data.columns.name:
        stratify_group = data.columns.name.split(';X;')[0]
        hti_colname = data.columns.name.split(";X;")[-1]
        hti_colname = make_hti_colname_easy_to_read(hti_colname)
        pass
    else:
        stratify_group = ""
        hti_colname = ""
    # Plot survival curves for each group
    for group in data[group_col].sort_values().unique():
        group_data = data[data[group_col] == group]
        kmf.fit(group_data[time_col].div(12), event_observed=group_data[event_col], label=group)    # conversion months -> years
        # make sure color coding is consistent
        if ">" in group and not "≤" in group:
            color = '#1f77b4'  # blue
            if group.startswith("Fem.") or stratify_group.lower() == "female":
                color = '#6A3D9A'
            elif group.startswith("Male") or stratify_group.lower() == "male":
                color = '#017374'

        elif "≤" in group and not ">" in group and not "<" in group:
            color = '#ff7f0e' # orange
            if group.startswith("Fem.") or stratify_group.lower() == "female":
                color = '#B39DDB'
            elif group.startswith("Male") or stratify_group.lower() == "male":
                color = '#20B2AA'
        else:
            color = 'green'
        kmf.plot_survival_function(color=color)

    if hti_colname:
        plt.title(hti_colname, fontsize=12)
    else:
        plt.title('Kaplan-Meier Survival Curve by Group')
    if stratify_group:
        plt.suptitle(f"{stratify_group}")

    plt.xlabel('Time (Years)')
    plt.ylabel('Percent Survival')
    plt.legend()

    # Add text box with additional information
    textstr = '\n'.join([
                            f'{str(group).replace("HT-Index", "n")}: {size}'
                            for group, size in zip(data[group_col].unique(), group_sizes)
                        ] + [f"", f'p-val: {p_value:.2f}'])

    plt.gca().text(0.05, 0.05, textstr, transform=plt.gca().transAxes, fontsize=9, verticalalignment='bottom')

    plt.show()


def perform_logrank_test(data, time_col, event_col, group_col):
    unique_groups = data[group_col].unique()
    group_data = [data[data[group_col] == group] for group in unique_groups]

    # make sure data is correctly split by string match
    for dat in group_data:
        assert (not dat.empty)

    if len(unique_groups) < 2:
        print("At least one group for logranks test is empty. Skipping dataset.")
        results=None

    elif len(unique_groups) == 2:
        results = logrank_test(group_data[0][time_col], group_data[1][time_col],
                               event_observed_A=group_data[0][event_col],
                               event_observed_B=group_data[1][event_col])
    elif len(unique_groups) == 3:
        results = logrank_test(group_data[0][time_col], group_data[2][time_col],
                               event_observed_A=group_data[0][event_col],
                               event_observed_B=group_data[2][event_col])
    # elif len(unique_groups) == 4:
    #     # stratified by sex, in one plot
    #     groupA = pd.concat([group_data_point for group_data_point in group_data if ">" in group_data_point.values[1][
    #         -1]])
    #     groupB = pd.concat([group_data_point for group_data_point in group_data if "≤" in group_data_point.values[1][
    #         -1]])
    #     results = logrank_test(groupA[time_col], groupB[time_col],
    #                            event_observed_A=groupA[event_col],
    #                            event_observed_B=groupB[event_col])
        pass
    else:
        raise ValueError("The data should be split into either 2 or 3 groups based on the HTI thresholds.")

    return results


def main(file_path, time_col, event_col, hi_file_path=None, hti_threshold=[0.5], split_mode='binary', stratify_by=None):
    """
    :param file_path: clinical.csv, clinical data file holding survival information and optionally a column holding
    the heterogeneity value with a column name from 'potential_colnames_HTI'
    :param time_col: column name in clinical.csv giving survival time information
    :param event_col: column holding the event information (either "0:LIVING" or "1:DECEASED")
    :param hi_file_path: if HT index is not present in clinical data, you ccn provide the value in a separate file
    containing the heterogeneity index list in correct order according to clinical data CSV (one value per line).
    :param hti_threshold: Heterogeneity threshold value(s). Provide one value for binary split or two values for
    ternary split. You can also perform binary split, when giving two values. In that case, the groups are build from
    upper and lower bonds.
    :param stratify_by: Subgroup feature to stratify by. Either \"Sex\" or \"Age_n\", where n is the number of
    age bins (2 by default, split by median)
    :param split_mode: Choose 'binary' for two groups or 'ternary' for three groups based on HI thresholds.
    """
    # Load HI list if provided
    hi_list = None
    if hi_file_path and os.path.exists(hi_file_path):
        with open(hi_file_path, 'r') as file:
            hi_list = [float(line.strip()) for line in file.readlines()]

    # Prepare the data
    km_data_list = prepare_data(file_path, time_col, event_col, hi_list, hti_threshold=hti_threshold,
                                split_mode=split_mode, stratify_by=stratify_by)

    for km_data in km_data_list:
    # Perform log-rank test
        log_rank_results = perform_logrank_test(km_data, 'Overall Survival (Months)',
                                                'Overall Survival Status', 'HI Group')
        if log_rank_results:

            # print(log_rank_results)
            alpha = 0.05
            if log_rank_results.p_value <= alpha:
                print(f"p-value {log_rank_results.p_value} significant with significance level {alpha}")
            else:
                print(f"p-value {log_rank_results.p_value} \033[1mnot\033[0m significant with significance level {alpha}.")

            # Plot Kaplan-Meier curves
            group_sizes = km_data['HI Group'].value_counts().sort_index().tolist()
            plot_kaplan_meier(km_data, 'Overall Survival (Months)', 'Overall Survival Status',
                              'HI Group', log_rank_results.p_value, group_sizes, hti_threshold=hti_threshold)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kaplan-Meier Survival Analysis")
    parser.add_argument("--clinical_csv", type=str,
                        default='../../..//res/merged_clinical_mirna_data_test.csv',
                        help="Path to the CSV file containing the data.")
    parser.add_argument("--time_col", type=str,
                        default='Overall Survival (Months)',
                        help="Time column name in csv stating survival duration e. g. in months.")
    parser.add_argument("--event_col", type=str,
                        default='Overall Survival Status',
                        help="Event column name in csv stating status either being:"
                             "\n0:LIVING"
                             "\nor"
                             "\n1:DECEASED")
    parser.add_argument("--hi_file_path", type=str,
                        default=None,
                        help="Path to a file containing the heterogeneity index list (one value per line).")
    parser.add_argument("--hti_threshold", type=float, nargs='+',
                        default=[0.5],
                        # default=[0.3, 0.7],
                        help="Heterogeneity threshold value(s). Provide one value for binary split or two values for ternary split.")
    parser.add_argument("--stratify_by", type=str, nargs='+',
                        # default=None,
                        # default="Sex",
                        # default="Age",
                        default="Age_3",
                        help="Subgroup feature to stratify by. Either \"Sex\" or \"Age_n\", where n is the number of "
                             "age bins (2 by default, split by median)")
    parser.add_argument("--split_mode", type=str, choices=['binary', 'ternary'],
                        default='binary',
                        # default='ternary',
                        help="Choose 'binary' for two groups or 'ternary' for three groups based on HI thresholds.")

    args = parser.parse_args()

    main(args.clinical_csv, args.time_col, args.event_col, args.hi_file_path, hti_threshold=args.hti_threshold,
         split_mode=args.split_mode, stratify_by=args.stratify_by)
