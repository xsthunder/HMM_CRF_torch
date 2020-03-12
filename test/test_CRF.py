
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

# 模型参考https://github.com/bojone/crf/
# CRF实现参考https://github.com/bojone/crf/blob/master/crf_keras.py#L54
import operator

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
        self.indexer = 0
        self.freq_cnt = Counter()
        self._reverse_dict = {}

    def touchc(self, c):
        self.freq_cnt[c] += 1

    def touchs(self, s):
        for c in s:
            self.touchc(c)

    def update_index(self):
        for k,v in self.freq_cnt.items():
            if v < self.min_freq: continue
            if k in self: continue

            self._reverse_dict[self.indexer]=k
            self[k] = self.indexer

            self.indexer += 1

    def reverse(self, idx):
        return self._reverse_dict[idx]

    def reveres_list(self, list_idx):
        return list(map(self.reverse, list_idx))

c2id = C2ID()
tag2id = C2ID()
# tag2id.indexer = 0
UNK = 'UNK'
PAD = 'PAD'
for cv in [c2id, tag2id]:
    cv.touchs([UNK, PAD])

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

# tag 的分布
import pandas  as pd
sorted(tag2id.freq_cnt.items(), key=operator.itemgetter(1))[:30]
df = pd.DataFrame(tag2id.freq_cnt.items())
# df = df.sort_values(by=1)
# df.describe()
df[ list(map(lambda x:x[0] == 'B' or x[0] == 'S', df[0]) )][1].sum()
# df
tag2id.reveres_list([1,2,3])

def padding(padding_idx,X):
    X = list(X)
    max_len = max(map(len, X))
    for i,x in enumerate(X):
        X[i] = x + [padding_idx] * (max_len - len(x))
    return X

import torch
from torch import nn
def onehot(y, dim_size):
    """
    y: shape (batch_size, max_seq_len)
    """
    assert len(y.shape) == 2, y.shape
    eye = np.eye(dim_size)
    return eye[y]

import numpy as np
from functools import partial
from pprint import pprint
from tqdm import tqdm
import math
assert isinstance( math.ceil(0.3), int)

class get_data():
    def __init__(self, batch_size = 2):
        self.batch_size = batch_size
        self.len = math.ceil( len(list(read_data()))/batch_size )

    def __iter__(self):
        batch_size = self.batch_size
        cnt = 0
        X = []
        Y = []
        def set_train():
            a = padding(c2id[PAD]  , X)
            b = padding(tag2id[PAD], Y)
            return tuple(map( np.array, (a,b)))
        for x, y in read_data():
            cnt += 1
            X.append(list(map(  c2id.__getitem__, x)))
            Y.append(list(map(tag2id.__getitem__, y)))

            if cnt == batch_size:
                cnt = 0
                yield set_train()

        return set_train()

    def __len__(self):
        return self.len

for x in tqdm(get_data()):
    break
print(list(map(np.shape, x)))
x

onehot(np.array(
    [
        [1,2,3],
        [0,3,1]
    ]
), 4)

import sure
from queue import PriorityQueue
class TopK:
    def __init__(self, k, topks = None):
        # (priority_number, data)
#         pq = PriorityQueue(k)
        assert k == 1, "not implemented"

        self.m_inf = -float('inf')
        self.data = None
        self.score = self.m_inf

        if topks is not None:
            assert len(topks) >= k
            for t in topks:
                self.put( t.get_max_data(), t.get_max_score(),)
            return

#         for i in range(k):
#             pq.put_nowait((m_inf))
#         self.pq = pq

    def put(self,  data, score,):
        assert len(data) >= 1
        if self.score is self.m_inf:
            pass
        else :
            assert type(score) == type(self.score), "score type muse consit"
        if score > self.score:
            self.score, self.data = score, data

    def __str__(self):
        return (self.score, self.data).__str__()

    def get_max_score(self):
        return self.score

    def get_max_data(self):
        return self.data

    def get_kth_data(self, k):
        raise NotImplementedError

    def get_kth_score(self, k):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()



