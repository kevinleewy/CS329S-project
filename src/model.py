import torch.nn as nn
from torchvision import models

class ResnetDummy(nn.Module):
    def __init__(self, freeze_pretrain=True):
        super(ResnetDummy, self).__init__()
        self.resnet = models.resnet50(pretrained=True)

        if freeze_pretrain:
            for param in self.resnet.parameters():
                param.requires_grad = False

        self.fc = nn.Linear(1000, 463)
        self.sigmoid = nn.Sigmoid()


    def forward(self, x):
        x = self.resnet(x)
        x = self.fc(x)
        x = self.sigmoid(x)
        return x