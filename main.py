from tensorflow.keras.layers import Dense, Input
from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.layers import LSTM, Dropout, GRU, Bidirectional
from tensorflow.keras.layers import GlobalMaxPool1D
from tensorflow.keras.layers import Conv1D, SpatialDropout1D
from tensorflow.keras.layers import Embedding, Dropout
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.optimizers import Adam, RMSprop, SGD
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.models import model_from_json
from tensorflow.keras.models import save_model, load_model
from tensorflow.keras.models import Sequential
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from wordcloud import WordCloud
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import SnowballStemmer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk
import re
import string
import random
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import emoji
import pickle
from PIL import Image


import warnings
warnings.filterwarnings('ignore')


nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')


# set global seed
seed = 42
np.random.seed(seed)
tf.random.set_seed(seed)

path = '/content/drive/My Drive/Deep Learning - Projetos/Embeddings /Musical_instruments_reviews.csv'
data = pd.read_csv(path)
data.head()

# lower case columns
data.columns = data.columns.str.lower()

# drop columns
cols_drop = ['reviewerid', 'asin', 'reviewername',
             'helpful', 'unixreviewtime', 'reviewtime']
data.drop(columns=cols_drop, axis=1, inplace=True)

# Summary
data['overall'] = data['overall'].replace({1: 2, 4: 5})


# sentiments
data['overall'] = data['overall'].replace({2: 'Negative',
                                           3: 'Neutral',
                                           5: 'Positive'
                                           })

data['overall'].value_counts()

data['reviewtext'] = data['reviewtext'].astype(str)
data['overall'] = data['overall'].astype(str)

data.dropna(axis=0, inplace=True)

data['reviewtext'] = data['reviewtext'] + ' ' + data['summary']
data.drop('summary', axis=1, inplace=True)

X = data['reviewtext']
y = data['overall']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=42)

encoder = LabelEncoder()

y_train = encoder.fit_transform(y_train)
y_test = encoder.transform(y_test)

print('Classes: ', encoder.inverse_transform([0, 1, 2]))

# Cleaning text


def cleaning_text(text):
    """
    Cleaning text in Twetts 
    Removing unwanted characters and emojis

                                            """

    # Removing characters and emojis
    removing_list = "@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+"
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U0001F1F2-\U0001F1F4"  # Macau flag
                               u"\U0001F1E6-\U0001F1FF"  # flags
                               u"\U0001F600-\U0001F64F"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U0001F1F2"
                               u"\U0001F1F4"
                               u"\U0001F620"
                               u"\u200d"
                               u"\u2640-\u2642"
                               "]+", flags=re.UNICODE)

    text = emoji_pattern.sub(r'', str(text))
    text = re.sub(removing_list, " ", text)
    text = re.sub(r'\W+', ' ', text)
    text = re.sub("'", '', text)
    text = text.lower().strip()

    # Stemming and Stopwords
    stemmer = SnowballStemmer('english')
    stop_words = set(stopwords.words('english'))

    tokens = []
    for token in text.split():
        if token not in stop_words:
            tokens.append(stemmer.stem(token))
        else:
            pass

    return " ".join(tokens)


