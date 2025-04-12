# 训练流程
import pandas as pd

from model import Transformer
from data_loader import DataProcessor
from rumor_detect.predict import Predictor
from train import Trainer

# 数据准备
train_df = pd.read_csv('./rumor_data/train.tsv', sep='\t')
test_df = pd.read_csv('./rumor_data/test.tsv', sep='\t')

processor = DataProcessor(max_len=180)
x_train, y_train = processor.preprocess(train_df, is_train=True)
x_test, y_test = processor.preprocess(test_df, is_train=False)
processor.save_dicts()

train_loader = processor.create_dataloader(x_train, y_train, batch_size=32)
test_loader = processor.create_dataloader(x_test, y_test, batch_size=32, shuffle=False)

# 初始化模型
model = Transformer(
    vocab_size=len(processor.word_dict),
    embedding_dim=20,
    num_class=len(processor.label_dict)
)

# 训练
trainer = Trainer(model)
trainer.train(train_loader, test_loader, epochs=20, lr=0.003)

# 预测示例
predictor = Predictor('./best_model.pkl')
if predictor.predict("鸡蛋不能吃，对人体有害！"):
    print("谣言")
else:
    print("不是谣言")
