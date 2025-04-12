# predict.py
import torch
import pickle

from keras_preprocessing.sequence import pad_sequences

from rumor_detect.model import Transformer
import torch


# print(torch.__version__)

class Predictor:
    def __init__(self, model_path, dict_path='./rumor_detect', device='cpu'):
        self.device = device
        self.word_dict = pickle.load(open(f'{dict_path}/word_dict.pk', 'rb'))
        self.label_dict = {v: k for k, v in pickle.load(open(f'{dict_path}/label_dict.pk', 'rb')).items()}
        self.model = self._load_model(model_path)
        self.max_len = 180  # 需与训练时一致

    def _load_model(self, model_path):
        model = Transformer(len(self.word_dict), 20, 2)  # 参数需与训练时一致
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.eval()
        return model.to(self.device)

    def predict(self, text):
        try:
            x = [[self.word_dict.get(char, 0) for char in text]]
            x = torch.LongTensor(pad_sequences(x, maxlen=self.max_len, padding='post', value=0))
            with torch.no_grad():
                output = self.model(x.to(self.device))
            pred = output.argmax().item()
            return self.label_dict[pred]
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return None


if __name__ == "__main__":
    predictor = Predictor('best_model.pkl')
    text = input("请输入要检测的文字：")
    is_rumor = predictor.predict(text)

    print("谣言") if is_rumor else print("非谣言")
