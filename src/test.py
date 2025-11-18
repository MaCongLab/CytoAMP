import os
import shutil

import numpy as np
import torch
from torch import nn
from Dataset_esm3 import protein_dataset_esm3
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ExponentialLR
from torch.utils.tensorboard import SummaryWriter
from model import Prot_model
from tqdm import tqdm
from sklearn.metrics import roc_auc_score,f1_score
import argparse
from torch.amp.autocast_mode import autocast
from sklearn.metrics import confusion_matrix,matthews_corrcoef

from transformers import AutoModelForMaskedLM


model = AutoModelForMaskedLM.from_pretrained('Synthyra/ESMplusplus_large', trust_remote_code=True)
tokenizer = model.tokenizer
import pandas as pd
from collections import defaultdict

def loss_func(metric,out_final,label):
    # mamba_loss = metric(mamba_out, label)
    # graph_2d_out_loss = metric(graph_2d_out, label)
    # graph_3d_out_loss = metric(graph_3d_out,label)
    # print(label.shape)
    # print(out_final.shape)
    out_final = metric(out_final,label)
    # print(out_final)
    return out_final

def collat_fn(batch):
    batch_seq_lst = []
    batch_label_lst = []
    # batch_bond_graph_lst = []
    batch_tokenized_lst = []
    max_len = 0
    for data in batch:
        batch_seq, batch_id,batch_label,batch_tokenized = data
        batch_seq_lst.append(batch_seq)
        batch_label_lst.append(batch_label)
        batch_tokenized_lst.append(batch_tokenized)
        max_len= max(max_len,batch_tokenized.shape[0])

    batch_tokens = tokenizer(batch_seq_lst,padding=True,return_tensors='pt',truncation=True,max_length=50)
    batch_label = torch.vstack(batch_label_lst)
    batch_label = torch.squeeze(batch_label,dim=-1)
    for i in range(len(batch_tokenized_lst)):
        batch_tokenized_lst[i] = torch.concat([batch_tokenized_lst[i],torch.ones(max_len-batch_tokenized_lst[i].shape[0])],dim=0)
    batch_tokenized = torch.vstack(batch_tokenized_lst).long()
    return batch_tokens['input_ids'],batch_tokens['attention_mask'], batch_label,batch_tokenized


def calculate_metrics(all_labels, all_preds, all_pred_scores):
    tn, fp, fn, tp = confusion_matrix(all_labels, all_preds).ravel()
    acc = (tp + tn) / (tp + tn + fp + fn)
    sen = tp / (tp + fn)
    spe = tn / (tn + fp)
    mcc = matthews_corrcoef(all_labels, all_preds)
    auc = roc_auc_score(all_labels, all_pred_scores)
    f1 = f1_score(all_labels, all_preds)
    return acc, sen, spe, mcc, auc,f1


if __name__ == '__main__':
    test_params = {'batch_size': 64,
              'shuffle': False,
              'num_workers': 0}
    device = 'cuda'

    test_data_path = f"../test.csv"
    df = pd.read_csv(test_data_path)
    test_data_set = protein_dataset_esm3(test_data_path, maxlen=50)
    test_generator = DataLoader(test_data_set, collate_fn=collat_fn, **test_params)

    model = Prot_model(feat_dim=128,aac_emb_dim=512,class_num=2).to(device)
    model.load_state_dict(torch.load('your pretrained model path',map_location='cuda'))
    model.eval()
    with torch.no_grad():
        total_num = 0
        hit_len = 0
        pred_lst = []
        label_lst = []
        pred_cls_lst = []
        for batch in tqdm(test_generator):
            batch_seq, attention_mask,batch_label,tokenized_for_cnn = batch
            label = batch_label.cuda()
            batch_seq_id = batch_seq.cuda()
            attention_mask = attention_mask.cuda()
            tokenized_for_cnn = tokenized_for_cnn.cuda()
            with autocast('cuda'):
                out_final = model(batch_seq_id,attention_mask,tokenized_for_cnn)
            pred_lst.append(out_final[:,1])
            pred = torch.argmax(out_final,dim=-1)
            pred_cls_lst.append(pred)
            label_lst.append(label)
    pred_lst = torch.cat(pred_lst)
    label_lst = torch.cat(label_lst)
    pred_cls_lst = torch.cat(pred_cls_lst)
    pred_lst = pred_lst.cpu()
    label_lst = label_lst.cpu()
    pred_cls_lst = pred_cls_lst.cpu()
    acc, sen, spe, mcc, auc,f1 = calculate_metrics(label_lst,pred_cls_lst,pred_lst)
    df['pred'] = pred_cls_lst
    df.to_csv('test_pred.csv',index=False)

    print(
        f"ACC: {acc:.4f}, Sensitivity: {sen:.4f}, Specificity: {spe:.4f}, MCC: {mcc:.4f}, AUC: {auc:.4f}, F1: {f1:.4f}")

