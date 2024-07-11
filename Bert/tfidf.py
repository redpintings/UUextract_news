import os
import json
import requests
from loguru import logger
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from lxml import etree
import torch
from example import url_set
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def fetch_webpage(url):
    try:
        logger.info(f'Fetching {url}')
        response = requests.get(url, timeout=3)
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return ''


def extract_title(html):
    tree = etree.HTML(html)
    if tree:
        title = tree.xpath('//title/text()')
        return title[0] if title else ''
    else:
        return ""


def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(['script', 'style']):
        script.extract()
    text = soup.get_text(separator=' ')
    return ' '.join(text.split())


def load_or_create_data():
    if os.path.exists('news_data.json') and os.path.exists('cleaned_data.json'):
        with open('news_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open('cleaned_data.json', 'r', encoding='utf-8') as f:
            cleaned_data = json.load(f)
    else:
        urls = url_set
        data = []
        for url in urls:
            html = fetch_webpage(url)
            title = extract_title(html)
            data.append({'url': url, 'html': html, 'title': title.strip()})

        with open('news_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        cleaned_data = [{'url': item['url'], 'text': clean_html(item['html']), 'title': item['title']} for item in data]

        with open('cleaned_data.json', 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

    return data, cleaned_data


data, cleaned_data = load_or_create_data()

corpus = [item['text'] for item in cleaned_data]
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(corpus)

y = [item['title'] for item in cleaned_data]

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')


class TextDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]).to('cpu') for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx]).to('cpu')
        return item

    def __len__(self):
        return len(self.labels)


inputs = tokenizer(corpus, padding=True, truncation=True, return_tensors="pt")
labels = [0 if t == 'negative' else 1 for t in y]

model.to(device)

train_dataset = TextDataset(inputs, labels)

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=train_dataset
)

trainer.train()
