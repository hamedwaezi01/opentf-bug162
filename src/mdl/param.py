import random
random.seed(0)
import torch
torch.manual_seed(0)
torch.cuda.manual_seed_all(0)
import numpy as np
np.random.seed(0)

fnn = {
    'd': 100,#size of hidden space
    'lr': 0.001,#learning rate
    'b': 100, #batch
    'e': 5, #epochs
}