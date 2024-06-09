import csv
import math


def read_tsv_filter_svs(file_path):
    """
    Reads a TSV file and collects all rows where the value in the second column ends with '.svs'.
    """
    filtered_rows = []
    with open(file_path, newline='') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        header = next(reader)  # Save the header row
        for row in reader:
            if row[1].strip().endswith('.svs'):
                filtered_rows.append(row)
    return header, filtered_rows


def remove_duplicates(primary_rows, secondary_rows):
    """
    Removes rows from primary_rows if they are present in secondary_rows.
    """
    secondary_set = set(tuple(row) for row in secondary_rows)
    unique_rows = [row for row in primary_rows if tuple(row) not in secondary_set]
    return unique_rows


def write_tsv(file_path, header, rows):
    """
    Writes the header and rows to a TSV file.
    """
    with open(file_path, 'w', newline='') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerow(header)
        writer.writerows(rows)


def split_and_write_tsv(output_base_path, header, rows):
    """
    Splits the rows into two equal parts and writes them to two TSV files.
    """
    split_index = math.ceil(len(rows) / 2)
    part1_rows = rows[:split_index]
    part2_rows = rows[split_index:]

    write_tsv(f"{output_base_path}manifest_part1.txt", header, part1_rows)
    write_tsv(f"{output_base_path}manifest_part2.txt", header, part2_rows)


# Example usage
file1 = '/home/mathias/DSitLS/project/TCGA-COAD/gdc_manifest.2024-06-01-TCGA-COAD-open-acces-slide-miRNA-mRNA-filter.txt'  # full manifest
file2 = '/home/mathias/DSitLS/project/TCGA-COAD/first_150_svs_files.txt' # data philip already has
output_base_path = '/home/mathias/DSitLS/project/TCGA-COAD/'

header1, rows1 = read_tsv_filter_svs(file1)
_, rows2 = read_tsv_filter_svs(file2)

filtered_rows = remove_duplicates(rows1, rows2)
split_and_write_tsv(output_base_path, header1, filtered_rows)
