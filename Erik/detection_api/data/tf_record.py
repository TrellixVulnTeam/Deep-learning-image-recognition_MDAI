# Run this script using the terminal command  python tf_record.py --output_path training.record

import tensorflow as tf
import pandas as pd
import numpy as np
from tensorflow.models.research.object_detection.utils import dataset_util
from PIL import Image

flags = tf.app.flags
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
FLAGS = flags.FLAGS

def create_tf_entry(label_and_data_info):

    height = 900 # Image height
    width = 1360 # Image width
    filename = label_and_data_info[0] # Filename of the image. Empty if image is not from file
    img = np.array(Image.open('GTSDB/' + filename.decode()))
    encoded_image_data = img.tostring() # Encoded image bytes
    image_format = b'png' # b'jpeg' or b'png'

    xmins = label_and_data_info[1] # List of normalized left x coordinates in bounding box (1 per box)
    xmaxs = label_and_data_info[2] # List of normalized right x coordinates in bounding box
             # (1 per box)
    ymins = label_and_data_info[3] # List of normalized top y coordinates in bounding box (1 per box)
    ymaxs = label_and_data_info[4] # List of normalized bottom y coordinates in bounding box
             # (1 per box)
    classes_text = label_and_data_info[5] # List of string class name of bounding box (1 per box)
    classes = label_and_data_info[6] # List of integer class id of bounding box (1 per box)
    # TODO END
    tf_label_and_data = tf.train.Example(features=tf.train.Features(feature={
      'image/height': dataset_util.int64_feature(height),
      'image/width': dataset_util.int64_feature(width),
      'image/filename': dataset_util.bytes_feature(filename),
      'image/source_id': dataset_util.bytes_feature(filename),
      'image/encoded': dataset_util.bytes_feature(encoded_image_data),
      'image/format': dataset_util.bytes_feature(image_format),
      'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
      'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
      'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
      'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
      'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
      'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_label_and_data


writer = tf.python_io.TFRecordWriter(FLAGS.output_path)

file_loc = 'GTSDB/gt.txt'
raw_data = pd.read_csv(file_loc, sep=';', header=None, names = ['filename', 'xmin', 'ymin', 'xmax', 'ymax', 'ClassID'])

i = 0
prev_file = ''
all_data_and_label_info = []
for filename in raw_data['filename']:
    if filename != prev_file:
        if i != 0:
            all_data_and_label_info.append(temp_data)

        temp_data = ([str.encode(filename), [raw_data['xmin'][i] ],[raw_data['xmax'][i]],[raw_data['ymin'][i]],[raw_data['ymax'][i]],
                   [str.encode(str(raw_data['ClassID'][i]))], [raw_data['ClassID'][i] + 1]])
    else:
        temp_data[1].append(raw_data['xmin'][i])
        temp_data[2].append(raw_data['xmax'][i])
        temp_data[3].append(raw_data['ymin'][i])
        temp_data[4].append(raw_data['ymax'][i])
        temp_data[5].append(str.encode(str(raw_data['ClassID'][i])))
        temp_data[6].append(raw_data['ClassID'][i] + 1)

    prev_file = filename
    i = i + 1

all_data_and_label_info.append(temp_data)

for data_and_label_info in all_data_and_label_info:
    tf_entry = create_tf_entry(data_and_label_info)
    writer.write(tf_entry.SerializeToString())

writer.close()
