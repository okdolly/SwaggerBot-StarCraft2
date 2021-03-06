import pickle
import random
import numpy as np
import tensorflow as tf
# from pad_data import pad_and_batch
# from prep_data import units, terran_x, terran_y, dict_map

## borrow some implementation from N. Locascio's code ob github
## https://github.com/nicholaslocascio/bcs-lstm/blob/master/draft/rnn.py
if __name__ == '__main__':
	## vector lengths for training and testing data 
	n_features = 68
	print("terran_x length is\n")
	## y vector length meant for the unit to use
	## (e.g 21 == 'SCV') or something (forget about events)
	n_outs = 36
	## number of batches
	batch_size = 1
	## hidden lstm cell sizes
	rnn_size = 100

	x_train = tf.placeholder(tf.float32, [batch_size, None, n_features])
	y_train = tf.placeholder(tf.float32, [batch_size, None])

	cell = tf.nn.rnn_cell.LSTMCell(rnn_size)

	init_state = cell.zero_state(rnn_size, tf.float32)
	outputs, final_state = tf.nn.dynamic_rnn(cell, x_train, dtype=tf.float32)

	if 'session' in locals() and session is not None:
		print('Close interactive session')
		session.close()

	config = tf.ConfigProto()
	config.gpu_options.allow_growth = True

	with tf.Session(config=config) as sess:
		tf.global_variables_initializer().run(session=sess)
		# random.shuffle(data)

		err_rate = 0.0
		for batch in data:
			x = [36]
			# print("batch[0] is\n", batch[0])
			# x = np.array(batch[0], dtype=np.float32)
			# print("x is\n", x)
			# print("length of row in x is\n", len(x))
			# y = []
			# for row in batch[1]:
			# 	y.append(row[0])
			# # print(y)
			# # y = np.array(batch[1], dtype=np.float32)
			# x = np.reshape(x, (-1, batch_size, n_features))
			# x = np.reshape(x, (x.shape[1], x.shape[0], x.shape[2]))
			o, s = sess.run([outputs, final_state], feed_dict={x_train:x})
			print("output:\n", o.shape)
			print("final s:\n", s[0].shape, s[1].shape)
			exit()


	#mapped_units = dict_map(units, 1)
