# -*- coding: utf-8 -*-
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score

# READ THE DOCUMENT
df = pd.read_excel(r"C:\xampp\htdocs\TA\Program\dataset\new_dataset_program.xlsx")
reviews = df["ulasan"].astype(str).tolist()
labels = df["label"].tolist()

# FE / TF IDF
tfidf = TfidfVectorizer(max_features=2000, ngram_range=(1,2))

# tfidf = TfidfVectorizer()
# Hanya ambil 5000 kata paling penting (berdasarkan frekuensi & relevansi). Untuk mengurangi ukuran vektor dan mempercepat training
# Mengambil unigram (kata tunggal) dan bigram (2 kata berurutan). Contoh: "tidak bagus" akan jadi dua fitur:tidak, tidak bagus. Untuk mempertimbangkan konteks antar kata
X = tfidf.fit_transform(reviews)
y = labels

# SPLIT DATA (TRAINING 80% DAN TESTING 20% )
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.4, random_state=42, stratify=y
)

# TRAIN MODEL SVM
model = SVC(kernel='linear')   # misalnya pakai kernel linear
model.fit(X_train, y_train) # melatih model menggunakan data training
y_pred = model.predict(X_test) # memprediksi label dari data testing

# AKURASI
acc = accuracy_score(y_test, y_pred)
print("Accuracy:", acc)
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# HYPERPARAMETER TUNING
# param_grid = {
#     'C': [0.1, 1, 10],
#     'kernel': ['linear', 'rbf', 'poly'],
#     'gamma': ['scale', 'auto']
# }

# param_grid = {
#     'C': [0.01, 0.1, 1, 10, 50, 100],
#     'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
#     'gamma': ['scale', 'auto', 0.01, 0.001],
#     'degree': [2, 3, 4, 5],
#     'class_weight': [None, 'balanced'],
#     'shrinking': [True, False]
# }

param_grid = {
    'C': [0.01, 0.1, 1, 10],
    'kernel': ['linear', 'rbf', 'poly'],
    'gamma': ['scale', 'auto', 0.01, 0.001],
    'degree': [2, 3, 4, 5],
    'class_weight': [None, 'balanced'],
    'shrinking': [True, False]
}
# mencoba semua kombinasi parameter dari param_grid dan memilih yang terbaik berdasarkan akurasi rata-rata dari 5-fold cross-validation
grid = GridSearchCV(
    estimator=SVC(class_weight='balanced'),
    param_grid=param_grid,
    cv=5, # ini artinya pakai 5-fold cross validation
    scoring='accuracy', # kriteria penilaian yang digunakan
    verbose=0, # 2 = menampilkan progres tuning di terminal
    n_jobs=-1 # gunakan semua core CPU agar proses nya cepat
)


grid.fit(X_train, y_train)

print("Selama pelatihan, model dengan parameter terbaik", grid.best_params_)
print("punya performa rata-rata sebesar", grid.best_score_) #rata-rata akurasi dari model terbaik selama cross-validation.

best_model = grid.best_estimator_
y_pred = best_model.predict(X_test)

print("\n=== Test Set Evaluation ===")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

#save to pickle
save_pickle_path = "C:\\xampp\\htdocs\\TA\\Program\\model\\model.pkl"

with open(save_pickle_path, 'wb') as f:
    pickle.dump(best_model, f)

print(f"✅ Model saved to: {save_pickle_path}")

# ==== SAVE TF-IDF VECTOR ====
save_tfidf_path = r"C:\xampp\htdocs\TA\Program\model\tfidf.pkl"
with open(save_tfidf_path, 'wb') as f:
    pickle.dump(tfidf, f)


print(f"✅TF-IDF Vectorizer saved to: {save_tfidf_path}")