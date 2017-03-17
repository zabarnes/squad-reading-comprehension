# -*- coding: utf-8 -*-

""" Auto Encoder Example.
Using an auto encoder on MNIST handwritten digits.
References:
    Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner. "Gradient-based
    learning applied to document recognition." Proceedings of the IEEE,
    86(11):2278-2324, November 1998.
Links:
    [MNIST Dataset] http://yann.lecun.com/exdb/mnist/
"""
from __future__ import division, print_function, absolute_import

import tensorflow as tf
import numpy as np


class data_wrapper:
    def __init__(self, input_mats, batch_size):
        #self.file_name = file_name
        #self.inputs = self.read_file()
        self.inputs = input_mats
        self.batch_size = batch_size
        self.cur_batch = 0
        self.total_batch = int(len(self.inputs)/batch_size-1)

    def read_file(self):
        inputs = np.load(self.file_name)
        inputs = inputs['data']
        return inputs

    def get_next_batch(self):
        val = self.inputs[self.cur_batch*self.batch_size:self.cur_batch*self.batch_size+self.batch_size]
        self.cur_batch += 1
        if self.cur_batch*self.batch_size+self.batch_size+200 >= len(self.inputs):
            self.cur_batch = 0
        return val,val

    def get_unseen_data(self):
        val = self.inputs[-200:]
    	return val,val

