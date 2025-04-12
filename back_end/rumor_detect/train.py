# train.py
import torch
from torch import optim
from tqdm import tqdm
import os
import model
import torch.nn as nn

class Trainer:
    def __init__(self, model, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.best_acc = 0.0

    def train(self, train_loader, test_loader, epochs, lr, save_path='./best_model.pkl'):
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()

        for epoch in range(epochs):
            self.model.train()
            total_loss = 0.0
            correct = 0
            total = 0

            with tqdm(train_loader, desc=f'Epoch {epoch + 1}/{epochs}') as pbar:
                for inputs, labels in pbar:
                    inputs, labels = inputs.to(self.device), labels.to(self.device)
                    optimizer.zero_grad()

                    outputs = self.model(inputs)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()

                    total_loss += loss.item()
                    _, predicted = outputs.max(1)
                    correct += predicted.eq(labels).sum().item()
                    total += labels.size(0)
                    pbar.set_postfix(loss=loss.item())

            train_acc = 100. * correct / total
            test_acc = self.evaluate(test_loader)

            print(f'Epoch {epoch + 1} | Train Acc: {train_acc:.2f}% | Test Acc: {test_acc:.2f}%')

            if test_acc > self.best_acc:
                self.best_acc = test_acc
                torch.save(self.model.state_dict(), save_path)
                print(f'Best model saved with acc: {test_acc:.2f}%')

    def evaluate(self, test_loader):
        self.model.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                _, predicted = outputs.max(1)
                correct += predicted.eq(labels).sum().item()
                total += labels.size(0)

        return 100. * correct / total