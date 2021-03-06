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
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
        transforms.RandomRotation(degrees=10),
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
    'unet_test': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(CROP_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(0, 1)
    ]),
}

unet_combined_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(CROP_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(degrees=10),
    ]),
    'validation': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(CROP_SIZE),
    ]),
    'test': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(CROP_SIZE),
    ]),
}

unet_image_transforms = {
    'train': transforms.Compose([
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
        transforms.Normalize(0, 1)
    ]),
    'validation': transforms.Compose([
        transforms.Normalize(0, 1)
    ]),
    'test': transforms.Compose([
        transforms.Normalize(0, 1)
    ]),
}

def get_data_transforms():
    return default_data_transforms

def load_datasets(
    base_path:str='/',
    splits: List = [0.8, 0.1, 0.1],
    num_labels: int = 36,
    data_transforms: Dict[str, Any]=default_data_transforms,
    segment: bool = False,
):
    
    dataset_attrs_path = os.path.join(base_path, f'train_dataset_attr_{num_labels}.npy')
    dataset_attrs = np.load(dataset_attrs_path, allow_pickle=True)

    dataset_images_path = os.path.join(base_path, 'train_dataset_images.npy')
    dataset_images = np.load(dataset_images_path, allow_pickle=True)

    dataset_attr_counts_path = os.path.join(base_path, f'train_dataset_attr_{num_labels}_counts.npy')
    dataset_attr_counts = np.load(dataset_attr_counts_path, allow_pickle=True)

    n, _ = dataset_images.shape

    assert dataset_attrs.shape[1] - 1 == dataset_attr_counts.shape[0]

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

        if segment:
            datasets[split] = DeepFashionWithSegmentation(dataset_splits[i], dataset_attrs, base_path,
                                        image_transform=unet_image_transforms[split],
                                        combined_transform=unet_combined_transforms[split])
        else:
            datasets[split] = DeepFashion(dataset_splits[i],
                                        dataset_attrs, base_path,
                                        transform=transform)

    return datasets, dataset_attr_counts

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

        return x, y, None, None

class DeepFashionWithSegmentation(Dataset):
    def __init__(self, dataset=[], attrs={}, base_path:str='/',
        image_transform=None,
        combined_transform=None
    ):
        self.dataset = dataset
        self.attrs = attrs
        self.base_path = base_path
        self.base_path += '/Img'
        self.image_transform = image_transform
        self.combined_transform = combined_transform
        
    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):

        item_id = self.dataset[idx][0]
        img_path = self.dataset[idx][1]

        # Use highres image for segmentation
        full_img_path = os.path.join(self.base_path, img_path).replace('img/', 'img_highres/')

        seg_im_path = full_img_path.replace('.jpg', '_segment.png')

        x = Image.open(full_img_path)
        x = transforms.ToTensor()(x)
        seg, hasSeg = loadSegmentationArray(seg_im_path, x.shape)
        seg = transforms.ToTensor()(seg)

        if self.image_transform:
            x = self.image_transform(x)

        # Combine image and seg data for transformations
        x = torch.cat((x, seg))

        if self.combined_transform:
            x = self.combined_transform(x)

        y = self.attrs[item_id]

        # Split image and seg data
        x, seg = x[:3, :, :], x[3:, :, :]
        
        return x, y, seg, hasSeg

# isEqualFunc is a function that maps each element x in a numpy
# array to 1 if x does not equal a value v, and 0 otherwise.
isNotEqualFunc = np.vectorize(lambda x, v: 1 if x != v else 0)

def loadSegmentationArray(seg_im_path, shape):

    if os.path.exists(seg_im_path):
        im_frame = Image.open(seg_im_path)

        # Convert to numpy array and discard alpha channel (channel 4)
        np_frame = np.array(im_frame)[:,:,:3]

        # Create a segmentation heatmap where each pixel is 1 for foreground
        # (RGB sum is non-zero), and 0 for background (RGB sum is zero)
        seg = isNotEqualFunc(np_frame.sum(axis=2), 0)[:,:,np.newaxis]
        
        return seg, 1
    else:
        seg = np.zeros((shape[1], shape[2], 1))
        return seg, 0
    