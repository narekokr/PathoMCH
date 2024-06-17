import pandas as pd

clinical_data_file = '../../TCGA-COAD/coadread_tcga_clinical_data_incl_survival.tsv'
clinical_data_df = pd.read_csv(clinical_data_file, sep='\t')

mirna_data_file = '../../TCGA-COAD/compiled_mirnas_quantification.csv'
mirna_data_df = pd.read_csv(mirna_data_file)


hsa_miR_143_df = mirna_data_df[mirna_data_df['miRNA_ID'] == 'hsa-mir-143']

hsa_miR_143_df = hsa_miR_143_df.T.reset_index()

hsa_miR_143_df.columns = hsa_miR_143_df.iloc[0]
hsa_miR_143_df = hsa_miR_143_df[1:]
hsa_miR_143_df.rename(columns={'miRNA_ID': 'Sample ID', 'hsa-mir-143': 'hsa-mir-143'}, inplace=True)
hsa_miR_143_df['Patient ID'] = [x[:12] for x in hsa_miR_143_df['Sample ID'].to_list()]
merged_df = pd.merge(clinical_data_df, hsa_miR_143_df[['Patient ID', 'hsa-mir-143']], left_on='Patient ID', right_on='Patient ID', how='left')

output_file = 'merged_clinical_mirna_data.csv'
merged_df.to_csv(output_file, index=False)