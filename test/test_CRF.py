
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: ./nb/CRF.ipynb

import sys
if __name__ == '__main__': sys.path.append('..')
import exp.common as common
from pprint import pprint
def pj(*args, **kargs):
    if common.IN_JUPYTER:
        pprint(*args, **kargs)

import operator

# 模型参考https://github.com/bojone/crf/
# CRF实现参考https://github.com/bojone/crf/blob/master/crf_keras.py#L54

import pandas as pd
def read_data(Forever=False):
    sent, tags = [],[]
    con = True
    while con:
        with open('../data/CRF/ResumeNER/train.char.bmes', 'r', encoding='UTF-8') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    yield sent, tags
                    sent, tags = [],[]
                    continue

                assert len(line.split())>=2, line
                w, tag = line.split()
                sent.append(w)
                tags.append(tag)
        con = Forever

from torch.utils.data import DataLoader
# next(read_data())

import sure
from collections import Counter

# 准备数据
# Counter return 0 for unknow key
class C2ID(Counter):

    # 0 for unknow
    def __init__(self):
        super().__init__(self)
        self.min_freq = 1
        # 0 for unknow
        self.indexer = 1
        self.freq_cnt = Counter()

    def touchc(self, c):
        self.freq_cnt[c] += 1

    def touchs(self, s):
        for c in s:
            self.touchc(c)

    def update_index(self):
        for k,v in self.freq_cnt.items():
            if v < self.min_freq: continue
            if k in self: continue
            self[k] = self.indexer
            self.indexer += 1

c2id = C2ID()
tag2id = C2ID()
for sent, tags in read_data():
    c2id.touchs(sent)
    tag2id.touchs(tags)

# token 的分布

def is_breaker(c,t):
    if c2id[c] == 0:
        if t[0] == 'B':return True
        if t[0] == 'M':return True
        if t[0] == 'S':return True
    return False

def check_breaker():
    max_len = 0
    breaker_c = []
    for sent, tags in read_data():
        max_len = max(len(sent), max_len)
        for c, t in zip(sent, tags):
            if is_breaker(c, t): breaker_c.append(c)
    return max_len, breaker_c

# sorted(c2id.freq_cnt.items(), key=operator.itemgetter(1))[:30]
df = pd.DataFrame(c2id.freq_cnt.items())
mxlen, breaker_c = check_breaker()

# 先不考虑去除低频项
c2id.update_index() # 0 for padding
tag2id.update_index() # 0 for unknown char
print('mxlen', mxlen, len(breaker_c))
import pandas  as pd
# df = df.sort_values(by=1)

# df.describe()
# c2id.min_freq = 2
# c2id.update_index()
# 检查有没有打断标签


# token 的分布
import pandas  as pd
sorted(c2id.freq_cnt.items(), key=operator.itemgetter(1))[:30]
df = pd.DataFrame(c2id.freq_cnt.items())
df = df.sort_values(by=1)
df.describe()

# token 的分布
import pandas  as pd
sorted(tag2id.freq_cnt.items(), key=operator.itemgetter(1))[:30]
df = pd.DataFrame(tag2id.freq_cnt.items())
# df = df.sort_values(by=1)
# df.describe()
df[ list(map(lambda x:x[0] == 'B' or x[0] == 'S', df[0]) )][1].sum()
# df

import numpy as np
cnt = 0
batch_size = 5
X = []
Y = []
for x, y in read_data():
    cnt += 1
    X.append(list(map(  c2id.__getitem__, x)))
    Y.append(list(map(tag2id.__getitem__, y)))

    if cnt == batch_size:
        break


def padding(X):
    X = list(X)
    max_len = max(map(len, X))
    for i,x in enumerate(X):
        X[i] = x + [0] * (max_len - len(x))
    return X


# np_X = np.zeros((cnt, max_len, )) # batch_size, max_seq_len,
train = (X, Y)
train = list(map(padding,  train))
train = list(map(np.array, train))
# torch.LongTensor(X)
list(map(lambda x:x.shape, train))

import torch
from torch import nn
def onehot(y, num):
    """
    y: shape (batch_size, max_seq_len)
    """
    assert len(y.shape) == 2, y.shape
    eye = np.eye(num)
    return eye[y]

onehot(np.array(
    [
        [1,2,3],
        [0,3,1]
    ]
), 4)

import torch.functional as F
num_embeddings = len(c2id) + 1
num_label = len(tag2id) + 1
embedding_dim = 64
lstm_dim = 32
train_X, train_Y = train
train_Y = onehot(train_Y, num_label)
train_Y = torch.Tensor(train_Y)
train_X = torch.LongTensor(train_X)
# train_X