topk = TopK(1)
for i in range(10):
    topk.put( [i],i+10,)
#     print(topk.data)
# assert topk.
topk.get_max_data().should.eql([9])
topk.get_max_score().should.eql(19)

topk = TopK(1)
topk.put( [1], 1,)
for i in range(1, 10):
    t = list(range(i)) + topk.get_max_data()
    topk.put(t, i)
topk.m_inf.should.eql(topk.m_inf)

def viterbi(nodes,trans_p, initial_state = None, topk = 1, start_p = None):
    """
    nodes: array, [{"<TAG>": <float>}]
    trans_p: dict, {"<TAG_A>": {"TAG_B": <float>}}, TAG_A -> TAG-B
    return_max=True: bool, set to False if your want to avoid ill endding tag and find your own.
    initial_state=None: None or list to avoid impossible starting tags
    start_p: P(o1), may be nessary
    all float number in log form
    """
    assert len(nodes.shape) == 2,len(nodes.shape)  # max_seq_len, label_num
    kth = 1
    if initial_state is None:
        initial_state = nodes[0]
        nodes = nodes[1:]

    def init_tok():return TopK(kth)

    def init_toks(): return [init_tok() for i in range(nodes.shape[-1])]

    last_best_nodes = init_toks()
    next_best_nodes = init_toks()


    for idx, (tk,score) in enumerate( zip(last_best_nodes , initial_state)):
        tk.put([idx], score)

    for node in nodes:
        for t,v in enumerate(node):

            current_best_node = init_tok() # for t

            for topk in last_best_nodes:
                path = topk.get_max_data()
                score = topk.get_max_score()

                last_t = path[-1]
                new_path = path + [t]
                tran = trans_p[last_t][t]

                current_best_node.put(new_path, score + tran + v)

            next_best_nodes[t] = current_best_node

        next_best_nodes, last_best_nodes =  last_best_nodes, next_best_nodes,

    topk = TopK(1, last_best_nodes)

    return topk.get_max_data()

nodes = [
    [1, 2, 1],
    [1, 1, 3],
    [4, 1, 3],
]
trans = [
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
]
nodes, trans = map(np.array, [nodes, trans])
viterbi(nodes, trans).should.eql([1,2,0])

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

    def _path_score(self, inputs, labels):
        return _path_score(inputs, labels, self.trans)

    def _sum_over_path_score(self, inputs, labels):
        return _sum_over_path_score(inputs, labels, self.trans)

    def veterbi_decode(self, nodes):
        return _veterbi_decode(nodes, self.trans.detached().numpy())

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

import torch.functional as F
# 空也放进去映射了，不用加1，否则回出现随机的tag2id.reserve，键值不存在错误。
num_embeddings = len(c2id)
num_label = len(tag2id)
embedding_dim = 64
lstm_dim = 32


