from torchvision import models
import torch

model = models.resnet18(pretrained=True)
sm = torch.jit.script(model)
sm.save("resnet-18.pt")
