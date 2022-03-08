import torch
import os
import random
import numpy as np
import matplotlib.pyplot as plt
import json
import torchvision.transforms as transforms
from PIL import Image
from tqdm import tqdm

from model import ResnetDummy
from unet import Unet
from dataloader import load_datasets, get_data_transforms

BASE_PATH = '/scratch/users/avento/deepfashion'
SAVE_PATH = os.path.join(BASE_PATH, 'embeddings')
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

model_metadata = {
    "model_13": {
        "weights": os.path.join(BASE_PATH, '2022-02-08_23-53-14/best_model.pt'),
        "model_args":{'num_labels':13, 'embedding_dim':512, 'freeze_pretrain':False},
    },
    "model_36": {
        "weights": os.path.join(BASE_PATH, '2022-02-28_07-05-40/best_model.pt'),
        "model_args":{'num_labels':36,'embedding_dim':512, 'freeze_pretrain':False},
    },
    "model_36_aug":  {
        "weights": os.path.join(BASE_PATH, '2022-02-28_16-52-37/best_model.pt'),
        "model_args": {'num_labels':36,'embedding_dim':512, 'freeze_pretrain':False},
    },
    "unet_36_aug": {
        "weights": os.path.join(BASE_PATH, '2022-03-05_01-09-36/best_model.pt'),
        "model_args": {'num_labels':36,'n_classes': 1, 'embedding_dim': 512},
    }
}

catalog_metadata = {
    "gallery": {
        "catalog_dir": os.path.join(BASE_PATH, 'catalog.json'),
    },
    "gap": {
        "img_dir":  os.path.join(BASE_PATH, "webscraped_images", "gap")
    },
    "express": {
        "img_dir":  os.path.join(BASE_PATH, "webscraped_images", "express")
    },
    "zappos": {
        "img_dir":  os.path.join(BASE_PATH, "webscraped_images", "zappos")
    }
}

def get_model(model_name):
    weights_path = model_metadata[model_name]["weights"]
    model_args = model_metadata[model_name]["model_args"]
    if "unet" in model_name:
        model = Unet(**model_args)
    else:
        model = ResnetDummy(**model_args)
    model.load_state_dict(torch.load(weights_path))
    model = model.to(DEVICE)
    return model


def generate_save_catalog_embeddings(model_name, catalog_name):
    model = get_model(model_name)
    model.eval()
    if "unet" in model_name:
        transforms = get_data_transforms()['unet_test']
    else:
        transforms = get_data_transforms()['test']
    all_embeds = []

    img_dir = catalog_metadata[catalog_name].get("img_dir")
    if not img_dir:
        catalog_dir = catalog_metadata[catalog_name]["catalog_dir"]
        with open(catalog_dir) as f:
            catalog = json.load(f)

        with torch.no_grad():
            for item_dict in tqdm(catalog):
                uri = item_dict['URI']
                full_img_path = os.path.join(BASE_PATH, uri)

                img = Image.open(full_img_path)
                img = transforms(img).unsqueeze(0).to(DEVICE)

                embed = model.embed(img)
                all_embeds.append(embed.cpu())
    else:
        files = os.listdir(img_dir)
        with torch.no_grad():
            for index in tqdm(range(len(files))):
                full_img_path = os.path.join(img_dir, f"{index}.jpg")

                img = Image.open(full_img_path)
                img = transforms(img).unsqueeze(0).to(DEVICE)

                embed = model.embed(img)
                all_embeds.append(embed.cpu())

         

    all_embeds = np.concatenate(all_embeds, axis=0)

    cur_save_path = os.path.join(SAVE_PATH, model_name)
    os.makedirs(cur_save_path, exist_ok=True)
    np.save(os.path.join(cur_save_path, f'{catalog_name}_embeds.npy'), all_embeds)

if __name__ == '__main__':
    for model in model_metadata.keys():
        for catalog in catalog_metadata.keys():
            print(f"Running for {model} and {catalog}...")
            generate_save_catalog_embeddings(model, catalog)




