import keras
import numpy as np
from functools import partial

from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.imagenet_utils import decode_predictions

import keras.applications.xception as xception
import keras.applications.vgg16 as vgg16
import keras.applications.resnet50 as resnet50
import keras.applications.inception_v3 as inception_v3
import keras.applications.inception_resnet_v2 as inception_resnet_v2
import keras.applications.mobilenet as mobilenet
import keras.applications.densenet as densenet
import keras.applications.nasnet as nasnet
import keras.applications.mobilenet_v2 as mobilenet_v2

model_fn_mapping = {"xception": xception.Xception, "vgg16":vgg16.VGG16, "resnet50":resnet50.ResNet50, "inception_v3": inception_v3.InceptionV3,
                "inception_resnet_v2": inception_resnet_v2.InceptionResNetV2, "mobilenet": mobilenet.MobileNet, "mobilenet_v2": mobilenet_v2.MobileNetV2,
                "densenet121": densenet.DenseNet121, "densenet169": densenet.DenseNet169, "densenet201": densenet.DenseNet201,
                "nasnetlarge": nasnet.NASNetLarge, "nasnetmobile": nasnet.NASNetMobile}

base_class_mapping = preprocess_fn_mapping = {"xception": xception, "vgg16":vgg16, "resnet50":resnet50, "inception_v3": inception_v3,
                "inception_resnet_v2": inception_resnet_v2, "mobilenet": mobilenet, "mobilenet_v2": mobilenet_v2,
                "densenet121": densenet, "densenet169": densenet, "densenet201": densenet,
                "nasnetlarge": nasnet, "nasnetmobile": nasnet}

preprocess_fn_mapping = {"xception": xception.preprocess_input, "vgg16":vgg16.preprocess_input, "resnet50":resnet50.preprocess_input, "inception_v3": inception_v3.preprocess_input,
                "inception_resnet_v2": inception_resnet_v2.preprocess_input, "mobilenet": mobilenet.preprocess_input, "mobilenet_v2": mobilenet_v2.preprocess_input,
                "densenet121": densenet.preprocess_input, "densenet169": densenet.preprocess_input, "densenet201": densenet.preprocess_input,
                "nasnetlarge": nasnet.preprocess_input, "nasnetmobile": nasnet.preprocess_input}

def get_result(model, filename, preprocess_fn):
    # Process Image
    original = load_img(filename, target_size=(224, 224))
    numpy_image = img_to_array(original)
    image_batch = np.expand_dims(numpy_image, axis=0)
    processed_image = preprocess_fn(image_batch.copy())

    predictions = model.predict(processed_image)
    return predictions

def decode_and_print_result(predictions, model_name = "Not Specific"):
    label = decode_predictions(predictions)
    print(model_name+" Result: ", label[0] )

def get_model(model_name, model_fn_mapping):
    model_fn = model_fn_mapping[model_name]
    model_fn = partial(model_fn, include_top=True, weights='imagenet', classes=1000) # General configs
    if (model_name == "mobilenet"):
        model_fn = partial(model_fn, alpha=1.0, depth_multiplier=1, dropout=1e-3)
    if (model_name == "mobilenet_v2"):
        model_fn = partial(model_fn, alpha=1.0, depth_multiplier=1)

    model = model_fn()
    return model

def iterate_model_running_using_one_image(filename, enable_set):
    for idx, model_name in enumerate(enable_set):
        print("Using Model: "+model_name)
        preprocess_fn = preprocess_fn_mapping[model_name]
        model = get_model(model_name = model_name ,model_fn_mapping = model_fn_mapping)
        print(model_name+" loaded")

        predictions = get_result(model = model, filename = filename, preprocess_fn = preprocess_fn)
        decode_and_print_result(predictions = predictions, model_name = model_name)

filename = "/Users/zyxu/Downloads/huskyphotos_20/husky_interleaved_repaired.bmp"
# enable_set = set(["xception", "mobilenet", "mobilenet_v2", "nasnetmobile"])
enable_set = set(["mobilenet"])
iterate_model_running_using_one_image(filename, enable_set)



