import numpy as np
import torch
import matplotlib.pyplot as plt
import os
from PIL import Image
import json
import random
import pickle

from model import ResnetDummy
from unet import Unet
from dataloader import get_data_transforms

"""
ALL of the following must be directly in the BASE_PATH folder
- weights folders (all from the model_metadata)
- four catalogs
- webscraped images folder from drive
- embeddings folder from drive
- img folder for gallery (the URIs)
"""

# DATA_PATH = '/Users/kevinlee/Data/Stanford/CS329S/project/CS329S-project/data/In-shop Clothes Retrieval Benchmark/Img'
# BASE_PATH = '/Users/kevinlee/Data/Stanford/CS329S/project/CS329S-project/deepfashion'
BASE_PATH = '/scratch/users/avento/deepfashion'
DATA_PATH = BASE_PATH
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
NUM_TO_SAMPLE = 5

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
}

catalog_metadata = {
    "gallery": {
        "catalog_dir": os.path.join(BASE_PATH, 'catalog.json'),
    },
    "gap": {
        "img_dir":  os.path.join(BASE_PATH, "webscraped_images", "gap"),
        "catalog_dir": os.path.join(BASE_PATH, "catalog_gap.json")
    },
    "express": {
        "img_dir":  os.path.join(BASE_PATH, "webscraped_images", "express"),
        "catalog_dir": os.path.join(BASE_PATH, "catalog_express.json")
    },
    "zappos": {
        "img_dir":  os.path.join(BASE_PATH, "webscraped_images", "zappos"),
        "catalog_dir": os.path.join(BASE_PATH, "catalog_zappos.json")
        
    }
}

in_distribution_catalogs = ["gallery"]
out_of_distribution_catalogs = ["gap", "express", "zappos"]

def get_embed(model_name, full_img_path, transform=get_data_transforms()["test"]):
    weights_path = model_metadata[model_name]["weights"]
    model_args = model_metadata[model_name]["model_args"]
    
    # TODO: Add Unet when those are done training !!!!!!!
    model = ResnetDummy(**model_args)
    model.load_state_dict(torch.load(weights_path, map_location="cpu"))
    model = model.to(DEVICE)
    model.eval()
    
    img = Image.open(full_img_path).convert('RGB')
    cur_img = transform(img).unsqueeze(0).to(DEVICE)
    embedding = model.embed(cur_img).cpu().detach().numpy().flatten()
    del model
    return embedding


# class Catalog():

#     def __len__(self) -> int:
#         return len(self.catalog)

#     def __get__(self, index):
#         raise NotImplementedError

# class IDCatalog(Catalog):
#     def __init__(self, catalog_path: str, image_path: str):
#         self.catalog_distribution = "in-distribution"
#         self.image_path = image_path

#         with open(catalog_path, "r") as f:
#             self.catalog = json.load(f)

#     def __get__(self, index) -> Image :
#         img_uri = self.catalog[index]['URI']
#         full_img_path = os.path.join(self.image_path, img_uri)
#         img = Image.open(full_img_path)
#         return img

# class OODCatalog(Catalog):
#     def __init__(self, catalog_path: str, image_path: str):
#         self.catalog_distribution = "out-of-distribution"
#         self.image_path = image_path

#         with open(catalog_path, "r") as f:
#             self.catalog = json.load(f)

#     def __get__(self, index) -> Image :
#         full_img_path = os.path.join(self.image_path, f"{index}.jpg")
#         img = Image.open(full_img_path)
#         return img

def get_img_from_index(catalog_name, all_catalogs, index):
    if catalog_name == "gallery":
        catalog = all_catalogs[catalog_name]
        img_uri = catalog[index]['URI']
        full_img_path = os.path.join(DATA_PATH, img_uri)
    else:
        img_dir = catalog_metadata[catalog_name]["img_dir"]
        full_img_path = os.path.join(img_dir, f"{index}.jpg")
    img = Image.open(full_img_path)
    return img

