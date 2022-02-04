import torch
from torch.utils.data import Dataset, DataLoader, Subset
from torch import nn
from tqdm import tqdm

from model import ResnetDummy
from dataloader import load_datasets

BASE_PATH = '/Users/kevinlee/Data/Stanford/CS329S/project/CS329S-project/data/In-shop Clothes Retrieval Benchmark'
# BASE_PATH = '/scratch/users/avento/deepfashion'
LEARNING_RATE = 0.01
EPOCHS = 50
BATCH_SIZE = 64
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

def train():

    datasets, num_labels = load_datasets(base_path=BASE_PATH)

    train_dataloader = torch.utils.data.DataLoader(datasets['train'],
                                        batch_size=BATCH_SIZE,
                                        shuffle=True,
                                        pin_memory=True)
    eval_dataloader = torch.utils.data.DataLoader(datasets['validation'],
                                        batch_size=BATCH_SIZE,
                                        shuffle=False,
                                        pin_memory=True)
    
    model = ResnetDummy(num_labels, freeze_pretrain=False)
    model = model.to(DEVICE)

    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    criterion = nn.BCEWithLogitsLoss(reduction='mean') # TODO: Confirm this works when doing vector to vector within each sample

    for epoch in range(EPOCHS):
        model.train()
        for imgs, attributes in tqdm(train_dataloader):
            imgs, attributes = imgs.to(DEVICE).float(), attributes.to(DEVICE).float()
            
            model.zero_grad()
            out = model(imgs)

            loss = criterion(out, attributes)
            loss.backward()

            optimizer.step()

        model.eval()
        with torch.no_grad():
            for imgs, attributes in tqdm(eval_dataloader):
                imgs, attributes = imgs.to(DEVICE).float(), attributes.to(DEVICE).float()
                out = model(imgs)

            # TODO: Calculate accuracy/F1

            # TODO: Save if best accuracy/F1

        # TODO: Save every N epochs



    # TODO: Add query/gallery split



if __name__ == "__main__":
    train()