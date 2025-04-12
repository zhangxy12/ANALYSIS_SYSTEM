import torch
from .model import BertClassifier
from transformers import BertTokenizer, BertConfig
import os

class TextClassifier:
    def __init__(self):
        # 定义标签列表
        self.labels = ['体育', '娱乐', '家居', '房产', '教育', '时尚', '时政', '游戏', '科技', '财经']

        # 假设 'bert' 文件夹的绝对路径
        bert_folder_abs_path = r"D:\dasanshang\NLP\1\Topic_and_user_profile_analysis_system\code\back_end\bert_class\bert"

        # 检查路径是否存在
        if not os.path.exists(bert_folder_abs_path):
            raise FileNotFoundError(f"指定的路径 {bert_folder_abs_path} 不存在。")

        # 加载Bert配置
        try:
            self.bert_config = BertConfig.from_pretrained(bert_folder_abs_path)
        except OSError as e:
            print(f"加载配置文件时出错: {e}")
            raise

        # 定义模型
        self.model = BertClassifier(self.bert_config, len(self.labels))

        # 假设 'best_bert_model' 文件夹的绝对路径
        best_model_folder_abs_path = r"D:\dasanshang\NLP\1\Topic_and_user_profile_analysis_system\code\back_end\bert_class\best_bert_model"

        # 检查路径是否存在
        if not os.path.exists(best_model_folder_abs_path):
            raise FileNotFoundError(f"指定的路径 {best_model_folder_abs_path} 不存在。")

        best_model_file_path = os.path.join(best_model_folder_abs_path, 'best_model.pkl')
        # 加载训练好的模型
        try:
            self.model.load_state_dict(torch.load(best_model_file_path, map_location=torch.device('cpu')))
        except FileNotFoundError as e:
            print(f"加载模型文件时出错: {e}")
            raise
        self.model.eval()

        # 加载分词器
        try:
            self.tokenizer = BertTokenizer.from_pretrained(bert_folder_abs_path)
        except OSError as e:
            print(f"加载分词器时出错: {e}")
            raise

    def classify_text(self, text):
        """
        对输入的文本进行分类，返回分类结果
        :param text: 待分类的文本
        :return: 分类结果的标签
        """
        # 对文本进行分词处理
        token = self.tokenizer(text, add_special_tokens=True, padding='max_length', truncation=True, max_length=512)
        input_ids = token['input_ids']
        attention_mask = token['attention_mask']
        token_type_ids = token['token_type_ids']

        # 将分词结果转换为张量
        input_ids = torch.tensor([input_ids], dtype=torch.long)
        attention_mask = torch.tensor([attention_mask], dtype=torch.long)
        token_type_ids = torch.tensor([token_type_ids], dtype=torch.long)

        # 进行预测
        with torch.no_grad():
            predicted = self.model(
                input_ids,
                attention_mask,
                token_type_ids,
            )
        # 获取预测结果的索引
        pred_label = torch.argmax(predicted, dim=1).item()

        # 根据索引获取对应的标签
        return self.labels[pred_label]