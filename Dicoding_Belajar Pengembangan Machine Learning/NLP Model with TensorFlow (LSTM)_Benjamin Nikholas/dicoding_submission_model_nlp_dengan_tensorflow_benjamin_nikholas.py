# -*- coding: utf-8 -*-
"""Dicoding Submission_Model NLP dengan TensorFlow_Benjamin Nikholas

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hUeRW6YmlJK_QC0vpWb1DmDBzZsmiPat

# Project Pertama: Membuat model NLP dengan TensorFlow
---
---
* Nama: Benjamin Nikholas
* Email: benjisturi@gmail.com
* Nomor Telp : [6287892677303](wa.me/6287892677303)

Kriteria Parameter:
1. Dataset yang akan dipakai bebas, namun minimal memiliki 1000 sampel.
2. Harus menggunakan LSTM dalam arsitektur model.
3. Harus menggunakan model sequential.
4. Validation set sebesar 20% dari total dataset.
5. Harus menggunakan Embedding.
6. Harus menggunakan fungsi tokenizer.
7. Akurasi dari model minimal 75% pada train set dan validation set.

---

Kriteria target nilai sempurna **(bintang 5)**:
1. dataset memiliki 3 kelas atau lebih
2. dataset memiliki minimal 2000 sampel data
3. akurasi pada training set dan validation set
4. Mengimplementasikan Callback
5. Membuat plot loss dan akurasi pada saat training dari validation set
"""

import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from sklearn.model_selection import train_test_split
from sklearn.utils import check_random_state
import tensorflow as tf
from tensorflow.keras import Sequential, layers, regularizers, optimizers
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

warnings.filterwarnings("ignore")
plt.figure(figsize=(8, 6))

# Check data info

df_movies = pd.read_csv('/content/imdb_movies.csv')
df_movies.info()

# Checking and Dropping columns with NaN

for cols in df_movies.columns:

  # Count value on each column with no NaN value
  data_length = len(df_movies[cols].dropna())

  # Drop Columns with incomplete data/value (NaN)
  if data_length != len(df_movies):
    print(cols)
    df_movies.drop(cols, axis = 1, inplace = True)

df_movies.info()

# Initialize random number generator to ensure reproducibility

def SetSeed(seed:int):
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    random.seed(seed)
    tf.random.set_seed(seed)
    check_random_state(seed)

for i in df_movies.columns:
  print(f'unique values on {i} : {len(df_movies[i].unique())}')
  if len(df_movies[i].unique()) < 10:
    print(df_movies[i].unique())

df_movie_status = df_movies[['names','status']]
df_movie_status.info()

# Check new dataframe

df_status = pd.get_dummies(df_movies.status)
df_movies = pd.concat([df_movie_status, df_status], axis = 1)
df_movies.drop(columns = 'status', inplace = True)
df_movies

# Membagi data menjadi train (80%) dan validation (20%)
X = df_movies['names'].values
y = df_movies.iloc[:, 1:].values

X_train, X_val, y_train, y_val = train_test_split(X, y,
                                                  train_size = 0.8,
                                                  random_state = 10)

"""### Tokenizer"""

tokenizer = Tokenizer(num_words = 5000, oov_token = 'X')

# Fit tokenizer on text data
tokenizer.fit_on_texts(X_train)
tokenizer.fit_on_texts(X_val)

# Implement Tokenization on train dan validation data
X_train_tokenized = tokenizer.texts_to_sequences(X_train)
X_val_tokenized = tokenizer.texts_to_sequences(X_val)

"""### Padding Sequence"""

max_length = 20
X_train_padded = pad_sequences(X_train_tokenized,
                               maxlen = max_length)

X_val_padded = pad_sequences(X_val_tokenized,
                             maxlen = max_length)

"""### LSTM Model"""

# LSTM Model

SetSeed(2024)

model = Sequential([

    # Add Embedding layer
    layers.Embedding(input_dim = 5000,
                     output_dim = 16),

    # Add LSTM Layer
    layers.LSTM(units = 64),
    layers.Dropout(0.2),

    # Add Fully Connected Layer
    layers.Dense(units = 128,
                 activation = 'relu',
                 kernel_regularizer = regularizers.l2(0.01)),
    layers.Dense(units = 128,
                 activation = 'relu'),
    layers.Dropout(0.5),
    layers.Dense(units = 3,
                 activation = 'softmax'),
])

# Compiling model

SetSeed(2024)

# AMSGrad Optimizer
AMSGrad = optimizers.Adam(amsgrad = True, name = 'Adam')

model.compile(loss = 'categorical_crossentropy',
              metrics = 'accuracy',
              optimizer = AMSGrad)

# Callbacks implementation

EarlyStop = tf.keras.callbacks.EarlyStopping(
    monitor = 'val_loss',
    min_delta = 0.001,
    verbose = 2,
    patience = 5,
    restore_best_weights = True,
    mode = 'min'
)

# Model Fitting

SetSeed(2024)

model_fit = model.fit(X_train_padded, y_train,
                      epochs = 50,
                      validation_data = (X_val_padded, y_val),
                      verbose = 2,
                      callbacks = EarlyStop)

# Check model fitting history data

model_history = pd.DataFrame(model_fit.history)
model_history.info()

# Accuracy Plot on Training and Validation

plt.plot(model_history.accuracy, label = 'train accuracy')
plt.plot(model_history.val_accuracy, label = 'validation accuracy')
plt.title('Training and Validation Accuracy\non LSTM Model')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

# Loss Plot on Training and Validation data

plt.plot(model_history.loss, label = 'train loss')
plt.plot(model_history.val_loss, label = 'validation loss')
plt.title('Loss Plot on LSTM Model')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

# Check accuracy on training and validation data

min_accuracy = 0.75 # 75%

print(f'''Training data accuracy pass 75% : {model_history.accuracy.max() > min_accuracy}
Validation data accuracy pass 75% : {model_history.val_accuracy.max() > min_accuracy}''')

