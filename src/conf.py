from utils import Logger
import os

'''
Configurations for preprocessing and training. Conf class contains the main settings. Below Conf your will find
general BRCA and LUAD configuration classes derived from Conf. Examples of specific trait configurations (e.g. for ESR1)
can be found below. In order to complete preprocessing fast, it is recommended to set NUM_CPU=60 if available.  
Note that most paths are catered for Google Cloud buckets, but can be modified to your needs.
'''

class Conf:
    def __init__(self, is_preprocessing=False):

        self.IS_PREPROCESSING = is_preprocessing
        self.DIAGNOSTIC_SLIDES = True
        self.LOAD_WEIGHTS_PATH = None
        self.ONLY_DX1 = False
        self.ZOOM_LEVEL = 20
        self.NUM_CPU = 60
        self.SAVE_IMAGES = True
        self.RESTORE_FROM_BEST_CKPT = False
        self.APPLY_AUGMENTATIONS = True  # True if for training we want data augmentations. With coco was beneficial to first train without until plateau. Then load ckpt and retrain with.
        self.IS_TRAIN = True
        self.N_ROUNDS = 5
        self.TRAIN_PCT = 0.8
        self.VAL_PCT = 0.1
        self.NETWORK_NAME = ''
        self.USE_SAVED_LABELS_IF_EXIST = False  # false will create labels dictionary from scratch
        self.BATCH_SIZE = 18
        self.IMG_SIZE = 512
        self.VAL_STEPS_MAX = 100000
        self.NUM_CLASS = 1
        self.TASK_TYPE = '2-class'
        self.CLINICAL_LABELS = ['lo', 'hi']
        self.LABELS = self.CLINICAL_LABELS

        self.IMG_TYPE = 'jpeg'
        self.N_CHANNELS = 3

        self.N_CHAR_PATIENT_ID = 12
        self.N_CHAR_SLIDE_ID = 23
        self.N_CHAR_SAMPLE_ID = 15

        # paths
        self.OUT_DIR = '../out/'
        self.CKPT_PATH_FORMAT = "../out/model_{}"
        self.IM_PATH_TO_LABEL_DICT_FORMAT = 'im_path_to_label_dict_{}_{}'
        self.ALL_SAMPLES_TFRECORDS_FOLDER = '../res/all_samples_dummy_labels/'
        self.generate_tfrecords_folders()

        if not os.path.exists(self.OUT_DIR):
            os.mkdir(self.OUT_DIR)

        self.SVS_SLIDES_PATH = '../data/slides/diagnostic/'
        self.IMG_PATH = '../data/images/zoom_{}_{}/'.format(self.ZOOM_LEVEL, self.IMG_SIZE)
        self.SLIDE_TYPE = 'DX'

        if not os.path.exists(self.IMG_PATH) and self.IS_PREPROCESSING:
            os.makedirs(self.IMG_PATH)

        # misc
        self.PANCAN_NAME_SUFFIX = 'COAD_UNHEALTHY_SAMPLES'

    def set_logger(self, folder_path):
        self.LOG = Logger(folder_path)

    def set_ckpt_path(self):
        self.CKPT_PATH = self.CKPT_PATH_FORMAT.format('_'.join(self.CLINICAL_LABELS))

    def generate_tfrecords_folders(self):
        for sub_data in ['train', 'val', 'all_samples_dummy_labels']:
            sub_data_path = '../res/{}/'.format(sub_data)
            if not os.path.exists(sub_data_path):
                os.mkdir(sub_data_path)

    def set_local(self):
        # self.LOCAL = True
        self.LOCAL = False
        self.GCS_PATTERN = '../res/{}*.tfrec'
        self.GCS_PATTERN_PER_SAMPLE = '../res/all_samples_dummy_labels/*tfrecords'
        print("!!! Using LOCAL settings !!! This means you are not training the full model optimally. To fully"
              "train, comment out: 'c.set_local()' in model.py")


# presets
class Conf_COAD(Conf):
    def __init__(self, is_preprocessing=False):
        super().__init__(is_preprocessing)
        self.TCGA_COHORT_NAME = 'coad'
        self.CLINICAL_FILEPATH = '../res/merged_clinical_mirna_data.csv'
        self.GCS_PATTERN_PER_SAMPLE = \
            '../res/patho_al/tfrecords/coad/per_sample/tf_records_zoom_20_labels_dummy_neg_dummy_pos/*tfrecords'
        self.PANCAN_NAME_SUFFIX = 'COAD_UNHEALTHY_SAMPLES'

class Conf_COAD_TRAITS_PIGR_extreme(Conf_COAD):
    def __init__(self, is_preprocessing=False):
        super().__init__(is_preprocessing)
        self.NAME = 'PIGR_lo_vs_hi'
        self.CLINICAL_LABEL_COLS = ["PIGR|5284"]
        self.LOAD_WEIGHTS_PATH = None  # change when transitioning to inference, e.g.: '../out/<model_name>/auc/'
        self.GCS_PATTERN = '../res/patho_al/tfrecords/coad/all_sharded/PIGR_lo_vs_hi/{}*.tfrec'

class Conf_COAD_TRAITS_miR_143_4p_extreme(Conf_COAD):
    def __init__(self, is_preprocessing=False):
        super().__init__(is_preprocessing)
        self.NAME = 'hsa-miR-143-3p_lo_vs_hi'
        self.CLINICAL_LABEL_COLS = ['hsa-miR-143-3p']
        # self.LOAD_WEIGHTS_PATH = '../out/hsa-miR-17-5p_lo_vs_hi_zoom_20_round_0_2020_05_22_20_59_43/auc/'
        self.LOAD_WEIGHTS_PATH = None
        self.GCS_PATTERN = '../res/main_al/tfrecords/coad/all_sharded/{}/'.format(self.NAME)+'{}*.tfrec'
