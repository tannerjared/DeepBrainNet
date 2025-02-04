# DeepBrainNet
Convolutional Neural Network trained for age prediction using a large (n=11,729) set of MRI scans from a highly diversified cohort spanning different studies, scanners, ages, ethnicities and geographic locations around the world.

Files are in HDF5(.h5) format for easy use in Keras. Model files initalize the architecture and the pre-trained weights.

Other files can be found here: https://upenn.box.com/v/DeepBrainNet

Use test.sh in the Script folder to perform brain age prediction on T1 brain scans.

- Run test.sh -h to see required parameters

----Data Requirements----

- T1 scans must be in nifti format
- Scans shoud be skull-stripped (bias correction also necessary) and linearly registered to the MNI152 brain in the box.com link above (the one built into FSL should work too).
- The DBN_model.h5 from the box.com link. This is about a 174 MB file.

**JT note**: The authors are not clear if the linear registration is 6, 9, or 12 degrees of freedom. My assumption is 12.

My updated scripts clean out unnecessary modules and fix formatting issues. There also were a couple updates to move away from legacy commands that are no longer supported. The scripts will need to be modified if your GPU is not CUDA_VISIBLE_DEVICES = 0. If you have multiple GPUs, you might need to modify those lines in the scripts. You also might need to set tensorflow==2.15.

My pipeline for processing involved using antscorticalthickness.sh (https://github.com/tannerjared/MRI_Guide/blob/master/preprocessing_antscorticalthickness.md) to skull strip and do other initial processing. Then I took the skull stripped brain (ExtractedBrain0N4.nii.gz), copied it into a working directory with the participant ID prepended, and used FLIRT to do a 12 degrees of freedom registration to the MNI152 1mm brain. I also completed a 6 DOF trial, which produced similar results, but opted for 12 to do a better job of normalizing brain sizes. I also tried the BrainNormalizedToTemplate.nii.gz images from the ANTs preprocessing (these are non-linearly transformed) but those values were significantly different from the affine methods; because the DeepBrainNet model was implemented on affine-registered brains, the non-linear values were deemed to be inaccurate.

**Note the naming convention for the brains for this processing to work smoothly**. I'm sure there's a fix to the code that would allow more flexible naming.

SubjectID_T1_BrainAligned.nii.gz

Replace ID with your participant ID, or at least an ID you can match to your participant.

For example: Subject2008_T1_BrainAligned.nii.gz

If, for some reason, you end up with individual brain age estimates for each slice of the brain for each participant (what happens if that naming convention isn't followed), you could also take the median of the brain ages from each slice for a participant and that will give you the final predicted brain age.

There are other methods of skull-stripping that might be used: BET, FreeSurfer, etc. I've had good experience with FreeSurfer and marginal with BET. I opted for the ANTs pipeline because is faster than FreeSurfer for a single brain using multiple cores (although I generally also process with FreeSurfer) and is the pipeline used by the developers of DeepBrainNet. Using any other preprocessing method will require comparisons with ANTS.

With preprocessed data, I ran this on a cluser computer like this:
`srun --mem=32gb --nodes=1 --partition=gpu --gpus=a100:1 --time=00:10:00 --pty bash -i`

Within that interactive session I ran the following:
`module load python tensorflow cuda`

`cd DeepBrainNet/Script`

`./test.sh -d ../../input_forDeepBrainNet/ -o ../../DeepBrainNet_out/ -m ../Models/DBN_model.h5`

It takes only a couple minutes to run on 205 brains. It's also quick on a local computer.

## Docker

An ARM64 container of DeepBrainNet is avaiable here

`docker pull jjtanner/deepbrainnet:latest`

With the data set up as described above, run the command like this. Change the paths of the input and output directories to match your setup.

```
docker run --rm \                                   
  -v ./DeepBrainNet_in/:/data \
  -v ./DeepBrainNet_out/:/output \
  deepbrainnet -d /data/ -o /output/ -m /app/Models/DBN_model.h5
```
