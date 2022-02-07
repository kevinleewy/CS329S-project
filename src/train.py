import numpy as np
import os
import random
import torch
from torch import nn
from tqdm import tqdm
from datetime import datetime

from model import ResnetDummy
from dataloader import load_datasets

# BASE_PATH = '/Users/kevinlee/Data/Stanford/CS329S/project/CS329S-project/data/In-shop Clothes Retrieval Benchmark'
BASE_PATH = '/scratch/users/avento/deepfashion'
LEARNING_RATE = 0.01
EPOCHS = 50
BATCH_SIZE = 64
WEIGHTS_SAVE_FREQUENCY = 10
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
RNG_SEED = 17
NOW = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def train():

    set_seed(RNG_SEED)

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

    best_accuracy = 0.0

    os.makedirs(os.path.join(BASE_PATH, NOW), exist_ok=True)

    for epoch in range(EPOCHS):
        model.train()
        with tqdm(train_dataloader) as pbar:
            for imgs, attributes in pbar:
                imgs, attributes = imgs.to(DEVICE).float(), attributes.to(DEVICE).float()
                
                model.zero_grad()
                out = model(imgs)

                loss = criterion(out, attributes)
                loss.backward()

                optimizer.step()

                pbar.set_description('Train Loss: {:.4f}'.format(
                    loss.item(),
                ))

        model.eval()
        with torch.no_grad():
            correct = 0.
            total = 0.
            with tqdm(eval_dataloader) as pbar:
                for imgs, attributes in pbar:
                    imgs, attributes = imgs.to(DEVICE).float(), attributes.to(DEVICE).float()
                    out = model(imgs)

                    outputs = torch.sigmoid(out)
                    predictions = torch.round(outputs)
                    total += attributes.size(0) * attributes.size(1)
                    correct += (predictions == attributes).sum().cpu().item()
                    accuracy = 100 * correct / (total + 1e-12)

                    pbar.set_description('Validation Accuracy: {:.4f}'.format(accuracy))

                # Save model if achieved best accuracy
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    torch.save(model.state_dict(), os.path.join(BASE_PATH, NOW, "best_model.pt"))

        if epoch % WEIGHTS_SAVE_FREQUENCY == 0:
            torch.save({
                "epoch": epoch,
                "best_accuracy": best_accuracy,
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
            }, os.path.join(BASE_PATH, NOW, f"checkpoint_{epoch}.pt"))
    
    # Save one last checkpoint
    torch.save({
        "epoch": epoch,
        "best_accuracy": best_accuracy,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
    }, os.path.join(BASE_PATH, NOW, f"checkpoint_{epoch}.pt"))


    # TODO: Add query/gallery split



if __name__ == "__main__":
    train()