def get_shift_mask(labels):
    """
    labels: (batch_size, max_seq_len, num_label) in onehot all element should be 1/0
    turn num_labels into matrix of (num_label, num_label) where m[ y[i] ][ y[i+1] ] = 1, 0 for else
    return (batch_size, max_seq_len, num_label, num_label)
    """
    labels1 = labels[:, :-1, ] # y[i]

    labels2 = labels[:, 1:] # y[i + 1]

    labels1 = labels1[:, :, :, None] # as 系数, row indexer
    labels2 = labels2[:, :, None, :] # as row, col indexer

    shift_mask = labels1 * labels2
    return shift_mask

import sure
tmp_num_label = 5
tmp_labels_raw = [[1,2,3,4], [3,3,3,2]]
tmp_labels = np.array(tmp_labels_raw)
tmp_labels = onehot(tmp_labels, tmp_num_label)
shift_mask = get_shift_mask(tmp_labels)

# for batch
for tags, mask in zip(tmp_labels_raw, shift_mask):

    # for seq
    # len = max_seq_len - 1
    for y_i, y_j,matrix in zip(tags[:-1], tags[1:], mask):
        # y_j  = y[i+1]
        matrix = np.copy(matrix)
        matrix[y_i][y_j] -= 1 # only matrix[y_i][y_j] = 1, else 0
        matrix.sum().should.eql(0)


import math
# 👴的CRF
class CRF(nn.Module):
    def __init__(self, num_label):
        super().__init__()
        # 先不考虑padding标签的问题
        # 先不考虑mask的问题
        self.trans = nn.Parameter(torch.Tensor(num_label, num_label))
        nn.init.kaiming_uniform_(self.trans, a=math.sqrt(5))

    def _path_score(self, inputs, labels, trans = None):
        trans = self.trans if trans is None else trans
        return _path_score(inputs, labels, trans)

    def _sum_over_path_score(self, inputs, labels, trans = None):

        trans = self.trans if trans is None else trans
        return _sum_over_path_score(inputs, labels, trans)

    def forward(self, inputs, labels):
        """
        inputs: (batch_size, max_seq_len, label_num) embed with latent dim label_nun
        labels: (batch_size, max_seq_len, label_num) ground-truth label in onehot
        return: score
       """
        path_score = self._path_score(inputs, labels)
        sum_over_path = self._sum_over_path_score(inputs, labels)

        return - path_score + sum_over_path

# trans[i][j]表示从i标签转移至j标签
def _path_score(inputs, labels, trans):
    """
    score of h(y[i]) ground-truch y[i] plus its g[y[i]][y[i+1]], inputs for h, trans for g
    inputs.size() # batch_size, max_seq_len, num_label
    trans.size() # num_label, num_label
    labels.size() #batch_size, max_seq_len, num_label
    """
    sum_h_score = inputs * labels # batch_size, max_seq_len, num_label
    sum_h_score = sum_h_score.sum(-1, ) # batch_size, max_seq_len
    sum_h_score = sum_h_score.sum(-1, keepdim = True) # batch_size, 1

    mask = get_shift_mask(labels)
    sum_g_score = mask * trans[None, None]
    sum_g_score = sum_g_score.sum((-1, -2)) # batch_size, max_seq_len
    sum_g_score = sum_g_score.sum((-1), keepdim = True) # batch_size, 1
    path_score = sum_g_score + sum_h_score
    path_score.shape # batc_size, 1
    return path_score

def _sum_over_path_score(inputs, labels, trans):
    """
    @see https://kexue.fm/archives/5542#%E5%BD%92%E4%B8%80%E5%8C%96%E5%9B%A0%E5%AD%90
    """
    trans = trans[None, :, :]
    Z = inputs[:,0,:]
    inputs = inputs[:, 1:,:]
    times_seq_len = inputs.shape[1]
    Z.shape
    for time_idx in range(times_seq_len):
            h = inputs[:, time_idx, :]
            Z = Z[:,:, None] # as row coeffiecient
            Z = Z + trans
            Z = torch.logsumexp(Z, -2)
            Z = Z + h
    Z = Z.sum(-1)
    return Z

class TestNER(nn.Module):
    def __init__(self):
        super().__init__()
        emb = nn.Embedding(num_embeddings, embedding_dim)
        lstm = nn.LSTM(input_size=embedding_dim, hidden_size=lstm_dim)
        fc = nn.Linear(lstm_dim, num_label)
        crf = CRF(num_label)

    def forward(self, inputs, labels):
        x = emb(inputs)
        x, (hn, cn)= lstm(x)
        x = fc(x)
        x = crf(x, labels)
        return x

