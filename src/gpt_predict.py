import json
import pandas as pd
from utils import GPT_QA

from tqdm import tqdm
from prompt import toxicity_prompt


dataset_path = 'datasetset path here'
output_path = 'output path here'

data_lst = []
with open(dataset_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for lines in tqdm(lines):
        tmp_json = json.loads(lines)
        data_lst.append(tmp_json)

with open(output_path, 'a+', encoding='utf-8') as f:
    for enu_idx,data in tqdm(enumerate(data_lst)):
        if len(data)==0:
            f.write(f'\n')
            f.flush()
            continue
        experiment = data['cytotoxicity assays']
        label_prompt = toxicity_prompt
        cytotoxicity_pred = GPT_QA(prompt=label_prompt,input=f'<experiment>{experiment}</experiment>',model_name='gpt-5-mini')
        cytotoxicity_pred = cytotoxicity_pred.replace('\n','')
        f.write(f'{cytotoxicity_pred}\n')
        f.flush()

    

     