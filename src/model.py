import torch.nn as nn
from torchvision import models

class ResnetDummy(nn.Module):
    def __init__(self, num_labels: int, freeze_pretrain: bool=True):
        super(ResnetDummy, self).__init__()
        self.num_labels = num_labels
        self.resnet = models.resnet50(pretrained=True)

        # Replace existing FC layer with custom one
        num_ftrs = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(num_ftrs, self.num_labels)

        if freeze_pretrain:
            for param in self.resnet.parameters():
                param.require_grad = False 
            for param in self.resnet.fc.parameters():
                param.require_grad = True 


    def forward(self, x):
        x = self.resnet(x)
        return x