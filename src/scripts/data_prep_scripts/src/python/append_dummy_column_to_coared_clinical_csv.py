import pandas as pd


def add_dummy_column(csv_file_path, output_file_path):
    # List of columns to concatenate
    columns_to_concat = ["Study ID", "Patient ID", "Sample ID", "Other Patient ID", "Other Sample ID",
                         "Pathology report uuid"]

    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Fill NaN values with empty strings to avoid issues during concatenation
    df[columns_to_concat] = df[columns_to_concat].fillna('')

    # Create the 'dummy' column by concatenating the specified columns
    df['dummy'] = df[columns_to_concat].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_file_path, index=False)


# Example usage
# csv_file_path = 'res/coadread_tcga_clinical_data_complete.csv'
# output_file_path = 'res/coadread_tcga_clinical_data_complete_with_dummy.csv'
# add_dummy_column(csv_file_path, output_file_path)
