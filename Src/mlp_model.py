# TensorFlow
import tensorflow as tf

# Helper libraries
import numpy as np
import utils

DATA_DIR = "../Datasets/Final_Data/normalized_all_vectors_merged_timeseries(4)_btc_only.csv"

# Parameters
learning_rate = 0.0001
training_epochs = 400
batch_size = 32
display_step = 100

# Network Parameters
n_hidden_1 = 64 # 1st layer number of neurons
n_hidden_2 = 128 # 2nd layer number of neurons
n_hidden_3 = 32 # 3rd layer number of neurons
num_input = 18*4 # input vector size
num_classes = 2 # 2 classes good-bad

# tf Graph input
X = tf.placeholder("float", [None, num_input])
Y = tf.placeholder("float", [None, num_classes])

# Store layers weight & bias
weights = {
    'h1': tf.Variable(tf.random_normal([num_input, n_hidden_1])),
    'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
    'h3': tf.Variable(tf.random_normal([n_hidden_2, n_hidden_3])),
    'out': tf.Variable(tf.random_normal([n_hidden_3, num_classes]))
}
biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1])),
    'b2': tf.Variable(tf.random_normal([n_hidden_2])),
    'b3': tf.Variable(tf.random_normal([n_hidden_3])),
    'out': tf.Variable(tf.random_normal([num_classes]))
}

# Create model
def neural_net(x,weights, biases):
    # Hidden fully connected layer with 16 neurons
    layer_1 = tf.add(tf.matmul(x, weights['h1']), biases['b1'])
    layer_1 = tf.nn.relu(layer_1)
    # Hidden fully connected layer with 16 neurons
    layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])
    layer_2 = tf.nn.relu(layer_2)
    # Hidden fully connected layer with 16 neurons
    layer_3 = tf.add(tf.matmul(layer_2, weights['h3']), biases['b3'])
    layer_3 = tf.nn.relu(layer_3)    
    # Output fully connected layer with a neuron for each class
    out_layer = tf.matmul(layer_3, weights['out']) + biases['out']
    return out_layer


# Construct model
logits = neural_net(X,weights,biases)

# Define loss and optimizer
loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss_op)

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()


print("Loading data..")

train_mode = 0

if(train_mode==0):
    data = utils.load_dataset(DATA_DIR,0)
    inputs,labels,feature_num = utils.convert_data_to_arrays(data,0,0)
    train_inputs,train_labels,test_inputs,test_labels = utils.smash_data_for_timeseries(inputs,labels)
else:
    data = utils.load_dataset(DATA_DIR,1)
    train,test = utils.smash_train_test(data)
    train_inputs,train_labels,feature_num = utils.convert_data_to_arrays(train,0,1)
    test_inputs,test_labels,feature_num = utils.convert_data_to_arrays(test,0,1)

if(len(train_labels) % batch_size == 0):
    train_iters = len(train_labels) / batch_size
else:
    train_iters = len(train_labels) / batch_size + 1

if(len(test_labels) % batch_size == 0):
	test_iters = len(test_labels) / batch_size
else:
	test_iters = len(test_labels) / batch_size + 1

print("Optimization starting..")

    
with tf.Session() as sess:
    sess.run(init)

    for epoch in range(training_epochs):
        
        avg_cost = 0.0

        #Loop over all batches
        for i in range(train_iters):

            batch_x = utils.next_batch(train_inputs,i,batch_size)
            batch_y = utils.next_batch(train_labels,i,batch_size)

            # Run optimization op (backprop) and cost op (to get loss value)
            _, c = sess.run([optimizer, loss_op], feed_dict={X: batch_x,
                                                         Y: batch_y})
            # Compute average loss
            avg_cost += c / train_iters
        # Display logs per epoch step
        if epoch % display_step == 0:
           print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(avg_cost))

    print("Optimization Finished!")


    print("Testing starting..")

    test_mode = 1

    #calculate accuraacy
    #test_mode=0: just the accuracy/f1/recall/precision/confusion matrix of the model
    #test_mode=1: calculate the accuracy, take the exact prediction and plot the faults (designed only for one asset testing)

    if(test_mode==0):

        correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(Y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
        print("Tf-Accuracy:", accuracy.eval({X: test_inputs, Y: test_labels}))

        y_p = tf.argmax(logits, 1)
        preds = sess.run([y_p], feed_dict = {X: test_inputs})
        preds = np.array(preds)[0]
        utils.calculate_metrics(preds,np.argmax(test_labels,1))

    else:

        Accuracy = 0
        pred_list = []

        for i in range(test_iters):
            next_input = utils.next_batch(test_inputs,i,batch_size)
            next_label = utils.next_batch(test_labels,i,batch_size)
            preds = sess.run([logits], feed_dict = {X: next_input})

            Acc,predictions = utils.examine_faults(preds,next_label)

            Accuracy += Acc

            pred_list.append(predictions)

            flat_list = []
            for sublist in pred_list:
                for item in sublist:
                    flat_list.append(item)

        print(float(float(Accuracy)/float(test_iters)))

        if(train_mode==0):
            utils.figure_faults_timeseries(flat_list)
        else:
            utils.figure_faults(test,data,flat_list)


	
