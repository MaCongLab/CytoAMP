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
import argparse
from sklearn.metrics import f1_score, roc_auc_score
from torch.amp import autocast,GradScaler

from transformers import AutoModelForMaskedLM
model = AutoModelForMaskedLM.from_pretrained('Synthyra/ESMplusplus_large', trust_remote_code=True)
tokenizer = model.tokenizer
import pandas as pd
from collections import defaultdict

def loss_func(metric,out_final,label):
    out_final = metric(out_final,label)
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




if __name__ == '__main__':
    # shutil.rmtree('pep_toxin'
    exp_name = 'toxicity_model_final'
    writer = SummaryWriter(f'{exp_name}')
    params = {'batch_size': 256,
              'shuffle': True,
              'num_workers':0}
    valid_params = {'batch_size': 128,
              'shuffle': False,
              'num_workers': 0}
    device = 'cuda'
    every_k = 10
    epochs = 400
    train_data_path = f"train_total.csv"
    valid_data_path = f"valid.csv"
    save_folder = f'save_models/{exp_name}/'
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    train_data_set = protein_dataset_esm3(train_data_path, maxlen=50)
    train_generator = DataLoader(train_data_set, collate_fn=collat_fn, **params)
    valid_data_set = protein_dataset_esm3(valid_data_path, maxlen=50)
    valid_generator = DataLoader(valid_data_set, collate_fn=collat_fn, **valid_params)

    model = Prot_model(feat_dim=128,aac_emb_dim=512,class_num=2).to(device)
    model.esm_model.eval()
    criteria = nn.CrossEntropyLoss()
    opt = torch.optim.AdamW(params=filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4, betas=(0.9, 0.999),weight_decay=1e-5)
    global_counter = 0
    lr_scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer=opt,gamma=0.95)
    best_valid_acc = 0
    scaler = GradScaler()
    for ep in range(epochs):
        if ep % 10 == 0 and ep > 0:
            lr_scheduler.step()
            tmplr = lr_scheduler.get_last_lr()[0]
            print(tmplr)
        model.train()
        model.esm_model.eval()
        for batch in tqdm(train_generator):
            # print(ba)
            batch_seq_id,attention_mask,batch_label,tokenized_for_cnn = batch
            batch_seq_id = batch_seq_id.to('cuda')
            attention_mask = attention_mask.to('cuda')
            tokenized_for_cnn = tokenized_for_cnn.cuda()
            label = batch_label.cuda()
            with autocast('cuda'):
                out_final = model(batch_seq_id,attention_mask,tokenized_for_cnn)
                cost = loss_func(criteria,out_final,label)
            tmpcost = cost.cpu().item()
            writer.add_scalar('Loss/train_celoss', tmpcost, global_counter)
            global_counter += 1
            opt.zero_grad()
            scaler.scale(cost).backward()
            scaler.step(opt)
            scaler.update()
        model.eval()
        with torch.no_grad():
            total_num = 0
            hit_len = 0
            pred_cls_lst = []
            label_lst = []
            pred_lst = []
            for batch in tqdm(valid_generator):
                batch_seq, attention_mask,batch_label,tokenized_for_cnn = batch
                label = batch_label.cuda()
                batch_seq_id = batch_seq.cuda()
                attention_mask = batch_seq.cuda()
                tokenized_for_cnn = tokenized_for_cnn.cuda()
                out_final = model(batch_seq_id,attention_mask,tokenized_for_cnn)
                pred_lst.append(out_final[:,1])
                pred = torch.argmax(out_final,dim=-1)
                pred_cls_lst.append(pred)
                total_num+=label.shape[0]
                label_right = label[pred==label]
                hit_len += label_right.shape[0]
                label_lst.append(label)
            pred_cls_lst = torch.cat(pred_cls_lst)
            label_lst = torch.cat(label_lst)
            pred_lst = torch.cat(pred_lst)
            auc_score = roc_auc_score(label_lst.cpu(), pred_lst.cpu())
            f1_score_num = f1_score(label_lst.cpu(), pred_cls_lst.cpu())
            writer.add_scalar('Valid/test_auc', hit_len/total_num, ep)
            writer.add_scalar('Valid/f1', f1_score_num, ep)
            writer.add_scalar('Valid/roc_score', auc_score, ep)
            if f1_score_num > best_valid_acc:
                best_valid_acc = f1_score_num
                torch.save(model.state_dict(), f'{save_folder}var_model_best.ckpt')
            torch.save(model.state_dict(), f'{save_folder}var_model_ep_{ep}.ckpt')


