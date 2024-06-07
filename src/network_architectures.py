from tensorflow.python import keras as backend


def inception_keras(c):
    from tensorflow.keras.applications import InceptionV3
    from tensorflow.keras.layers import Input, GlobalMaxPooling2D, Dense
    from tensorflow.keras.models import Model

    c.network_name = 'inception'
    model_input = Input(shape=(c.IMG_SIZE, c.IMG_SIZE, c.N_CHANNELS))

    base_model = InceptionV3(input_shape=(c.IMG_SIZE, c.IMG_SIZE, c.N_CHANNELS),
                             input_tensor=model_input,
                             include_top=False)

    x = base_model.output
    x = GlobalMaxPooling2D()(x)
    out_activation = Dense(1, activation='sigmoid', name='sigmoid_activation_2class')(x)

    model = Model(inputs=base_model.input, outputs=out_activation)
    return model
