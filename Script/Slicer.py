from sklearn.preprocessing import StandardScaler

import nibabel as nib
# from nilearn import plotting
import numpy as np
from PIL import Image
import sys
import os

os.environ['CUDA_VISIBLE_DEVICES'] = "0"

myDirectory = str(sys.argv[1])
Destination = str(sys.argv[2])

y = 0
directory = os.fsencode(myDirectory)
names = []

for file in os.listdir(directory):
    myFile = os.fsencode(file)
    myFile = myFile.decode('utf-8')
    myNifti = nib.load((myDirectory + myFile))
    print(y, 'Train')
    y = 1+y
    data = myNifti.get_fdata()
    data = data*(185.0/np.percentile(data, 97))

    scaler = StandardScaler()
    names.append(myFile)
    for sl in range(0, 80):
        x = sl

        clipped = data[:, :, (45+x)]

        image_data = Image.fromarray(clipped).convert('RGB')
        image_data.save((Destination + 'Test/' + myFile[:-7] + '-'+str(x)+'.jpg'))
