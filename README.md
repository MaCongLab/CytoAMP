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

## How to use CytoAMP Model?

The codes that related to the model are as follows:
1. ```Dataset_esm3.py```: Contains the Dataset class to load the sequence during the model training.
2. ```model.py```: Contains the Constructed Deep-learning-based Model 
3. ```train.py```: script to train the model and evaluate on the valid dataset
4. ```test.py```: script to test the model and output the evaluation metrics.

The parameter of training is as follows:
| Parameter    | Default Value | Meaning| 
| -------- | ------- | ------- |
| epochs  | 100   | Number of training epochs    |
| save_k | 10    | Save model for every k epochs    |
| batch_size    | 256    | the size of batch for training    |
| lr    | 1e-3    | learning rate |
| device    | cuda  | using cuda or cpu|
| weight_decay    | 1e-4   |weight decay parameter for Adam optimizer|
| train_data_path    | ../data/train_total.csv  |The place where train set is placed|
| valid_data_path    | ../data/valid.csv  |The place where valid set is placed|
| feat_dim| 512 | The feature dimension of the amino acid embedding|
| exp_name| toxicity_model| The name of the experiment|
## Environment Preparaion
The environment can be created by using conda:

```conda create -n CytoAMP python=3.9```

And the packages needed can be installed using pip:

```pip install -r requirements.txt```

