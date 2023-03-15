# DeepBrainNet
Convolutional Neural Network trained for age prediction using a large (n=11,729) set of MRI scans from a highly diversified cohort spanning different studies, scanners, ages, ethnicities and geographic locations around the world.

Files are in HDF5(.h5) format for easy use in Keras. Model files initalize the architecture and the pre-trained weights.

Other files can be found here: https://upenn.box.com/v/DeepBrainNet




Use test.sh in the Script folder to perform brain age prediction on T1 brain scans.

- Run test.sh -h to see required parameters

----Data Requirements----

- T1 scans must be in nifti format
- Scans shoud be skull-stripped and linearly registered.

JT note: The authors are not clear if the linear registration is 6, 9, or 12 degrees of freedom. They also do not detail what the target is. My assumption is MNI152 space as the target and 12 degrees of freedom because they used FLIRT but that's an unknown.

My updated scripts clean out unnecessary modules and fix formatting issues. There also were a couple updates to move away from legacy commands that are no longer supported. The scripts will need to be modified if your GPU is not CUDA_VISIBLE_DEVICES = 0. If you have multiple GPUs, you might need to modify those lines in the scripts.

My pipeline for processing invovled using antscorticalthickness.sh (https://github.com/tannerjared/MRI_Guide/blob/master/preprocessing_antscorticalthickness.md) to skull strip and do other initial processing. Then I took the skull stripped brain (ExtractedBrain0N4.nii.gz), copied it into a working directory with the participant ID prepended, and used FLIRT to do a 12 degrees of freedom registration to the MNI152 1mm brain. I also completed a 6 DOF trial, which produced similar results, but opted for 12 to do a better job of normalizing brain sizes. I also tried the BrainNormalizedToTemplate.nii.gz images from the ANTs preprocessing (these are non-linearly transformed) but those values were significantly different from the affine methods; because the DeepBrainNet model was implemented on affine-registered brains, the non-linear values were deemed to be inaccurate.

There are other methods of skull-stripping that could be used: BET, FreeSurfer, etc. I've had good experience with FreeSurfer and marginal with BET. I opted for the ANTs pipeline because is faster than FreeSurfer (although I generally also process with FreeSurfer).

With preprocessed data, I ran this on a cluser computer like this:
`srun --mem=16gb --partition=gpu --gpus=1 --time=01:00:00 --pty bash -i`

Within that interactive session I ran the following:
`module load python tensorflow cuda`

`cd DeepBrainNet/Script`

`./test.sh -d ../../input_forDeepBrainNet/ -o ../../DeepBrainNet_out/ -m ../Models/DBN_model.h5`

It takes only a couple minutes to run on 205 brains.
