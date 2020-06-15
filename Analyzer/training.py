import pandas as pd
import numpy as np


data = pd.read_excel("data_reduced.xlsx")
y = data['malware']

# Drop filenames, list of imports and signature
data = data.drop(columns=['file', 'malware']) 

# Mark None signature as 2
data['signature_trusted'] = data['signature_trusted'].fillna(2).astype(np.int64) 


categories = ["type", "struct_version", 'signature_trusted',  'os', 'flags',
              'filetype' , 'Subsystem', 'Magic', 'Machine', 'FileAlignment', ]

data_enc = pd.get_dummies(data, columns = categories)


def save_enc_columns(data="data_reduced.xlsx"):
    data = pd.read_excel(data)
    data = data.drop(columns=['file', 'malware']) 
    data['signature_trusted'] = data['signature_trusted'].fillna(2).astype(np.int64) 
    categories = ["type", "struct_version", 'signature_trusted',  'os', 'flags',
                  'filetype' , 'Subsystem', 'Magic', 'Machine', 'FileAlignment', ]
    
    data_enc = pd.get_dummies(data, columns = categories)
    
    with open('enc_columns.txt', 'w') as f:
        f.write('[')
        for c in data_enc.columns:
            f.write("'"+c+"',")
        f.write(']')


def get_saved_columns(file='enc_columns.txt'):
    with open(file, 'r') as f:   
        return eval(f.readline())
    
    
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

X = data_enc.iloc[:].values

sc = MinMaxScaler()
X = sc.fit_transform(X.astype(np.float64))

#Save scaler
from sklearn.externals import joblib
joblib.dump(sc, "scaler.save")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.1, random_state = 0)


import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras import optimizers


classifier = Sequential()
classifier.add(Dense(units = 135, kernel_initializer='glorot_normal', input_dim = 134, activation='relu'))
#classifier.add(Dropout(rate = 0.15))
classifier.add(Dense(units = 35, kernel_initializer='glorot_normal', activation='relu'))
#classifier.add(Dropout(rate = 0.25))
classifier.add(Dense(units = 1, kernel_initializer='glorot_normal', activation='sigmoid'))


classifier.compile(loss='binary_crossentropy', optimizer='adam',  metrics=['accuracy'])
classifier.fit(X_train, y_train, batch_size = 16, epochs = 30)


#Save NN
model_json = classifier.to_json()
with open("model2.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
classifier.save_weights("model2.h5")
print("Saved model to disk")


#Evaluation
# --Confussion matrix--
# TruePositive(TP) Type1Error(FP)
# Type2Error(FN)   TrueNegative(TN)
from sklearn.metrics import confusion_matrix, accuracy_score

y_test_pred = classifier.predict(X_test)
cmp = np.concatenate((y_test_pred, pd.DataFrame(y_test)), axis = 1)

y_test_pred = (y_test_pred > 0.5)
cm = confusion_matrix(y_test, y_test_pred)
print("Test accuracy: ",accuracy_score(y_test, y_test_pred))


# Predict NEW
import static
pe = static.PortableExecutable("F:/Games/ArcheRage/bin32/locales/ko.dll")
res = pe.run()
assert res != None

    
res = pd.DataFrame([res])
# Delete unusing features
res.pop('imports')
res.pop('peid_signatures')
# Process None values in signature feature
res['signature_trusted'] = res['signature_trusted'].fillna(2).astype(np.int64) 

# One-Hot encode
new_data = pd.get_dummies(res, columns = categories)
new_data = new_data.reindex(columns = data_enc.columns, fill_value=0)
scaler = joblib.load("scaler.save")
new_data = scaler.transform(new_data)

#Load NN
from keras.models import model_from_json
json_file = open('model2.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model2.h5")
print("Loaded model from disk")


print("Prediction: ", loaded_model.predict(new_data))