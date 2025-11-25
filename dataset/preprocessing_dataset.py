import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import re
from indoNLP.preprocessing import replace_slang


#1. baca documentnya
df = pd.read_excel(r"C:\xampp\htdocs\TA\Program\dataset\old_dataset_program.xlsx")

# ambil ko;om ulasan_clean
df = df[["ulasan", "label"]].copy()
reviews = df["ulasan"].astype(str)

#2. --- Case Folding --- 
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
    #Hapus huruf berulang lebih dari 1 kali (misal niattt -> niat)
    # return re.sub(r'(.)\1{2,}', r'\1', word)
    return re.sub(r'(.)\1+', r'\1', word)

def normalize_text(text):
    text = replace_slang(text)
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

#8. --- ganti kolom ulasan dengan hasil dari review_cleaned ---
df["ulasan"] = review_cleaned.apply(lambda x: " ".join(x))

#9. --- Export hasil preprocessing ke Excel ---
output_path = r"C:\xampp\htdocs\TA\Program\dataset\new_dataset_program.xlsx"
df.to_excel(output_path, index=False)

print("✅ Preprocessing selesai. File disimpan di:", output_path)