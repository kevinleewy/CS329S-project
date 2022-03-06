import torch.nn as nn
from torchvision import models

class ResnetDummy(nn.Module):
    def __init__(self, num_labels: int, embedding_dim: int = 512, freeze_pretrain: bool=True):
        super(ResnetDummy, self).__init__()
        self.num_labels = num_labels
        self.resnet = models.resnet50(pretrained=True)

        # Replace existing FC layer with custom one
        num_ftrs = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(num_ftrs, embedding_dim)
        self.classifier = nn.Sequential(
            nn.ReLU(),
            nn.Linear(embedding_dim, self.num_labels)
        )

        if freeze_pretrain:
            for param in self.resnet.parameters():
                param.require_grad = False 
            for param in self.resnet.fc.parameters():
                param.require_grad = True 


    def forward(self, x):
        x = self.embed(x)
        x = self.classifier(x)
        return x

    def embed(self, x):
        return self.resnet(x)
