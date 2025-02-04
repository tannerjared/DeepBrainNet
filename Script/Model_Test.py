import os
import sys
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
import pandas as pd
from keras.models import load_model

os.environ['CUDA_VISIBLE_DEVICES'] = "0"
model = load_model(sys.argv[3])
print(model.summary())

# Use the parent directory of the provided folder and tell flow_from_directory which class folder to use:
test_dir = str(sys.argv[1])  # e.g., "../tmp/Test/All/"
parent_dir = os.path.dirname(test_dir.rstrip('/'))  # should give "../tmp/Test"
print(parent_dir)

batch_size = 80
datagen_test = ImageDataGenerator(
    rescale=1./255,
    horizontal_flip=False,
    vertical_flip=False,
    featurewise_center=False,
    featurewise_std_normalization=False
)

# Specify the class subfolder "All" explicitly:
test_generator = datagen_test.flow_from_directory(
    directory=parent_dir,
    classes=['All'],
    batch_size=batch_size,
    seed=42,
    shuffle=False,
    class_mode=None
)

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
