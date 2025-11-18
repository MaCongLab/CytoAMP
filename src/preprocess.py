import pandas as pd
from sklearn.model_selection import train_test_split
import json
import re

def extract_labels(sequence_path,label_path,out_path):
    seq_lst = []

    with open(sequence_path, "r") as f:
        for line in f:
            line = line.strip()
            tmp_json = json.loads(line)
            seq_lst.append(tmp_json["sequence"])

    with open(out_path,'w') as f_out:
        with open(label_path,'r') as f_in:
            for enu_idx,line in enumerate(f_in.readlines()):
                line = line.strip()
                label = re.match(r'<result>(.*)</result>',line).group(1)
                tmp_seq = seq_lst[enu_idx]
                if 'x' in tmp_seq or 'X' in tmp_seq:
                    continue
                if 'o' in tmp_seq or 'O' in tmp_seq:
                    continue
                if 'u' in tmp_seq or 'U' in tmp_seq:
                    continue
                if 'b' in tmp_seq or 'B' in tmp_seq:
                    continue
                if 'z' in tmp_seq or 'Z' in tmp_seq:
                    continue
                if '-' in tmp_seq:
                    continue
                f_out.write(f'{seq_lst[enu_idx]}\t{label}\n')

def split_data(path):
    label_map = {
        'cytotoxic':1,
        'non-toxic':0,
        'unknown':0
    }
    df = pd.read_csv(path,sep='\t',names=['sequence','label'])
    df = df[df['label']!='unknown'].reset_index(drop=True)
    df['label'] = df['label'].map(lambda x:  label_map[x])
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])
    train_df.to_csv('../data/train_total.csv', index=False)
    test_df.to_csv('../data/test_total.csv', index=False)

def valid_split_data(path):
    test_df = pd.read_csv(path)
    valid_df, test_df = train_test_split(test_df, test_size=0.5, random_state=42, stratify=test_df['label'])
    valid_df.to_csv('../data/valid.csv', index=False)
    test_df.to_csv('../data/test.csv', index=False)

if __name__ == '__main__':
    # extract_labels(sequence_path='../data/combined_dataset.txt', label_path='../data/combined_dataset_gpt-5.txt',out_path='../data/dataset_total.tsv')
    # split_data('../data/dataset_total.tsv')
    valid_split_data('../data/test_total.csv')
