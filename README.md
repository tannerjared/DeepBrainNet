# DeepBrainNet
Convolutional Neural Network trained for age prediction using a large (n=11,729) set of MRI scans from a highly diversified cohort spanning different studies, scanners, ages, ethnicities and geographic locations around the world.

Files are in HDF5(.h5) format for easy use in Keras. Model files initalize the architecture and the pre-trained weights.

Other files can be found here: https://upenn.box.com/v/DeepBrainNet




Use test.sh in the Script folder to perform brain age prediction on T1 brain scans.

- Run test.sh -h to see required parameters

----Data Requirements----

- T1 scans must be in nifti format
- Scans shoud be skull-striped and linearly registered.

JT note: The authors are not clear if the linear registration is 6, 9, or 12 degrees of freedom. They also do not detail what the target is. My assumption is MNI152 space because they used FLIRT but that's an unknown.
My updated scripts clean out unnecessary modules and fix formatting issues. The scripts will need to be modified if your GPU is not CUDA_VISIBLE_DEVICES = 0. If you have multiple GPUs, you might need to modify those lines in the scripts.
