import keras
import numpy as np
from functools import partial
from image_to_quality import emulator_file_list_at_all_loss_rate
import pickle
import matplotlib.pyplot as plt
import scipy
import numpy

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

base_class_mapping = {"xception": xception, "vgg16":vgg16, "resnet50":resnet50, "inception_v3": inception_v3,
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
    print(model_name+" result: ", label[0])

def decode_top_1_result(predictions, model_name = "Not Specific"):
    label = decode_predictions(predictions)
    return label[0][0]

def decode_top_5_result(predictions, model_name = "Not Specific"):
    label = decode_predictions(predictions)
    return label[0]

def get_model(model_name, model_fn_mapping):
    model_fn = model_fn_mapping[model_name]
    model_fn = partial(model_fn, include_top=True, weights='imagenet', classes=1000) # General configs
    if (model_name == "mobilenet"):
        model_fn = partial(model_fn, alpha=1.0, depth_multiplier=1, dropout=1e-3)
    if (model_name == "mobilenet_v2"):
        model_fn = partial(model_fn, alpha=1.0, depth_multiplier=1)

    model = model_fn()
    return model

def get_model_with_name_only(model_name):
    model_fn_mapping = {"xception": xception.Xception, "vgg16":vgg16.VGG16, "resnet50":resnet50.ResNet50, "inception_v3": inception_v3.InceptionV3,
                "inception_resnet_v2": inception_resnet_v2.InceptionResNetV2, "mobilenet": mobilenet.MobileNet, "mobilenet_v2": mobilenet_v2.MobileNetV2,
                "densenet121": densenet.DenseNet121, "densenet169": densenet.DenseNet169, "densenet201": densenet.DenseNet201,
                "nasnetlarge": nasnet.NASNetLarge, "nasnetmobile": nasnet.NASNetMobile}

    return get_model(model_name, model_fn_mapping)

def iterate_model_running_using_one_image(filename, enable_set):
    for idx, model_name in enumerate(enable_set):
        print("Using Model: "+model_name)
        preprocess_fn = preprocess_fn_mapping[model_name]
        model = get_model(model_name = model_name ,model_fn_mapping = model_fn_mapping)
        print(model_name+" loaded")

        predictions = get_result(model = model, filename = filename, preprocess_fn = preprocess_fn)
        decode_and_print_result(predictions = predictions, model_name = model_name)


def using_model_to_get_predictions(filename, model, model_name):
    # print("Using Model: "+model_name)
    preprocess_fn = preprocess_fn_mapping[model_name]
    # print(model_name+" loaded")
    predictions = get_result(model = model, filename = filename, preprocess_fn = preprocess_fn)
    return predictions

def get_top_1_attribute_and_name_and_accuracy(filename, model, model_name):
    preprocess_fn = preprocess_fn_mapping[model_name]
    predictions = get_result(model = model, filename = filename, preprocess_fn = preprocess_fn)
    attr, name, acc = decode_top_1_result(predictions)
    return attr, name, acc

def get_top_n_correctness_using_file_and_attribute(filename, attribute, model, model_name, top_n = 1):
    preprocess_fn = preprocess_fn_mapping[model_name]
    predictions = get_result(model = model, filename = filename, preprocess_fn = preprocess_fn)
    attr_list = decode_top_5_result(predictions)
    for attr, name, acc in attr_list[0:top_n]:
        if attr == attribute:
            return 1

    return 0

def get_correctness_using_file_and_attribute(filename, attribute, model, model_name):
    attr, name, acc = get_top_1_attribute_and_name_and_accuracy(filename, model, model_name)
    if (attr == attribute):
        return 1
    else:
        return 0

# get 1,2,3,4 results, for filename_string of loss rate
def get_ml_result_for_one_file_at_loss_rate(filename, loss_rate, attribute, model, model_name):
    # convert loss rate to string
    loss_rate_str = str(int(loss_rate*100))
    name = filename + "_" + loss_rate_str
    dist_filename_list = [name + "_" + n + ".bmp" for n in["1", "2", "3", "4"]]
    result_list = []
    for filename in dist_filename_list:
        result_list.append(get_top_n_correctness_using_file_and_attribute(filename, attribute, model, model_name, top_n=5))
        # result_list.append(get_correctness_using_file_and_attribute(filename, attribute, model, model_name))
    return result_list

def get_all_ml_result(path, name_list, loss_rate_list, attribute_dict, model, model_name):
    dataset_result = {}
    for loss_rate in loss_rate_list:
        loss_rate_result = {}
        for name in name_list:
            for i in range(10):
                filename = name+str(i)
                filepath = path + filename
                loss_rate_result[filename] = get_ml_result_for_one_file_at_loss_rate(filepath, loss_rate, attribute_dict[filename][0], model, model_name)
        # loss_rate_str = str(int(loss_rate*100))
        dataset_result[loss_rate] = loss_rate_result
        print(dataset_result)

    pickle.dump(dataset_result, open('data_ml.pkl', 'wb'))
    return dataset_result


def parse_ml_result(dataset_result, metric):
    loss_rate_list = []
    loss_list = []
    loss_fix_list = []
    interleave_list = []
    interleave_fix_list = []

    for loss_rate, lr_result in dataset_result.items():
        value0_list = []
        value1_list = []
        value2_list = []
        value3_list = []
        # get average quality for all files under one loss rate
        for name, result in lr_result.items():
            value0_list.append(result[0]) # loss
            value1_list.append(result[1])
            value2_list.append(result[2]) # interleave
            value3_list.append(result[3])

        loss_list.append(sum(value0_list) / len(value0_list))
        loss_fix_list.append(sum(value1_list) / len(value1_list))
        interleave_list.append(sum(value2_list) / len(value2_list))
        interleave_fix_list.append(sum(value3_list) / len(value3_list))
        loss_rate_list.append(loss_rate)

    plt.plot(loss_rate_list, loss_list, label="Loss without recovery")
    plt.plot(loss_rate_list, loss_fix_list, label="Loss with recovery")
    plt.plot(loss_rate_list, interleave_list, label="Interleaving without recovery")
    plt.plot(loss_rate_list, interleave_fix_list, label="Interleaving with recovery")

    plt.legend(loc='upper right')
    plt.xlabel('Loss Rate')
    plt.ylabel('Top 5 Accuracy for model '+metric)
    plt.savefig(metric+'_top_1_acc_vs_loss_rate.png')
    plt.gcf().clear()

if __name__ == "__main__":
    name_list = ["airplane", "automobile", "bird", "cat", "deer",
                 "dog", "frog", "horse", "ship", "truck"]
    # name_list = ["airplane"]
    loss_rate_list = [0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.2, 0.3, 0.4]

    attribute_dict = pickle.load(open("gt_attr.pkl", 'rb'))

    path = "./testset/"
    print("Emulating all files")

    file_list = []
    for name in name_list:
        for i in range(10):
            file_list.append(name+str(i))
    emulator_file_list_at_all_loss_rate(path, file_list, loss_rate_list, redo=False)

    print("Getting results")
    model_name = "mobilenet"
    model = get_model(model_name = model_name ,model_fn_mapping = model_fn_mapping)
    dataset_result = get_all_ml_result(path, name_list, loss_rate_list, attribute_dict, model, model_name)

    print("Generating plots")
    parse_ml_result(dataset_result, metric=model_name)
