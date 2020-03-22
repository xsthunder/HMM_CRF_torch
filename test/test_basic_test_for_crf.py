
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: ./nb/basic_test_for_crf.ipynb

import sys
if __name__ == '__main__': sys.path.append('..')
import exp.common as common
from pprint import pprint
def pj(*args, **kargs):
    if common.IN_JUPYTER:
        pprint(*args, **kargs)

import sure

import torch
from torch import optim
from exp.CRF import CRF
from exp.CRF import onehot
import numpy as np
num_label = 3
inputs = np.array([
    # seq
    [
        [0.1, 0.2, 0.1],
        [0.1, 0.2, 0.3],
    ]
])
LABELS = np.array([
    [1,1]
])
labels = onehot(LABELS, 3)
(inputs, labels, ) = map(torch.Tensor,  (inputs, labels, ) )
(LABELS, ) = map(torch.LongTensor, (LABELS, ))
MASK = torch.ones_like(LABELS, dtype=torch.bool)

# 没有提前取负号
from torch import nn
from lib.ConditionalRandomField import ConditionalRandomField, allowed_transitions
label_dic = {'O':0, 'B-a':1, 'I-a':2}
constraints = allowed_transitions(constraint_type='BIO', labels=label_dic)

class J_crf(nn.Module):
    def __init__(self):
        super().__init__()
        self.crf = ConditionalRandomField(num_tags=len(label_dic), constraints=constraints, include_start_end_transitions=False)

    def forward(self, inputs, labels):
        return -self.crf(inputs, labels)

import matplotlib.pyplot as plt
def pxy(x, y, name='idk'):
    name = str(name)
    fig, = plt.plot(x,y, )
    fig.set_label(name)
    plt.legend()
# pxy([1,2], [3,2], '2')
# pxy([1,2], [5,6], '1')

# (路劲分数/配分函数) < 1
# log(路劲分数/配分函数) < 0
# -log(路劲分数/配分函数) > 0
args = (inputs, labels)
loss = crf(inputs, labels)
assert torch.all(loss > 0)

sop = crf._sum_over_path_score(*args).sum()
ps = crf._path_score(*args).sum()
# loss == spo - ps
# sum of path 应该  > path score
# 看了一边代码感觉没问题
# 看了一下trans的初始化，有点区别，感觉没啥问题，都是有正有负，不过j的variance要大一些
assert sop > ps, "sum of path 应该  > path score"
del crf