# bif_care
Simple IPython based user interface to [CARE](http://csbdeep.bioimagecomputing.com/) a toolbox for Content-aware Image Restoration.

## How to use:
CARE needs pairs of registered images - low (input) and high (output) quality. It trains a convolutional neural network how to transform low quality images - which might even be of less physical resolution - into high quality images. After training, newly recorded low quality images or movies can be predicted. 2D, 3D and multi-channel images are supported. For each channel a separate network is trained.

#### Input selection and patch extraction
1. Copy and rename the IPython notebook template file: `bif_care_templ.ipynb` to `my_care_project.ipynb`
2. Open your renamed `my_care_project.ipynb` file in Jypyter or IPyhton notebook.
3. In order to train CARE, the path to the image pairs needs to be specified. Then, choose images for low and high quality respectively using a wild-card (e.g. `low*.tif` and `high*.tif`). The images will be converted and image patches are extracted. This step is required for efficient GPU execution. Choose patch sizes for your input dimensions `(Z)YX` and set how many patches should be extracted per image pair. After image patches have been extracted, they are saved to the output directory. 

#### Training the network
The training of a neural network is done iteratively in `epochs`. In each epoch, the network weights' are updated by optimizing a loss function on `steps_per_epoch` batches of image patches. The size of the batches is given by `batch_size`. To make use of all your image data, select `steps_per_epoch = #patches / batch_size`. Per default, 10% of patches are used for validation and not used in training.

4. Select training parameters and execute training code block.

#### Using the trained network for prediction
You can predict new images in the IPython notebook directly using the prediction widgets, or use the Fiji:

0. Add (or enable) [CSBDeep](http://sites.imagej.net/CSBDeep/) to your Fiji update sites
1. Open image you want to predict in Fiji
2. In Fiji choose `Plugins->CSBDeep->Run your network`
3. Select network file `<bif_care-out-folder>/models/CH_X_model/TF_SavedModel.zip` as 'Import model (.zip)' of your trained channel
4. Set additional parameters such as number of tiles (higher number, in case your entire image cannot be loaded on your GPU memory) and press OK

#### Vanilla screencast for input selection and training
![bif_care User interface](vid/bif_care_demo_01.mp4)

## Installation
### NVidia Cuda and cuDNN
1. Install [NVidia CUDA toolkit](https://developer.nvidia.com/cuda-toolkit-archive)
2. Install [NVidia cuDNN](https://developer.nvidia.com/cudnn)

#### Known working versions
1. NVidia CUDA toolkit  9.0 + cuDNN 7.3.0
2. NVidia CUDA toolkit 10.0 + cuDNN 7.5.1

### Python dependencies
We strongly recommend using the [Anaconda Python distribution](https://www.anaconda.com/distribution/) with Python == 3.6. Furthermore, we recommend to create a new conda virtual environment with `conda create -n py36_bif_care python=3.6 anaconda`.

You can install all mayor dependencies, including tensforflow (1.12.1) and csbdepp (0.3.0) by:

```
cd <this-path>
pip install -r requirements.txt -e .
```

If your Python distribution comes without PyQt5, install it by:

```
conda install pyqt
```

### IPython widgets
The user interface is written using IPython/Jupyter widgets, which requires the installation of [node.js]([nodejs](https://nodejs.org/en/))

Finally, you have to install jypyter widgets and enable them, by:

```
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter nbextension enable --py widgetsnbextension

```
More information on [Jupyter/IPython widgets](https://ipywidgets.readthedocs.io/en/stable/user_install.html).


### Troubleshooting and known issues
* tensorflow 1.13.x requires NVidia tookit 10.0 (or higher; not tested) for the latest csbdeep 0.3.0 release. 
* 




