# CytoAMP
A dataset for cytotoxicity of AMPs 
## What is CytoAMP?
CytoAMP is a dataset for the AMP cytotoxicity prediction constructed based on the public databases. It is focused on labelling the cytotoxicity based on the experimental assays. It also contains a code for building a deep-learning-based model for cytotoxicity prediction. 
<div align = "center"> 
<img src="/images/CytoAMP.png" width="50%" alt="CytoAMP" align='middle'>
</div>

## The structure of this project
```
.
├── data
│   ├── combined_dataset.txt
│   ├── combined_dataset_gpt-5.txt
│   ├── dataset_total.tsv
│   ├── test.csv
│   ├── test_total.csv
│   ├── train_total.csv
│   └── valid.csv
├── src
│   ├── Dataset_esm3.py
│   ├── model.py
│   ├── preprocess.py
│   ├── test.py
│   ├── train.py
│   └── vocab.txt
└── images

```
This project holds three dirs:
1. ```/data``` directory holds the file of the dataset.
2. ```/src``` directory holds the codes used for generating the dataset and model construction.
3. ```/images``` the resources files for readme.

## How to use CytoAMP?
The CytoAMP dataset contains two parts, the first one is the experiment assays of the peptide and the second one is the label assigned by GPT-5-mini based on the experiment assays.
In our repo, combined_dataset.txt is the file containing all the experimental assays, with each line a json string for one AMP. The json format is as follows:
```json
{
    "sequence": "GIWDTIKSMGKVFAGKILQNL",
    "cytotoxicity assays": [
        {
            "targetCell": "Human erythrocytes",
            "concentration": "90",
            "unit": "µM",
            "assay": "50% Hemolysis"
        },
        {
            "targetCell": "CEM-SS cells",
            "concentration": "7.42",
            "unit": "µM",
            "assay": "50% Cell death"
        }
    ]
}
```
And the file combined_dataset_gpt-5.txt contains the labels assigned by GPT-5-mini, with each row corresponding to the AMP in combined_dataset.txt.
```html
<result>cytotoxic</result>
<result>cytotoxic</result>
<result>cytotoxic</result>
<result>cytotoxic</result>
<result>unknown</result>
<result>unknown</result>
<result>cytotoxic</result>
<result>cytotoxic</result>
```
The python script ```preprocess.py``` can be used to generate a .tsv file ```dataset_total.tsv``` that combines the sequence and labels in those two files together, and then split it into ```train_total.csv```, ```valid.csv``` and ```test.csv```. Which can be used for model training and evaluation.

