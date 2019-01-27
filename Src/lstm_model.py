# TensorFlow
import tensorflow as tf
from tensorflow.contrib import rnn

# Helper libraries
import numpy as np
import utils
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score

DATA_DIR = "../Datasets/normalized_all_vectors_merged_timeseries.csv"

learning_rate = 0.001
epochs = 10
n_classes = 1
n_units =512
number_of_layers = 3
input_length = 10
number_of_sequences = 18
batch_size = 32
num_layers = 5
drop_prob = 0.4

xplaceholder= tf.placeholder('float',[None,input_length,number_of_sequences])
yplaceholder = tf.placeholder('float')

def recurrent_neural_network_model():

	x = tf.unstack(xplaceholder,input_length,axis=1)
	layer ={ 'weights': tf.Variable(tf.random_normal([n_units, n_classes])),'bias': tf.Variable(tf.random_normal([n_classes]))}
	

	lstm_cells = []
	for _ in range(num_layers):
		cell = tf.nn.rnn_cell.LSTMCell(n_units) 
		cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=1-drop_prob)
		lstm_cells.append(cell)

	lstm_layers = rnn.MultiRNNCell(lstm_cells)
	outputs, states = tf.nn.static_rnn(lstm_layers, x, dtype=tf.float32)
	return tf.matmul(outputs[-1], layer['weights']) + layer['bias']

logit = recurrent_neural_network_model()
logit = tf.reshape(logit, [-1])
cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=logit, labels=yplaceholder))
optimizer = tf.train.RMSPropOptimizer(learning_rate=learning_rate).minimize(cost)

init = tf.global_variables_initializer()

print("Loading data..")
	
data = utils.load_dataset(DATA_DIR)

train,test = utils.smash_train_test(data)

train_inputs,train_labels,feature_num = utils.convert_data_to_arrays(train,1)
test_inputs,test_labels,feature_num = utils.convert_data_to_arrays(test,1)

train_iters = 0
if(len(train_labels) % batch_size == 0):
    train_iters = len(train_labels) / batch_size
else:
    train_iters = len(train_labels) / batch_size + 1


print("Optimization starting..")

    
with tf.Session() as sess:
	sess.run(init)

	for epoch in range(epochs):
		epoch_loss = 0

		for i in range(train_iters):

			batch_x = utils.next_batch(train_inputs,i,batch_size)
			batch_y = utils.next_batch(train_labels,i,batch_size)

			batch_x = batch_x.reshape((-1,input_length,number_of_sequences))

			_, c = sess.run([optimizer, cost], feed_dict={xplaceholder: batch_x, yplaceholder: batch_y})

			epoch_loss += c/train_iters

		print('Epoch', epoch, 'completed out of', epochs, 'loss:', epoch_loss)

	print("Optimization Finished!")

	correct_preds = tf.round(tf.nn.sigmoid(logit)) 

	accuracy = tf.reduce_mean(tf.cast(correct_preds, "float"))

	# Calculate accuracy
	test_inputs = test_inputs.reshape((-1,input_length,number_of_sequences))
	print("Accuracy: ",accuracy.eval({xplaceholder: np.array(test_inputs), yplaceholder: np.array(test_labels)}))