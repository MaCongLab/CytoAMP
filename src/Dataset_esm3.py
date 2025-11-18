import os.path
import os
import torch
import pandas as pd
import numpy as np
import math

class protein_dataset_esm3(torch.utils.data.Dataset):
    def __init__(self,data_path,maxlen):
        self.df = pd.read_csv(data_path)
        self.length = self.df.shape[0]
        self.maxlen = maxlen
        self.aac_vocab = self.load_vocab('vocab.txt')

    def __len__(self):
        return self.length

    def load_vocab(self,path):
        vocab = {}
        with open(path,'r') as f:
            for enu_id,line in enumerate(f):
                line = line.strip()
                vocab[line] = enu_id
        return vocab

    def __getitem__(self, idx):
        tmp_seq = self.df.loc[idx,'sequence']
        tmp_id = idx
        tmp_seq = tmp_seq.replace('\xa0','')
        tmp_seq = tmp_seq.replace(' ', '')
        tmp_label = self.df.loc[idx,'label']
        tmp_label = torch.tensor(tmp_label,dtype=torch.long)
        tmp_tokenized = [0]
        if len(tmp_seq)>50:
            tmp_seq=tmp_seq[:50]
        for token in tmp_seq:
            tmp_tokenized.append(self.aac_vocab[token])
        tmp_tokenized.append(self.aac_vocab['<eos>'])
        tmp_tokenized = torch.tensor(tmp_tokenized,dtype=torch.long)
        return tmp_seq,tmp_id,tmp_label,tmp_tokenized



