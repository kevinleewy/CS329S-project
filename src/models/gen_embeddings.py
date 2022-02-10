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
from dataloader import load_datasets, get_data_transforms

BASE_PATH = '/scratch/users/avento/deepfashion'
WEIGHTS_PATH = os.path.join(BASE_PATH, '2022-02-08_23-53-14/best_model.pt')
CATALOG_PATH = os.path.join(BASE_PATH, 'catalog.json')
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

def generate_save_catalog_embeddings():
    datasets, attr_counts = load_datasets(base_path=BASE_PATH)
    num_labels = attr_counts.shape[0]

    model = ResnetDummy(num_labels, freeze_pretrain=False)
    model.load_state_dict(torch.load(WEIGHTS_PATH))
    model = model.to(DEVICE)
    model.eval()

    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    all_embeds = []
    transforms = get_data_transforms()['test']
    with torch.no_grad():
        for item_dict in tqdm(catalog):
            uri = item_dict['URI']
            full_img_path = os.path.join(BASE_PATH, uri)

            img = Image.open(full_img_path)
            img = transforms(img).unsqueeze(0).to(DEVICE)

            embed = model.embed(img)
            all_embeds.append(embed.cpu())

    all_embeds = np.concatenate(all_embeds, axis=0)
    np.save(os.path.join(BASE_PATH, 'catalog_embeds.npy'), all_embeds)

if __name__ == '__main__':
    generate_save_catalog_embeddings()




