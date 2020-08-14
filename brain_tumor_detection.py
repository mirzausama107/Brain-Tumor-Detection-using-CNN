#importing all necessary libraries
try:
    from app import *
    import tensorflow as tf
    from tensorflow.keras.layers import Conv2D, Input, ZeroPadding2D, BatchNormalization, Activation, MaxPooling2D, \
        Flatten, Dense
    from tensorflow.keras.models import Model, load_model
    from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score
    from sklearn.utils import shuffle
    import cv2
    import imutils
    import numpy as np
    import matplotlib.pyplot as plt
    import time
    from os import listdir

    print("fond")
except:

    print("no fond")


def hello(a):
    # cropping
    def crop_brain_contour(image, plot=False):
        # import imutils
        # import cv2
        # from matplotlib import pyplot as plt

        # Convert the image to grayscale, and blur it slightly
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Threshold the image, then perform a series of erosions +
        # dilations to remove any small regions of noise
        thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours in thresholded image, then grab the largest one
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)

        # Find the extreme points
        extLeft = tuple(c[c[:, :, 0].argmin()][0])
        extRight = tuple(c[c[:, :, 0].argmax()][0])
        extTop = tuple(c[c[:, :, 1].argmin()][0])
        extBot = tuple(c[c[:, :, 1].argmax()][0])

        # crop new image out of the original image using the four extreme points (left, right, top, bottom)
        new_image = image[extTop[1]:extBot[1], extLeft[0]:extRight[0]]

        if plot:
            plt.figure()

            plt.subplot(1, 2, 1)
            plt.imshow(image)

            plt.tick_params(axis='both', which='both',
                            top=False, bottom=False, left=False, right=False,
                            labelbottom=False, labeltop=False, labelleft=False, labelright=False)

            plt.title('Original Image')

            plt.subplot(1, 2, 2)
            plt.imshow(new_image)

            plt.tick_params(axis='both', which='both',
                            top=False, bottom=False, left=False, right=False,
                            labelbottom=False, labeltop=False, labelleft=False, labelright=False)

            plt.title('Cropped Image')

            plt.show()

        return new_image

    # original_image = cv.imread()
    # cropped_image = crop_brain_contour(original_image,True)

    def load_data(dir_list, image_size):
        # load all images in a directory
        X = []
        y = []
        image_width, image_height = image_size

        for directory in dir_list:
            for filename in listdir(directory):
                # load the image
                image = cv2.imread(directory + '\\' + filename)
                # crop the brain and ignore the unnecessary rest part of the image
                image = crop_brain_contour(image, plot=False)
                # resize image
                image = cv2.resize(image, dsize=(image_width, image_height), interpolation=cv2.INTER_CUBIC)
                # normalize values
                image = image / 255.
                # convert image to numpy array and append it to X
                X.append(image)
                # append a value of 1 to the target array if the image
                # is in the folder named 'yes', otherwise append 0.
                if directory[-3:] == 'yes':
                    y.append([1])
                else:
                    y.append([0])

        X = np.array(X)
        y = np.array(y)

        # Shuffle the data
        X, y = shuffle(X, y)

        print(f'Number of examples is: {len(X)}')
        print(f'X shape is: {X.shape}')
        print(f'y shape is: {y.shape}')

        return X, y

    import os
    augmented_path = r'C:\Users\Muhammad Usama Abid\Desktop\uni\augmented_data'

    # augmented data (yes and no) contains both the original and the new generated examples
    augmented_yes = os.path.join(augmented_path, 'yes')
    augmented_no = os.path.join(augmented_path, 'no')

    IMG_WIDTH, IMG_HEIGHT = (240, 240)

    X, y = load_data([augmented_yes, augmented_no], (IMG_WIDTH, IMG_HEIGHT))

    """
    def plot_sample_images(X, y, n=50):
        for label in [0, 1]:
            # grab the first n images with the corresponding y values equal to label
            images = X[np.argwhere(y == label)]
            n_images = images[:n]

            columns_n = 10
            rows_n = int(n / columns_n)

            plt.figure(figsize=(20, 10))

            i = 1  # current plot
            for image in n_images:
                plt.subplot(rows_n, columns_n, i)
                plt.imshow(image[0])

                # remove ticks
                plt.tick_params(axis='both', which='both',
                                top=False, bottom=False, left=False, right=False,
                                labelbottom=False, labeltop=False, labelleft=False, labelright=False)

                i += 1

            label_to_str = lambda label: "Yes" if label == 1 else "No"
            plt.suptitle(f"Brain Tumor: {label_to_str(label)}")
            plt.show()

    plot_sample_images(X, y)
    """

    def split_data(X, y, test_size=0.2):
        X_train, X_test_val, y_train, y_test_val = train_test_split(X, y, test_size=test_size)
        X_test, X_val, y_test, y_val = train_test_split(X_test_val, y_test_val, test_size=0.5)

        return X_train, y_train, X_val, y_val, X_test, y_test

    X_train, y_train, X_val, y_val, X_test, y_test = split_data(X, y, test_size=0.3)

    def build_model(input_shape):
        # Define the input placeholder as a tensor with shape input_shape.
        X_input = Input(input_shape)  # shape=(?, 240, 240, 3)

        # Zero-Padding: pads the border of X_input with zeroes
        X = ZeroPadding2D((2, 2))(X_input)  # shape=(?, 244, 244, 3)

        # CONV -> BN -> RELU Block applied to X
        X = Conv2D(32, (7, 7), strides=(1, 1), name='conv0')(X)
        X = BatchNormalization(axis=3, name='bn0')(X)
        X = Activation('relu')(X)  # shape=(?, 238, 238, 32)

        # MAXPOOL
        X = MaxPooling2D((4, 4), name='max_pool0')(X)  # shape=(?, 59, 59, 32)

        # MAXPOOL
        X = MaxPooling2D((4, 4), name='max_pool1')(X)  # shape=(?, 14, 14, 32)

        # FLATTEN X
        X = Flatten()(X)  # shape=(?, 6272)
        # FULLYCONNECTED
        X = Dense(1, activation='sigmoid', name='fc')(X)  # shape=(?, 1)

        # Create model. This creates your Keras model instance, you'll use this instance to train/test the model.
        model = Model(inputs=X_input, outputs=X, name='BrainDetectionModel')

        return model

    IMG_SHAPE = (IMG_WIDTH, IMG_HEIGHT, 3)
    model = build_model(IMG_SHAPE)
    print(model.summary())

    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

    # Nicely formatted time string
    def hms_string(sec_elapsed):
        h = int(sec_elapsed / (60 * 60))
        m = int((sec_elapsed % (60 * 60)) / 60)
        s = sec_elapsed % 60
        return f"{h}:{m}:{round(s, 1)}"

    def compute_f1_score(y_true, prob):
        # convert the vector of probabilities to a target vector
        y_pred = np.where(prob > 0.5, 1, 0)

        score = f1_score(y_true, y_pred)

        return score

    start_time = time.time()

    model.fit(x=X_train, y=y_train, batch_size=32, epochs=10, validation_data=(X_val, y_val))

    end_time = time.time()
    execution_time = (end_time - start_time)
    print(f"Elapsed time: {hms_string(execution_time)}")

    def plot_metrics(history):
        train_loss = history['loss']
        val_loss = history['val_loss']
        train_acc = history['accuracy']
        val_acc = history['val_accuracy']

        # Loss
        plt.figure()
        plt.plot(train_loss, label='Training Loss')
        plt.plot(val_loss, label='Validation Loss')
        plt.title('Loss')
        plt.legend()
        plt.show()

        # Accuracy
        plt.figure()
        plt.plot(train_acc, label='Training Accuracy')
        plt.plot(val_acc, label='Validation Accuracy')
        plt.title('Accuracy')
        plt.legend()
        plt.show()

    history = model.history.history
    print(history)
    for key in history.keys():
        print(key)
    plot_metrics(history)
    loss, acc = model.evaluate(x=X_test, y=y_test)
    # Accuracy of the best model on the testing data
    print(f"Test Loss = {loss}")
    print(f"Test Accuracy = {acc}")