class autoencoder:
    def __init__(self, input_mats):
        # Parameters
        self.learning_rate = 0.04

        self.training_epochs = 50
        self.batch_size = 1
        self.display_step = 1
        self.examples_to_show = 10
        self.dropout = .5

        # Network Parameters
        self.n_hidden_3 = 20 # 2nd layer num features
        self.n_hidden_2 = 100
	self.n_hidden_1 = 200 # 1st layer num features

        self.n_input_1 = 300 # data dimension 1 
        self.n_input_2 = 300 # data dimension 2

        # Data Class
        self.my_data = data_wrapper(input_mats, self.batch_size)

        self.setup()
        self.saver = tf.train.Saver()

    def setup(self):
        # tf Graph input (only pictures)
        self.X = tf.placeholder("float", [None, self.n_input_1, self.n_input_2])
        self.dropout_placeholder = tf.placeholder(tf.float32, (), name="dropout_placeholder")

        self.weights = {
            'encoder_h1': tf.Variable(tf.random_normal([self.n_input_2, self.n_hidden_1])),
            'encoder_h2': tf.Variable(tf.random_normal([self.n_hidden_1, self.n_hidden_2])),
	    'encoder_h3': tf.Variable(tf.random_normal([self.n_hidden_2, self.n_hidden_3])),
            'decoder_h1': tf.Variable(tf.random_normal([self.n_hidden_3, self.n_hidden_2])),
            'decoder_h2': tf.Variable(tf.random_normal([self.n_hidden_2, self.n_input_1])),
            'decoder_h3': tf.Variable(tf.random_normal([self.n_hidden_1, self.n_input_2])),
        }
        self.biases = {
            'encoder_b1': tf.Variable(tf.random_normal([1,self.n_hidden_1])),
            'encoder_b2': tf.Variable(tf.random_normal([1,self.n_hidden_2])),
            'encoder_b3': tf.Variable(tf.random_normal([1,self.n_hidden_3])),
            'decoder_b1': tf.Variable(tf.random_normal([1,self.n_hidden_2])),
            'decoder_b2': tf.Variable(tf.random_normal([1,self.n_hidden_1])),
            'decoder_b3': tf.Variable(tf.random_normal([1,self.n_input_2])),
        }
        # Construct model
        encoder_op = self.encoder(self.X)
        self.decoder_op = self.decoder(encoder_op)

        # Prediction
        y_pred = self.decoder_op
        # Targets (Labels) are the input data.
        y_true = self.X

        # Define loss and optimizer, minimize the squared error
        self.cost = tf.reduce_mean(tf.pow(y_true - y_pred, 2))
        self.optimizer = tf.train.RMSPropOptimizer(self.learning_rate).minimize(self.cost)

    # Building the encoder
    def encoder(self, x):
        # Encoder Hidden layer with sigmoid activation #1

        assert x.get_shape().as_list() == [None,self.n_input_1,self.n_input_2]
        term = tf.reshape(x,[-1,self.n_input_2])
        assert term.get_shape().as_list() == [None,self.n_input_2]
        term = tf.matmul(term,self.weights['encoder_h1']) + self.biases['encoder_b1']
        assert term.get_shape().as_list() == [None,self.n_hidden_1]
        layer_1 = tf.nn.sigmoid(term)
        tf.nn.dropout(layer_1, self.dropout_placeholder)
        assert layer_1.get_shape().as_list() == [None,self.n_hidden_1]


        term2 = tf.matmul(layer_1,self.weights['encoder_h2']) + self.biases['encoder_b2']
        assert term2.get_shape().as_list() == [None,self.n_hidden_2]
        layer_2 = tf.nn.sigmoid(term2)
        assert layer_2.get_shape().as_list() == [None,self.n_hidden_2]


        term3 = tf.matmul(layer_2,self.weights['encoder_h3']) + self.biases['encoder_b3']
        assert term3.get_shape().as_list() == [None,self.n_hidden_3]
        layer_3 = tf.nn.sigmoid(term3)
        assert layer_3.get_shape().as_list() == [None,self.n_hidden_3]


        result = tf.reshape(layer_3,[-1,self.n_input_2,self.n_hidden_3])
        assert result.get_shape().as_list() == [None,self.n_input_1,self.n_hidden_3]
        tf.nn.dropout(result, self.dropout_placeholder)
        return result



    # Building the decoder
    def decoder(self, x):
        # Encoder Hidden layer with sigmoid activation #1

        assert x.get_shape().as_list() == [None,self.n_input_1,self.n_hidden_3]
        term = tf.reshape(x,[-1,self.n_hidden_3])
        assert term.get_shape().as_list() == [None,self.n_hidden_3]
        term = tf.matmul(term,self.weights['decoder_h1']) + self.biases['decoder_b1']
        assert term.get_shape().as_list() == [None,self.n_hidden_2]
        layer_1 = tf.nn.sigmoid(term)
        tf.nn.dropout(layer_1, self.dropout_placeholder)
        assert layer_1.get_shape().as_list() == [None,self.n_hidden_2]

        term2 = tf.matmul(layer_1,self.weights['decoder_h2']) + self.biases['decoder_b2']
        assert term2.get_shape().as_list() == [None,self.n_hidden_1]
        layer_2 = tf.nn.sigmoid(term2)
        assert layer_2.get_shape().as_list() == [None,self.n_hidden_1]


        term3 = tf.matmul(layer_2,self.weights['decoder_h3']) + self.biases['decoder_b3']
        assert term3.get_shape().as_list() == [None,self.n_input_2]
        layer_3 = tf.nn.sigmoid(term3)
        assert layer_3.get_shape().as_list() == [None,self.n_input_2]

        result = tf.reshape(layer_3,[-1,self.n_input_1,self.n_input_2])
        assert result.get_shape().as_list() == [None,self.n_input_1,self.n_input_2]

        return result


    def answer(self):
        self.saver.restore(sess, "/data/autoencoder.ckpt")

        result = []
        init = tf.global_variables_initializer()
        # Launch the graph
        with tf.Session() as sess:
            sess.run(init)
            total_batch = self.my_data.total_batch
            # Training cycle
            count = 0
            for epoch in range(self.training_epochs):
                # Loop over all batches
                epoch_cost = []
                for i in range(total_batch):
                    batch_xs, batch_ys = self.my_data.get_next_batch()
                    # Run optimization op (backprop) and cost op (to get loss value)
                    output_feed = [self.decoder_op]
                    input_feed = {self.X: batch_xs, self.dropout_placeholder: self.dropout}
                    decoded = sess.run(output_feed, input_feed)
                    result.extend(decoded)
        np.savez('data/encoded_hr',data='result')


    def train(self):

        # Initializing the variables
        init = tf.global_variables_initializer()
        # Launch the graph
        with tf.Session() as sess:
            sess.run(init)
            total_batch = self.my_data.total_batch
            # Training cycle
            count = 0
            for epoch in range(self.training_epochs):
                # Loop over all batches
                epoch_cost = []
                for i in range(total_batch):
                    batch_xs, batch_ys = self.my_data.get_next_batch()
                    # Run optimization op (backprop) and cost op (to get loss value)
                    output_feed = [self.optimizer, self.cost, self.decoder_op]
                    input_feed = {self.X: batch_xs, self.dropout_placeholder: self.dropout}
                    _, c, decoded = sess.run(output_feed, input_feed)
                    count += 1

                    epoch_cost.append(c)
                # Display logs per epoch step
                epoch_cost = float(sum(epoch_cost))/len(epoch_cost)
                if epoch % self.display_step == 0:
                    print("Epoch:", '%04d' % (epoch+1),
                          "cost=", "{:.9f}".format(epoch_cost))
                if epoch % 4 == 0:
                    print("unseen set")
                    batch_xs, batch_ys = self.my_data.get_unseen_data()
                    output_feed = [self.cost]
                    input_feed = {self.X: batch_xs, self.dropout_placeholder: 1}
                    c = sess.run(output_feed, input_feed)
                    print(c)

            print("Optimization Finished!")
            save_path = self.saver.save(sess, "/data/autoencoder.ckpt")

print("loading 1st datafile")
my_data = np.load('data/encodings0.npz')['data']
print("loading 2nd datafile")
my_data = np.concatenate((my_data,np.load('data/encodings1.npz')['data']),axis=0)
a = autoencoder(my_data)
a.train()





