import torch
from torch.utils.data import Dataset, DataLoader, Subset
import torchvision.transforms as transforms

import os
import pandas as pd
from PIL import Image

class DeepFashion(Dataset):
    def __init__(self, base_path='/', split='train', augment=False):
        attr_cloth_file = os.path.join(base_path, 'Anno/attributes/list_attr_cloth.txt')
        attr_items_file = os.path.join(base_path, 'Anno/attributes/list_attr_items.txt')
        splits_file = os.path.join(base_path, 'Eval/list_eval_partition.txt')

        attrs = pd.read_csv(attr_cloth_file, header=1)
        attrs = attrs['attribute_name'].values.tolist()
        self.df_labels = pd.read_csv(attr_items_file, sep=' ', names=attrs, skiprows=2)
        self.df_labels = self.df_labels.replace(-1, 0)

        df_splits = pd.read_csv(splits_file, sep='\s+', header=1)
        self.img_paths = df_splits[df_splits["evaluation_status"] == split]["image_name"].values 
        
        self.base_path = base_path
        self.augment = None
        self.preprocess = transforms.Compose([transforms.ToTensor()])#, transforms.Resize((IMG_SIZE, IMG_SIZE))])
        
    def __len__(self):
        return len(self.img_paths)

    def __getitem__(self, idx):
        img_path = self.img_paths[idx]
        cur_id = img_path.split('/')[-2]

        full_img_path = os.path.join(self.base_path, img_path)
        img = Image.open(full_img_path)
        img = self.preprocess(img)

        if self.augment:
            pass

        attributes = self.df_labels[self.df_labels.index == cur_id].values.flatten()
        
        return img, attributes.astype(float)