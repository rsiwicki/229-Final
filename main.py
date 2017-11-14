import sys
import os.path
import tensorflow as tf
import helper
import warnings
from distutils.version import LooseVersion
import project_tests as tests

# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion(
    '1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    # TODO: Implement function
    #   Use tf.saved_model.loader.load to load the model and weights
    # return None, None, None, None, None

    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'

    tf.saved_model.loader.load(sess, [vgg_tag], vgg_path)
    image_input = sess.graph.get_tensor_by_name(vgg_input_tensor_name)
    keep_prob = sess.graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    layer3_out = sess.graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    layer4_out = sess.graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    layer7_out = sess.graph.get_tensor_by_name(vgg_layer7_out_tensor_name)

    return image_input, keep_prob, layer3_out, layer4_out, layer7_out


tests.test_load_vgg(load_vgg, tf)


def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer7_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer3_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    # TODO: Implement function
    # return None


    conv_out = tf.layers.conv2d(vgg_layer7_out, num_classes, 1, 1,
                                kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    # transposed convolutions - upsample by 2
    deconv_1 = tf.layers.conv2d_transpose(conv_out, num_classes, 4, 2, 'SAME',
                                          kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    # deconv_1 = tf.layers.conv2d_transpose(conv_out, num_classes, 64,32, 'SAME', kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    # skip connection to previous VGG layer
    skip_layer_1 = tf.layers.conv2d(vgg_layer4_out, num_classes, 1, 1,
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    skip_conn_1 = tf.add(deconv_1, skip_layer_1)

    # Upsample by 2
    deconv_2 = tf.layers.conv2d_transpose(skip_conn_1, num_classes, 4, 2, 'SAME',
                                          kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    skip_layer_2 = tf.layers.conv2d(vgg_layer3_out, num_classes, 1, 1,
                                    kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    skip_conn_2 = tf.add(deconv_2, skip_layer_2)

    # Upsample by 8 (three pooling layers in VGG encoder)
    deconv_3 = tf.layers.conv2d_transpose(skip_conn_2, num_classes, 16, 8, 'SAME',
                                          kernel_initializer=tf.truncated_normal_initializer(stddev=0.01))
    return deconv_3


tests.test_layers(layers)


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """
    # TODO: Implement function
    # return None, None, None

    # define logits and labels
    logits = tf.reshape(nn_last_layer, (-1, num_classes))
    labels = tf.reshape(correct_label, (-1, num_classes))
    # loss function
    cross_entropy_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=logits))
    # Optimizer
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    # train_op = minimise loss
    train_op = optimizer.minimize(cross_entropy_loss)

    return logits, train_op, cross_entropy_loss


tests.test_optimize(optimize)


def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_im	age: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    # TODO: Implement function
    # pass
    # global g_iou
    patience = 1
    keep_prob_stat = 0.8
    learning_rate_stat = 1e-4
    # g_iou,_ = tf.metrics.mean_iou(tf.argmax(tf.reshape(correct_label, (-1, 2)), -1), tf.argmax(logits, -1),num_classes)

    # Write metrics to data.txt for plotting later.
    with open("data.txt", "w") as data:
        val_loss_history = [float("inf")]
        for epoch in range(epochs):
            avg_loss = 0
            n = 0
            for image, label in get_batches_fn(batch_size, get_train=True):
                _, loss = sess.run([train_op, cross_entropy_loss],
                                   feed_dict={input_image: image,
                                              correct_label: label,
                                              keep_prob: keep_prob_stat,
                                              learning_rate: learning_rate_stat})
                # iou = sess.run(g_iou)
                avg_loss = (avg_loss * n + loss) / (n + 1)
                n += 1
                # Overwrite last line of stdout on linux. Not sure if this works on windows...
                print("Epoch %d of %d: Batch loss %.4f, Avg loss: %.4f\r" % (epoch + 1, epochs, loss, avg_loss), end="")
            print("\nEpoch %d of %d: Final Training loss: %.4f" % (epoch + 1, epochs, avg_loss))

            val_loss = 0
            n = 0
            for image, label in get_batches_fn(batch_size, get_train=False):
                loss, = sess.run([cross_entropy_loss],
                                 feed_dict={input_image: image,
                                            correct_label: label,
                                            keep_prob: keep_prob_stat,
                                            learning_rate: learning_rate_stat})

                val_loss = (val_loss * n + loss) / (n + 1)
                n += 1
            print("%d\t%f\t%f" % (epoch + 1, avg_loss, val_loss), file=data)
            print("Epoch %d of %d: Val loss %.4f" % (epoch + 1, epochs, val_loss))
            val_loss_history.append(val_loss)
            if helper.early_stopping(val_loss_history, patience):
                print("Early stopping. Min Val Loss:", min(val_loss_history))
                break
                # sess.run(g_iou)


tests.test_train_nn(train_nn)


def run():
    # global g_iou
    # global g_iou_op
    image_shape = (160, 576)
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)

    epochs = 50
    batch_size = 2
    num_classes = 2
    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)

    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/

    with tf.Session() as sess:
        # Path to vgg model
        vgg_path = os.path.join(data_dir, 'vgg')
        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network

        # TODO: Build NN using load_vgg, layers, and optimize function
        image_input, keep_prob, vgg_layer3_out, vgg_layer4_out, vgg_layer7_out = load_vgg(sess, vgg_path)
        # Fully Convolutional Network
        last_layer = layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes)
        correct_label = tf.placeholder(dtype=tf.float32, shape=(None, None, None, num_classes))
        learning_rate = tf.placeholder(dtype=tf.float32)

        # TODO: where does logits get used?`
        logits, train_op, cross_entropy_loss = optimize(last_layer, correct_label, learning_rate, num_classes)
        g_iou, g_iou_op = tf.metrics.mean_iou(tf.argmax(tf.reshape(correct_label, (-1, 2)), -1), tf.argmax(logits, -1),
                                              num_classes)

        # TODO: Train NN using the train_nn function
        sess.run(tf.global_variables_initializer())
        train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, image_input, correct_label,
                 keep_prob, learning_rate)

        # iou = sess.run(g_iou)
        # print("IOU: %.4f" %(iou))

        # print("g_iou",sess.run(g_iou, g_iou_op))

        # TODO: Save inference data using helper.save_inference_samples
        helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep_prob, image_input)

        # OPTIONAL: Apply the trained model to a video


if __name__ == '__main__':
    run()
