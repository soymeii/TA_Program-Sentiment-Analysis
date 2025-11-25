import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import re
from indoNLP.preprocessing import replace_slang
import pickle



# 1. Baca data JSON dari stdin
df = pd.read_excel(r"C:\xampp\htdocs\TA\Program\result\crawling_from_tokopedia.xlsx")
reviews  = df["review"].astype(str)
#2. --- Case Folding --- mengambil kolom review dan lowerCase kan (CaseFolding)
review_lowercase = reviews.str.lower()

#3. --- Stopword Removal ---
stop_factory = StopWordRemoverFactory()
stop_remover = stop_factory.create_stop_word_remover()
review_stopword_removed = review_lowercase.apply(lambda x: stop_remover.remove(x))

#4. --- Stemming ---
stem_factory = StemmerFactory()
stemmer = stem_factory.create_stemmer()
review_stemmed = review_stopword_removed.apply(lambda x: stemmer.stem(x))

#5. --- Normalization ---
def remove_repeated_char(word):
    return re.sub(r'(.)\1+', r'\1', word)

def normalize_text(text):
    """Gunakan IndoNLP untuk mengganti slang + hilangkan huruf berulang"""
    # Normalisasi slang
    text = replace_slang(text)
    # Hilangkan huruf berulang
    text = " ".join(remove_repeated_char(word) for word in text.split())
    return text

review_normalized = review_stemmed.apply(normalize_text)

#6. --- Tokenizing ---
review_tokenized = review_normalized.apply(nltk.word_tokenize)

#7. --- Cleansing ---
def cleansing(tokens):
    cleaned = []
    for word in tokens:
        # hapus tanda baca, angka, dan hanya simpan huruf
        word = re.sub(r'[^a-zA-Z]+', '', word)
        if word != "":
            cleaned.append(word)
    return cleaned

review_cleaned = review_tokenized.apply(cleansing)
df["review"] = review_cleaned.apply(lambda x: " ".join(x))

#8. --- Load model dan tfidf pkl ---
with open(r"C:\xampp\htdocs\TA\Program\model\tfidf.pkl", 'rb') as f:
    tfidf = pickle.load(f)

with open(r"C:\xampp\htdocs\TA\Program\model\model.pkl", 'rb') as f:
    model = pickle.load(f)

#9. --- Transformasi data menggunakan tfidf ---
X_new = tfidf.transform(df["review"])

#10. --- Prediksi menggunakan model yang sudah dilatih ---
label_map = {0: "negative", 1: "positive"} #ngubah angka jadi string label
df["label"] = model.predict(X_new)
df["label"] = df["label"].map(label_map)

#11. --- Export hasil preprocessing ke Excel ---
output_path = r"C:\xampp\htdocs\TA\Program\result\preprocessed_from_tokopedia.xlsx"
df.to_excel(output_path, index=False)