def get_closest_embeds(img_embed, all_embeds, num_to_sample):
    distances = []
    for index, embed in enumerate(all_embeds):
        distance = np.sum((embed - img_embed) ** 2)
        if distance > 0: # To ensure not same image 
            distances.append((index, distance))
    
    distances.sort(key=lambda x: x[1], reverse=False)
    out = []
    prev_dist = None
    for index, dist in distances:
        if dist != prev_dist:
            prev_dist = dist
            out.append(index)
            print(index, dist, all_embeds[index])
            if len(out) == num_to_sample:
                break
    return out


def generate_plot_and_query_user(img_path, catalog_names, num_to_sample=5):
    imgs_to_plot = []
    num_imgs = 0
    prev_end = 0
    catalog_indices = {}
    all_catalogs = {}
    for catalog_name in catalog_names:
        with open(catalog_metadata[catalog_name]["catalog_dir"], "r") as f:
            full_catalog = json.load(f)
        all_catalogs[catalog_name] = full_catalog
        num_imgs += len(full_catalog)
        catalog_indices[catalog_name] = np.arange(prev_end, num_imgs)
        prev_end = num_imgs
    
    
    def find_imgs_to_plot(indices_to_choose, name):
        for idx in indices_to_choose:
            for catalog_name, indices in catalog_indices.items():
                if idx in indices:
                    offset = int(idx - indices[0])
                    cur_img = get_img_from_index(catalog_name, all_catalogs, offset)
                    imgs_to_plot.append((cur_img, name))
                    break
    
    # Random Baseline
    random_img_indices = np.random.choice(num_imgs, size=num_to_sample, replace=False)
    find_imgs_to_plot(random_img_indices, "Random")
                
    
    # All Other Models
    for model_name in model_metadata.keys():
        img_embed = get_embed(model_name, img_path)
        embeds_path = os.path.join(BASE_PATH, "embeddings", model_name)
        all_embeds = []
        for catalog_name in catalog_names:
            full_embed_path = os.path.join(embeds_path, f"{catalog_name}_embeds.npy")
            cur_embeds = np.load(full_embed_path)
            all_embeds.append(cur_embeds)
        all_embeds = np.concatenate(all_embeds, axis=0)
        model_indices = get_closest_embeds(img_embed, all_embeds, num_to_sample)
        find_imgs_to_plot(model_indices, model_name)
        
    random.shuffle(imgs_to_plot)
    
    total_models = len(model_metadata.keys()) + 1 # +1 for random
    plt.ion()
    fig, ax = plt.subplots(nrows=total_models, ncols=num_to_sample + 1, figsize=(25, 16))
    
    query_img = Image.open(img_path).convert('RGB')
    ax[0, 0].imshow(query_img)
    ax[0, 0].set_title(f'Query Image')
    for i in range(total_models):
        ax[i, 0].axis('off')
    for idx, (img, _) in enumerate(imgs_to_plot):
        row = idx // num_to_sample
        col = (idx % num_to_sample) + 1
        ax[row, col].imshow(img)
        ax[row, col].set_title(f'Image {idx}')
        ax[row, col].axis('off')
    
    plt.tight_layout()
    temp_save_path = os.path.join(BASE_PATH, "ImgOut.png")
    plt.savefig(temp_save_path)
    print(f"Image has been saved at {temp_save_path}.  Go open it and get ready to review!")
    
    plt.close()

    outputs = []
    catalog_distribution = "in-distribution" if "gallery" in catalog_names else "out-of-distribution"
    for idx, (_, model) in enumerate(imgs_to_plot):
        val = None
        while val not in ["y", "n"]:
            val = input(f"Do your like image{idx} (y or n): ")
        outputs.append((model, val, catalog_distribution))
    
    return outputs


if __name__ == "__main__":
    # TODO: ADD MORE IMGS HERE :P 
    query_img_paths = [os.path.join(BASE_PATH, "New-Summer-Clothes-for-Women.jpeg")]
    out = []
    for img_path in query_img_paths:
        out += generate_plot_and_query_user(img_path, in_distribution_catalogs, num_to_sample=NUM_TO_SAMPLE)
        out += generate_plot_and_query_user(img_path, out_of_distribution_catalogs, num_to_sample=NUM_TO_SAMPLE)
    
    with open(os.path.join(BASE_PATH, "eval_results.pickle"), 'wb') as handle:
        pickle.dump(out, handle, protocol=pickle.HIGHEST_PROTOCOL)
