This Docker container will automatically preprocess T1-weighted images as preparation for DeepBrainNet calculation. At its core, it is a container with both ANTs and FSL. As such, it has the ability to be used for many processing pipelines. You are welcome to update the 
`ENTRYPOINT ["/opt/app/script/automate_preprocessing.sh"]` part in the Dockerfile to be more generic.

You can also run the Docker container like this to get an interactive bash terminal. You'd have access to ANTS and FSL command line tools.

`docker run -it --entrypoint /bin/bash jjtanner/dbn-preproc:latest`

**This container does not (yet) work on Apple Silicon. The DeepBrainNet container does but this is so far AMD/X86 only.**

All brain template files have been uploaded to GitHub other than T_template0.nii.gz. You can download that and all T_template and Priors files as follows

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

The MNI152_T1_1mm_brain_LPS_filled.nii.gz is also hosted here: https://upenn.box.com/v/DeepBrainNet

Build the Docker container locally like this from within the DBNpreproc directory.
```
docker build -t dbn-preproc .
```
You can download a prebuilt AMD64/X_64 container that includes all template brain images like this

`docker pull jjtanner/dbn-preproc:latest`

Run the container like this if you built locally
```
docker run --rm \
-v ./DBNpreproc_in:/data/input \
-v ./DBNpreproc_out:/data/output \
dbn-preproc /data/input /data/output
```
Run the container like this to pull from the Docker Hub
```
docker run --rm \
-v ./DBNpreproc_in:/data/input \
-v ./DBNpreproc_out:/data/output \
jjtanner/dbn-preproc:latest /data/input /data/output
```

The script inside the container requires T1 files to be named like:
```
sub-01_T1w.nii.gz
sub-02_T1w.nii.gz
...
```

The container will preprocess all sub-*_T1w.nii.gz files in your input directory and save the outputs to your specified output directory. It can take anywhere from about **30 minutes (using 12+ cores) to 6 hours (using 1 core) per brain**.

Note that the container limits ITK threads/cores to 4. You are welcome to change the default in the Dockerfile and in the automate_preprocessing.sh script depending on your system resources. More cores will result in a faster processing but require more RAM and cores (of course).

It's likely faster to run this in parallel than serial. That would require multiple input and output directories and running multiple instances of the Docker container at the same time.
