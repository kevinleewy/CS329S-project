import torch
from torch.utils.data import Dataset, DataLoader, Subset
from torch import nn
from tqdm import tqdm

from model import ResnetDummy
from dataloader import DeepFashion

BASE_PATH = '/scratch/users/avento/deepfashion'
LEARNING_RATE = 0.01
EPOCHS = 50
BATCH_SIZE = 64
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

def train():
    model = ResnetDummy()
    model = model.to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    train_dataset = DeepFashion(base_path=BASE_PATH, split='train')
    train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE)
    criterion = torch.nn.BCELoss(reduction='mean') # TODO: Confirm this works when doing vector to vector within each sample

    for epoch in range(EPOCHS):
        for sample in tqdm(train_dataloader):
            imgs, attributres = sample
            imgs, attributes = imgs.to(DEVICE).float(), attributres.to(DEVICE).float()
            
            model.zero_grad()
            out = model(imgs)

            loss = criterion(out, attributes)
            loss.backward()

            optimizer.step()

    # TODO: Add query/gallery split



if __name__ == "__main__":
    train()