This Docker container will automatically preprocess T1-weighted images as preparation for DeepBrainNet calculation.

Needed template files can be downloaded

```
wget https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/3133832/Oasis.zip
unzip Oasis.zip && rm -rf Oasis.zip
```

The contents of the templates directory should be

```
MNI152_T1_1mm_brain_LPS_filled.nii.gz
Priors2/
T_template0.nii.gz
T_template0_BrainCerebellum.nii.gz
T_template0_BrainCerebellumExtractionMask.nii.gz
T_template0_BrainCerebellumProbabilityMask.nii.gz
```

Priors2 should contain
```
priors1.nii.gz
priors2.nii.gz
priors3.nii.gz
priors4.nii.gz
priors5.nii.gz
priors6.nii.gz
```

All files have been uploaded to GitHub other than T_template0.nii.gz. Download that (and all T_template and Priors files from the previously posted link).

The MNI152_T1_1mm_brain_LPS_filled.nii.gz is also hosted here: https://upenn.box.com/v/DeepBrainNet

Build the Docker container locally like this from within the DBNpreproc directory.
```
docker build -t dbn-preproc .
```

Run the container like this
```
docker run --rm \
-v ./DBNpreproc_in:/data/input \
-v ./DBNpreproc_out:/data/output \
dbn-preproc /data/input /data/output
```

The script inside the container requires T1 files to be named like: `sub-01_T1w.nii.gz`

The container will preprocess all sub-*_T1w.nii.gz files in your input directory and save the outputs to your specified output directory.