# 不过crf的，用交叉熵
class TestNER(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb = nn.Embedding(num_embeddings, embedding_dim)
        self.lstm = nn.LSTM(input_size=embedding_dim, hidden_size=lstm_dim)
        self.fc = nn.Linear(lstm_dim, num_label)
        self.crf = CRF(num_label)
        self.nodes = None

    def decode(self):
        self.crf.veterbi_decode(self.nodes.detach.numpy())

    def forward_nodes(self, inputs):
        x = self.emb(inputs)
        x, (hn, cn)= self.lstm(x)
        x = self.fc(x)
        self.nodes = x
        return x


    def forward(self, inputs, labels):
        x = self.forward_nodes(inputs)
        x = self.crf(x, labels)
        return x

lr = 1e-4
testner = TestNER()
for train in get_data():
    break;
train_X, train_Y = train
train_Y = onehot(train_Y, num_label)
train_Y = torch.Tensor(train_Y)
train_X = torch.LongTensor(train_X)
for ep in range(20):
    testner.zero_grad()
    outputs = testner(train_X, train_Y)
#     print(outputs.shape, train_Y.shape)
#     loss = nn.CrossEntropyLoss(outputs, train_Y)
    loss = outputs.sum()
#     print(loss)
#     print(loss)
    loss.backward()
    with torch.no_grad() :
        for p in testner.parameters():
            p.data.add_(-lr, p.grad.data)

#     testner??
#     break;

from seqeval.metrics import classification_report

class Parser:
    def __init__(self, model):
        self.model = model

    def parse_one_seq(self,seq_nodes, trans = None):
        if trans is None:
            trans = self.model.crf.trans.detach().numpy()
        pred=viterbi(seq_nodes, trans)
        return pred

    def parse_nodes(self, nodes=None, trans=None):
        if nodes is None:
            nodes = self.model.nodes.detach().numpy()
        if trans is None:
            trans = self.model.crf.trans.detach().numpy()

        parse = partial(self.parse_one_seq, trans = trans)
        self.y_pred = list(map(parse, nodes))
        self.y_pred = np.array(self.y_pred)
        return self.y_pred

    def parse_test(self, test_X, test_Y):
        assert len(test_Y.shape) == 2, "please give test_Y in shape (batch_size, max_seq_len) tag in sparse int, given"+str(test_Y.shape)
        with torch.no_grad():
            nodes = self.model.forward_nodes(test_X)
        y_pred = self.parse_nodes(nodes)
        return self.cvt_report(test_Y, y_pred)

    def cvt_report(self, y_pred, y_true):
        y_pred, y_true = map(self.cvt, (y_pred, y_true))
        print(list(map(np.shape, (y_pred, y_true ))))
        print(list(map(np.dtype, (y_pred, y_true ))))
        print((y_pred, y_true ))
        return classification_report(y_true, y_pred)

    def cvt(self, y):
        return list(map(tag2id.reveres_list, y))

parser = Parser(testner)
y_pred = parser.parse_nodes()
y_pred = parser.cvt(y_pred)
y_true = parser.cvt(train[1])
print(classification_report(y_true, y_pred))

assert isinstance(y_pred, list)
len(y_pred).should.eql(2)

del testner, train, train_X, train_Y,  y_pred, y_true

# TODO move this to common if duplicates
import tqdm as _tqdm
def _empty_tqdm(g):
    """
    for travis
    """
    try:
        l = len(l)
    except:
        l = '?'
    for i,x in enumerate(g):
        i = str(i)
        print(f"({i}/{l})", end='')
        yield x

if common.IN_JUPYTER:
    tqdm = _tqdm.notebook.tqdm
elif common.IN_TRAVIS:
    tqdm = _empty_tqdm
else :
    tqdm = _tqdm.tqdm


for i in _empty_tqdm(range(10)):
    print(i)
    pass
for i in _empty_tqdm(get_data()):
    a, b = i
    break

test_ner = TestNER()
def train_ep():
    cnt = 0
    for train in tqdm(get_data(10)):
        test_ner.zero_grad()

        if common.IN_JUPYTER or common.IN_TRAVIS:
            # avoid overtime
            if cnt > 10:
                break
        cnt += 1

        train_X, train_Y = train
        train_Y = onehot(train_Y, num_label)
        train_Y = torch.Tensor(train_Y)
        train_X = torch.LongTensor(train_X)

        outputs = test_ner(train_X, train_Y)
    #     print(outputs.shape, train_Y.shape)
    #     loss = nn.CrossEntropyLoss(outputs, train_Y)
        loss = outputs.sum()
        loss.backward()
        with torch.no_grad() :
            for p in test_ner.parameters():
                p.data.add_(-lr, p.grad.data)

    return loss
for ep in tqdm(range(10)):
    print(train_ep())