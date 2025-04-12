# model.py
import torch
import math
import torch.nn as nn

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=128):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * -(math.log(10000.0)/d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1)].requires_grad_(False)
        return self.dropout(x)

class Transformer(nn.Module):
    def __init__(self, vocab_size, embedding_dim, num_class,
                 feedforward_dim=256, num_head=2, num_layers=3,
                 dropout=0.1, max_len=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.positional_encoding = PositionalEncoding(embedding_dim, dropout, max_len)
        encoder_layer = nn.TransformerEncoderLayer(embedding_dim, num_head,
                                                   feedforward_dim, dropout)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc = nn.Linear(embedding_dim, num_class)

    def forward(self, x):
        x = x.transpose(0, 1)
        x = self.embedding(x)
        x = self.positional_encoding(x)
        x = self.transformer(x)
        x = x.mean(axis=0)
        return self.fc(x)