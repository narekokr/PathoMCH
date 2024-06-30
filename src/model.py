import argparse
import importlib
from shutil import copyfile
from predict import *
from network_architectures import *
import os
from tfrecords_reader import *
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# tf.logging.set_verbosity(tf.logging.ERROR)

import tensorflow as tf

'''
Control training and inference from here.
Requires tensorflow 1.14 and python 3 (specifically developed using TensorFlow 1.14.0 and python 3.6)
'''

# Train on multiple GPUs (if not available will default to 1 replica)
# strategy = tf.distribute.MirroredStrategy(devices=["/gpu:0"])
strategy = tf.distribute.MirroredStrategy()
print('Number of devices: {}'.format(strategy.num_replicas_in_sync))

# Command-line argument parsing for configuration class and resample round
parser = argparse.ArgumentParser(description='Process configuration class and resample round.')
parser.add_argument('--config_class', type=str, default='Conf_COAD_TRAITS_mir_1269a_extreme',
                    help='Name of the configuration class to use.')
parser.add_argument('--resample_round', type=int, default=0,
                    help='Resample round to use (default: 0).')
parser.add_argument('--use_local_data', type=bool, default=True,
                    help='Whether to use local data (default: True).')
args = parser.parse_args()

# Dynamically import the specified configuration class
config_module = importlib.import_module('conf')
config_class = getattr(config_module, args.config_class)
c = config_class()

# General settings
training = False  # set to False for predictions
resample_round = args.resample_round  # which of the resampling rounds to use
use_local_data = args.use_local_data  # whether to use local data
print("Resample round {}".format(resample_round))

# Training settings
c.APPLY_AUGMENTATIONS = True  # flip augmentations that apply only to train set
c.NETWORK_NAME = 'inception'
EPOCHS = 1000  # setting an upper limit. The model will likely stop before, when converging on validation set.
lr = 0.001
BATCH_SIZE_PER_REPLICA = c.BATCH_SIZE
BATCH_SIZE = BATCH_SIZE_PER_REPLICA * strategy.num_replicas_in_sync

# Prepare model folders and code snapshot used for model
model_folder = '../out/{}_zoom_{}_round_{}_{}'.format(c.NAME, c.ZOOM_LEVEL, resample_round, get_time_stamp())
os.mkdir(model_folder)
c.set_logger(model_folder)
copyfile('../src/model.py', model_folder+'/model.py')
copyfile('../src/network_architectures.py', model_folder+'/network_architectures.py')
copyfile('../src/conf.py', model_folder+'/conf.py')
model_folder_loss = model_folder + '/loss'
model_folder_acc = model_folder + '/acc'
model_folder_auc = model_folder + '/auc'
for f in [model_folder_loss, model_folder_acc, model_folder_auc]:
    if not os.path.exists(f):
        os.mkdir(f)

print(c.GCS_PATTERN)
# sys.exit()
if training:
    # get filenames and number of tiles to determine number of steps
    if use_local_data:
        c.GCS_PATTERN = c.GCS_PATTERN_LOCAL
    training_filenames = tf.io.gfile.glob(c.GCS_PATTERN.format('train/round_{}_train'.format(resample_round)))
    validation_filenames = tf.io.gfile.glob(c.GCS_PATTERN.format('val/round_{}_val'.format(resample_round)))
    print("Training filenames\n", training_filenames)
    print("Val filenames:\n", validation_filenames)
    random.shuffle(training_filenames)
    random.shuffle(validation_filenames)
    # File names contain number of samples in each. Using this to obtain total number of images (tiles).
    n_train = sum([int(f.split('-')[-1].split('.')[0]) for f in training_filenames])
    n_val = sum([int(f.split('-')[-1].split('.')[0]) for f in validation_filenames])
    STEPS_PER_EPOCH_VAL = n_val // BATCH_SIZE


def get_lr_metric(optimizer):
    def lr(y_true, y_pred):
        return optimizer.lr
    return lr


with strategy.scope():
    loss = 'binary_crossentropy'
    main_metric = tf.keras.metrics.binary_accuracy
    model = inception_keras(c)
    acc_val_metric = 'val_binary_accuracy'

    # Compile the model
    optimizer = tf.keras.optimizers.Adam(learning_rate=lr)
    lr_metric = get_lr_metric(optimizer)
    model.compile(optimizer=optimizer, loss=loss, metrics=[main_metric, lr_metric, tf.keras.metrics.AUC()])

    # Train the model
    global_step = 0
    if training:
        if c.LOAD_WEIGHTS_PATH:
            model.load_weights(tf.train.latest_checkpoint(c.LOAD_WEIGHTS_PATH))
            log.print_and_log("Loaded model from path: {}".format(c.LOAD_WEIGHTS_PATH))

        TFRec = tfrecords(c)

        ckpt_prefix = "ckpt"
        checkpoint_prefix_loss = os.path.join(model_folder_loss, ckpt_prefix + "_{epoch}")
        checkpoint_prefix_acc = os.path.join(model_folder_acc, ckpt_prefix + "_{epoch}")
        checkpoint_prefix_auc = os.path.join(model_folder_auc, ckpt_prefix + "_{epoch}")
        STEPS_PER_EPOCH_TRAIN = n_train // (BATCH_SIZE * 16)  # division by batch size due to BATCH_SIZE number of tiles being processed per step. Division by 16 to evaluate every 1/16th epoch to avoid overfitting due to tile similarities between batches (many tiles per slide make it seem like there's a lot of the same per slide)
        print("steps TRAIN", STEPS_PER_EPOCH_TRAIN)
        print("steps val", STEPS_PER_EPOCH_VAL)
        train_tfrecords = TFRec.get_training_dataset(training_filenames, BATCH_SIZE)
        val_tfrecords = TFRec.get_inference_dataset(validation_filenames, BATCH_SIZE)
        res = model.fit(train_tfrecords,
                        steps_per_epoch=STEPS_PER_EPOCH_TRAIN,
                        epochs=EPOCHS,
                        validation_data=val_tfrecords,
                        validation_freq=1,
                        validation_steps=STEPS_PER_EPOCH_VAL,
                        callbacks=[
                            tf.keras.callbacks.ReduceLROnPlateau(patience=10, verbose=1),
                            tf.keras.callbacks.EarlyStopping(patience=30, verbose=1),
                            tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_prefix_loss,
                                                               save_weights_only=True,
                                                               save_best_only=True),
                            tf.keras.callbacks.ModelCheckpoint(monitor='val_auc',
                                                               filepath=checkpoint_prefix_auc,
                                                               save_weights_only=True,
                                                               save_best_only=True,
                                                               mode='max')
                        ])

    else:
        if not c.LOCAL:
            assert c.LOAD_WEIGHTS_PATH, "LOAD_WEIGHTS_PATH is None!"
        conf_architecture = c
        conf_per_sample_tfrecords = c
        log.print_and_log("Inference using weights under: {}".format(c.LOAD_WEIGHTS_PATH))
        # evaluate against ground truth
        predict_per_sample(c, conf_architecture, c.LOAD_WEIGHTS_PATH, model,
                           out_folder_suffix='_round_{}'.format(resample_round))
