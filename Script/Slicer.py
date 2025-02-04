import sys
import os
from sklearn.preprocessing import StandardScaler
import nibabel as nib
import numpy as np
from PIL import Image

os.environ['CUDA_VISIBLE_DEVICES'] = "0"
# First, read the arguments:
myDirectory = str(sys.argv[1])
Destination = str(sys.argv[2])
# Now create the output folder inside Destination:
output_folder = os.path.join(Destination, 'Test', 'All')
os.makedirs(output_folder, exist_ok=True)

y = 0
directory = os.fsencode(myDirectory)
names = []
for file in os.listdir(directory):
    myFile = file.decode('utf-8')
    # Skip hidden files and non-NIfTI files
    if myFile.startswith('.') or (not myFile.endswith('.nii') and not myFile.endswith('.nii.gz')):
        continue
    myNifti = nib.load(myDirectory + myFile)
    print(y, 'Train')
    y += 1
    data = myNifti.get_fdata()
    data = data * (185.0 / np.percentile(data, 97))
    scaler = StandardScaler()
    names.append(myFile)
    for sl in range(0, 80):
        x = sl
        clipped = data[:, :, (45 + x)]
        image_data = Image.fromarray(clipped).convert('RGB')
        image_data.save(os.path.join(output_folder, myFile[:-7] + '-' + str(x) + '.jpg'))