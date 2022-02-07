import torch
from torch.utils.data import Dataset, DataLoader, Subset
import torchvision.transforms as transforms

import numpy as np
import os
from PIL import Image
from typing import Any, Dict, List

NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]
CROP_SIZE = 224

# Data augmentation and normalization for training
# Just normalization for validation
# Normalization: See https://pytorch.org/vision/stable/models.html
default_data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(CROP_SIZE),
        transforms.RandomHorizontalFlip(),
        # transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
        # transforms.RandomRotation(degrees=10),
        transforms.ToTensor(),
        transforms.Normalize(NORM_MEAN, NORM_STD)
    ]),
    'validation': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(CROP_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(NORM_MEAN, NORM_STD)
    ]),
    'test': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(CROP_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(NORM_MEAN, NORM_STD)
    ]),
}

def load_datasets(
    base_path:str='/',
    splits: List = [0.8, 0.1, 0.1],
    data_transforms: Dict[str, Any]=default_data_transforms
):
    
    dataset_attrs_path = os.path.join(base_path, 'train_dataset_attr.npy')
    dataset_attrs = np.load(dataset_attrs_path, allow_pickle=True)

    dataset_images_path = os.path.join(base_path, 'train_dataset_images.npy')
    dataset_images = np.load(dataset_images_path, allow_pickle=True)

    n, _ = dataset_images.shape
    _, n_labels = dataset_attrs.shape
    n_labels = n_labels - 1 # First column is image_id

    # Convert dataset_attrs to dict
    dataset_attrs = { row[0]: row[1:].astype(np.float) for row in dataset_attrs }

    # Determine split counts
    n_train = int(splits[0] * n)
    n_val = int(splits[1] * n)
    n_test = n - n_train - n_val

    lengths = [n_train, n_val, n_test]

    dataset_splits = torch.utils.data.random_split(dataset_images, lengths)

    datasets = {}
    for i, (split, transform) in enumerate(data_transforms.items()):

        datasets[split] = DeepFashion(dataset_splits[i], dataset_attrs, base_path, transform=transform)

    return datasets, n_labels

class DeepFashion(Dataset):
    def __init__(self, dataset=[], attrs={}, base_path:str='/', transform=None):
        self.dataset = dataset
        self.attrs = attrs
        self.base_path = base_path
        self.transform = transform
        
    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):

        item_id = self.dataset[idx][0]
        img_path = self.dataset[idx][1]

        full_img_path = os.path.join(self.base_path, img_path)
        x = Image.open(full_img_path)
        
        y = self.attrs[item_id]

        if self.transform:
            x = self.transform(x)

        return x, y
