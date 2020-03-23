
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: ./nb/CRF.ipynb

import sys
if __name__ == '__main__': sys.path.append('..')
import exp.common as common
from exp.common import tqdm

import operator
import numpy as np

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

def j_viterbi(logits, transitions):
    """
    Uses viterbi algorithm to find most likely tags for the given inputs.
    If constraints are applied, disallows all other transitions.
    Returns a tensor with the same size as the mask (not list)
    """
    logits = model.nodes
    mask = None
    transitions = model.crf.trans
    batch_size, sequence_length, num_tags = logits.size()

    if mask is None:
        mask = torch.ones(*logits.shape[:2], dtype=torch.bool, device=logits.device)

    # Augment transitions matrix with start and end transitions
    start_tag = num_tags
    end_tag = num_tags + 1

    # Apply transition constraints
    # inverse mask because torch.masked_fill will fill value when mask is True
    constrained_transitions = transitions.detach()
    # transitions[:num_tags, :num_tags] = constrained_transitions

    history = []
    # Transpose batch size and sequence dimensions
    mask = mask.transpose(0, 1).bool()
    logits = logits.transpose(0, 1)

    score = logits[0]

    # For each i we compute logits for the transitions from timestep i-1 to timestep i.
    # We do so in a (batch_size, num_tags, num_tags) tensor where the axes are
    # (instance, current_tag, next_tag)
    for i in range(1, sequence_length):
        # The emit scores are for time i ("next_tag") so we broadcast along the current_tag axis.
        emit_scores = logits[i].view(batch_size, 1, num_tags)
        broadcast_score = score.view(batch_size, num_tags, 1)
        inner = broadcast_score + emit_scores + constrained_transitions
        update_score, indices = inner.max(dim=1)
        # if mask[i] is True(mask[i] == 1 means this char is not padded) we use new_score,
        # otherwise last score.
        score = torch.where(mask[i].unsqueeze(1), update_score, score)
        history.append(indices)
    last_indices = score.argmax(-1)
    best_path = [last_indices]
    indices = last_indices
    # backtrace the path inversely
    for i in range(-1, -sequence_length, -1):
        recur_indices = history[i].gather(1, indices.view(batch_size, 1)).squeeze()
        indices = torch.where(mask[i], recur_indices, indices)
        best_path.insert(0, indices)
    best_path = torch.stack(best_path).transpose(0, 1)
    return best_path

# dont use this
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

        return torch.sum(- path_score + sum_over_path)

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

    mask = get_shift_mask(labels) # (batch_size, max_seq_len, num_label, num_label)
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
    trans = trans[None, :, :] # (1, num_label, num_label,)
    Z = inputs[:,0,:]
    inputs = inputs[:, 1:,:]
    times_seq_len = inputs.shape[1]
    Z.shape
    for time_idx in range(times_seq_len):
            h = inputs[:, time_idx, :] # batch_size, num_label
            Z = Z[:,:, None] # as row coeffiecient, (batch_size, num_label, 1)
            Z = Z + trans
            Z = torch.logsumexp(Z, -2)
            Z = Z + h
    Z = torch.logsumexp(Z, -1)
    return Z