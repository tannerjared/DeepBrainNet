from keras.preprocessing.image import ImageDataGenerator

import numpy as np
import pandas as pd

# import h5py
from keras.models import load_model
import sys
import os

os.environ['CUDA_VISIBLE_DEVICES'] = "0"

model = load_model(sys.argv[3])
print(model.summary())

test_dir = sys.argv[1]

batch_size = 80

datagen_test = ImageDataGenerator(rescale=1./255, horizontal_flip=False, vertical_flip=False,
                                  featurewise_center=False, featurewise_std_normalization=False)

print(test_dir)

test_generator = datagen_test.flow_from_directory(
    directory=str(test_dir),
    batch_size=batch_size,
    seed=42,
    shuffle=False,
    class_mode=None)

labels_test = []
sitelist = []
IDlist = []
sex_test = []
slice_test = []
deplist = []
test_generator.reset()
i = 0

for x in test_generator.filenames:
    i = i+1
    sl = x.split('-')[1].split('.')[0]
    x = x.split('_T1')[0]

    IDlist.append(x)

test_generator.reset()
predicty = model.predict(test_generator, verbose=1, steps=test_generator.n/batch_size)

prediction_data = pd.DataFrame()
prediction_data['ID'] = IDlist

prediction_data['Prediction'] = predicty

IDset = set(prediction_data['ID'].values)
IDset = list(IDset)


final_prediction = []
final_labels = []
final_site = []

for x in IDset:
    check_predictions = prediction_data[prediction_data['ID'] == x]['Prediction']
    predicty = check_predictions.reset_index(drop=True)
    final_prediction.append(np.median(predicty))

predicty1 = final_prediction

out_data = pd.DataFrame()
out_data['ID'] = IDset
out_data['Pred_Age'] = predicty1
out_data.to_csv(sys.argv[2], index=False)
