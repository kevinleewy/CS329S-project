import numpy as np
import os
import random
import torch
from torch import nn
from tqdm import tqdm
from datetime import datetime
import pickle

from loss import SoftDiceLoss
from metrics import mean_iou, dice_coefficient
from model import ResnetDummy
from unet import Unet
from dataloader import load_datasets
from utils import compute_imbalanced_class_weights, compute_f1

# BASE_PATH = '/Users/kevinlee/Data/Stanford/CS329S/project/CS329S-project/data/In-shop Clothes Retrieval Benchmark'
BASE_PATH = '/scratch/users/avento/deepfashion'
LEARNING_RATE = 0.001
EPOCHS = 50
BATCH_SIZE = 64
WEIGHTS_SAVE_FREQUENCY = 10
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
RNG_SEED = 17
NOW = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
NUM_LABELS = 36 # 13, 36, or 347
SEGMENT = True
LAMBD = 0.1

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def train():

    set_seed(RNG_SEED)

    datasets, attr_counts = load_datasets(base_path=BASE_PATH, num_labels=NUM_LABELS, segment=SEGMENT)
    num_labels = attr_counts.shape[0]
    weights = compute_imbalanced_class_weights(attr_counts, as_tensor=True)
    weights = weights.to(DEVICE)

    train_dataloader = torch.utils.data.DataLoader(datasets['train'],
                                        batch_size=BATCH_SIZE,
                                        shuffle=True,
                                        pin_memory=True)
    eval_dataloader = torch.utils.data.DataLoader(datasets['validation'],
                                        batch_size=BATCH_SIZE,
                                        shuffle=False,
                                        pin_memory=True)
    
    if SEGMENT:
        model = Unet(num_labels=num_labels, n_classes=1, pretrained_path=os.path.join(BASE_PATH, 'pretrained_unet.pt'))
        seg_criterion = SoftDiceLoss()
    else:
        model = ResnetDummy(num_labels, freeze_pretrain=False)
    model = model.to(DEVICE)

    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    criterion = nn.BCEWithLogitsLoss(weight=weights, reduction='mean') # TODO: Confirm this works when doing vector to vector within each sample

    best_f1 = 0.0

    os.makedirs(os.path.join(BASE_PATH, NOW), exist_ok=True)

    accs = []
    f1s = []
    for epoch in range(EPOCHS):
        model.train()
        with tqdm(train_dataloader) as pbar:
            for imgs, attributes, segs, segLossMask in pbar:
                imgs, attributes = imgs.to(DEVICE).float(), attributes.to(DEVICE).float()
                
                if SEGMENT:
                    segs.to(DEVICE).float()
                    segLossMask.to(DEVICE)

                model.zero_grad()
                out = model(imgs)

                if SEGMENT:
                    classification_loss = criterion(out[0], attributes)
                    seg_loss = seg_criterion(segLossMask.reshape(-1,1,1,1) * out[1], segs)
                    loss = classification_loss + LAMBD * seg_loss
                else:
                    loss = criterion(out, attributes)

                loss.backward()

                optimizer.step()

                pbar.set_description('Train Loss: {:.4f}'.format(
                    loss.item(),
                ))


        model.eval()
        all_probs = []
        # all_dice_accs = []
        # all_ious = []
        all_attributes = []
        with torch.no_grad():
            correct = 0.
            total = 0.
            with tqdm(eval_dataloader) as pbar:
                for imgs, attributes, segs, segLossMask in pbar:
                    imgs, attributes = imgs.to(DEVICE).float(), attributes.to(DEVICE).float()

                    if SEGMENT:
                        segs.to(DEVICE).float()
                        segLossMask.to(DEVICE)

                    out = model(imgs)

                    if SEGMENT:
                        outputs = torch.sigmoid(out[0])
                        # dice_accs = dice_coefficient(segLossMask.reshape(-1,1,1,1) * out[1], segs)
                    else:
                        outputs = torch.sigmoid(out)
                    predictions = torch.round(outputs)
                    total += attributes.size(0) * attributes.size(1)
                    correct += (predictions == attributes).sum().cpu().item()
                    accuracy = 100 * correct / (total + 1e-12)
                    f1 = compute_f1(attributes.cpu(), predictions.cpu(), avg_per_attribute=True)

                    all_probs.append(outputs.cpu())
                    all_attributes.append(attributes.cpu())

                    pbar.set_description('Validation Accuracy: {:.4f}, F1 Score: {:.4f}'.format(accuracy, f1))

        accs.append(accuracy)
        all_probs = np.concatenate(all_probs, axis=0)
        all_attributes = np.concatenate(all_attributes, axis=0)
        epoch_f1 = compute_f1(all_attributes, np.round(all_probs), avg_per_attribute=True)
        f1s.append(epoch_f1)

        # Save model if achieved best f1
        if epoch_f1 > best_f1:
            print(f"Saving best model at epoch = {epoch} with f1 = {epoch_f1}")
            best_f1 = epoch_f1
            torch.save(model.state_dict(), os.path.join(BASE_PATH, NOW, "best_model.pt"))

        if epoch % WEIGHTS_SAVE_FREQUENCY == 0:
            torch.save({
                "epoch": epoch,
                "best_f1": best_f1,
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
            }, os.path.join(BASE_PATH, NOW, f"checkpoint_{epoch}.pt"))
                        
    # Save one last checkpoint
    torch.save({
        "epoch": epoch,
        "best_f1": best_f1,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
    }, os.path.join(BASE_PATH, NOW, f"checkpoint_{epoch}.pt"))

    # Save a pickle file for analysis
    with open(os.path.join(BASE_PATH, NOW, f"dict_{epoch}.pickle"), 'wb') as handle:
        pickle.dump({
            "val_outputs": all_probs,           # outputs for last epoch
            "val_attributes": all_attributes,   # attributes for last epoch
            "val_accuracies": accs,             # accuracies across all epochs
            "val_f1s": f1s,                     # f1 scores across all epochs
        }, handle, protocol=pickle.HIGHEST_PROTOCOL)


    # TODO: Add query/gallery split



if __name__ == "__main__":
    train()
