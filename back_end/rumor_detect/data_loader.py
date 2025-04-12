# data_loader.py
import pickle
import numpy as np
import pandas as pd
import torch
from keras_preprocessing.sequence import pad_sequences
from torch.utils.data import TensorDataset


# from torch.utils.data import TensorDataset


class DataProcessor:
    def __init__(self, max_len=180):
        self.word_dict = None
        self.label_dict = None
        self.max_len = max_len

    def build_vocab(self, texts):
        chars = set(''.join(texts))
        self.word_dict = {char: i + 1 for i, char in enumerate(chars)}
        self.word_dict['<PAD>'] = 0

    def build_label_dict(self, labels):
        unique_labels = list(set(labels))
        self.label_dict = {label: i for i, label in enumerate(unique_labels)}

    def save_dicts(self, save_dir='./'):
        with open(f'{save_dir}/word_dict.pk', 'wb') as f:
            pickle.dump(self.word_dict, f)
        with open(f'{save_dir}/label_dict.pk', 'wb') as f:
            pickle.dump(self.label_dict, f)

    def load_dicts(self, load_dir='./'):
        with open(f'{load_dir}/word_dict.pk', 'rb') as f:
            self.word_dict = pickle.load(f)
        with open(f'{load_dir}/label_dict.pk', 'rb') as f:
            self.label_dict = pickle.load(f)

    def preprocess(self, df, is_train=False):
        texts = df['text'].tolist()
        labels = df['label'].tolist()

        if is_train:
            self.build_vocab(texts)
            self.build_label_dict(labels)

        x = [[self.word_dict.get(char, 0) for char in text] for text in texts]
        x = pad_sequences(x, maxlen=self.max_len, padding='post', value=0)
        y = [self.label_dict[label] for label in labels]
        return x, np.array(y)

    def create_dataloader(self, x, y, batch_size=32, shuffle=True):
        dataset = TensorDataset(torch.LongTensor(x), torch.LongTensor(y))
        return torch.utils.data.DataLoader(dataset, batch_size, shuffle)