def feature_engineering(data):
    """ Pipeline of Feature engineering for 
         text classification problem 

        1 - cleaning text 
        2 - spliting data
        3 - label encoder 
        4 - tokenization 
        5 - pad_sequences 
                                          """

    # cleaning text
    data['reviewtext'] = data['reviewtext'].apply(lambda x: cleaning_text(x))

    # spliting data
    X = data['reviewtext']
    y = data['overall']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42)

    # LabelEncoder
    encoder = LabelEncoder()
    y_train = encoder.fit_transform(y_train.to_list())
    y_test = encoder.fit_transform(y_test.to_list())

    y_train = y_train.reshape(-1, 1)
    y_test = y_test.reshape(-1, 1)

    print('Classes: ', encoder.inverse_transform([0, 1, 2]))
    print('\n')

    # Tokenization
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(X_train)

    # Vocabulary Size
    word_index = tokenizer.word_index
    num_words = len(word_index) + 1

    # Tokens
    sequence_train = tokenizer.texts_to_sequences(X_train)
    sequence_test = tokenizer.texts_to_sequences(X_test)

    # max sequence
    MAX_SEQUENCE_LENGTH = 55

    # pad_sequences
    X_train = pad_sequences(sequences=sequence_train,
                            maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')
    X_test = pad_sequences(sequences=sequence_test,
                           maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')

    return (X_train, X_test, y_train, y_test, num_words, word_index, tokenizer)


X_train, X_test, y_train, y_test, num_words, word_index, tokenizer = feature_engineering(
    data)

print(X_train.shape, y_train.shape)
print(X_test.shape, y_test.shape)

# compile parameters

optimizer = RMSprop(learning_rate=0.001)
loss = SparseCategoricalCrossentropy()
metrics = ['accuracy']

# Embedding parameters

EMBEDDING_GLOVE = 300
EMBEDDING_DIM = 300
MAX_SEQUENCE_LENGTH = 55
NUM_WORDS = 18485

# Build LSTM


def lstm_architecture(pre_trained=True, num_words=NUM_WORDS, embedding_dim=EMBEDDING_GLOVE, max_sequence_length=MAX_SEQUENCE_LENGTH):
    """The LSTM model architecture
    with option for use Glove embedding """

    if pre_trained:

        # Glove Embedding
        GLOVE_EMB = '/content/glove.6B.300d.txt'

        embeddings_index = {}
        f = open(GLOVE_EMB)
        for line in f:
            values = line.split()
            word = value = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
        f.close()

        print('Found {} word vectors.'.format(len(embeddings_index)))

        # Embedding matrix
        embedding_matrix = np.zeros((num_words, embedding_dim))

        for word, i in word_index.items():
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector

        # LSTM with Glove
        model = Sequential()
        model.add(Input(shape=max_sequence_length))
        model.add(Embedding(input_dim=num_words,
                            output_dim=embedding_dim,
                            weights=[embedding_matrix],
                            input_length=max_sequence_length,
                            trainable=False))
        model.add(LSTM(units=128, recurrent_dropout=0.20))
        model.add(Dense(units=512, activation='relu'))
        model.add(Dropout(0.20))
        model.add(Dense(units=64, activation='relu'))
        model.add(Dense(units=3, activation='softmax'))

        return model

    else:

        # LSTM without Glove
        model = Sequential()
        model.add(Input(shape=max_sequence_length))
        model.add(Embedding(input_dim=num_words,
                            output_dim=embedding_dim,
                            input_length=max_sequence_length))
        model.add(LSTM(units=128, recurrent_dropout=0.20))
        model.add(Dense(units=512, activation='relu'))
        model.add(Dropout(0.20))
        model.add(Dense(units=64, activation='relu'))
        model.add(Dense(units=3, activation='softmax'))

        return model


model = lstm_architecture(pre_trained=False, embedding_dim=EMBEDDING_DIM)

model.compile(optimizer=optimizer,
              loss=loss,
              metrics=metrics)

model.summary()

# callbacks

checkpoint = ModelCheckpoint(filepath='model.h5',
                             monitos='val_loss',
                             verbose=1,
                             save_only_weights=True)


early_stopping = EarlyStopping(monitor='val_loss',
                               min_delta=0.00001,
                               patience=10)


reduce_learning_rate = ReduceLROnPlateau(monitor='val_loss',
                                         factor=0.2,
                                         patience=5,
                                         min_delta=0.0001)


callbacks = [checkpoint, early_stopping, reduce_learning_rate]

model.fit(X_train, y_train,
          batch_size=128,
          epochs=10,
          validation_data=(X_test, y_test),
          callbacks=[callbacks])

loss, accuracy = model.evaluate(X_test, y_test)

# save weights and json model
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)

model.save_weights('model.h5')

# save tokenizer
with open('tokenizer.pkl', 'wb') as handle:
    pickle.dump(tokenizer, handle)

# Loading model json
new_model = model_from_json(model_json)

new_model.load_weights('model.h5')


new_model.compile(optimizer=optimizer,
                  loss=loss,
                  metrics=metrics)

class_names = ['Negative', 'Neutral', 'Positive']


def tweet_predict(text):
    # time
    time_pred = time.time()

    # tweet
    text = [text]

    # tokenization
    text = tokenizer.texts_to_sequences(text)

    # pad sequences
    text = pad_sequences(text, maxlen=MAX_SEQUENCE_LENGTH)

    # predict
    sentiment = model.predict(text)
    sentiment = np.argmax(sentiment, axis=1)

    if sentiment.any() == 2:
        print('Positive')
    elif sentiment.any() == 1:
        print('Neutral')
    else:
        print('Negative')


text = 'I loved this guittar'

tweet_predict(text)
