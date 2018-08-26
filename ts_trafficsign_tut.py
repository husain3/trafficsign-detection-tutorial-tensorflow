import os
import random
import skimage.data
import skimage.transform
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

def load_data(data_dir):
	"""Loads a dta set and returns two lists:
	
	images: a list of Numpy arrays, each representing an image
	labels: a list of numbers that represent the images labels.
		
	"""

	#Get all subdirectories of data_dir. Each represent a label.

	directories = [d for d in os.listdir(data_dir)
				if os.path.isdir(os.path.join(data_dir, d))] #might be an indentation error here
	# Loop through the label directories and collect the data in
	# two lists, labels and images

	labels = []
	images = []

	for d in directories:
		label_dir = os.path.join(data_dir, d)
		file_names = [os.path.join(label_dir, f)
						for f in os.listdir(label_dir) if f.endswith(".ppm")]
		# For each label, load it's images and add them to the images list.
		# And add the label number (i.e. directory name) to the labels list.

		#print("%s %s" % (label_dir, file_names))
		#print("\n")	
		for f in file_names:
			images.append(skimage.data.imread(f))
			labels.append(int(d))

	
	print("Unique Labels: {0}\nTotal Images: {1}".format(len(set(labels)), len(images)))
	return images, labels


# Load training and testing datasets

def display_images_and_labels(images, labels):
	"""Display the first image of each label."""
	unique_labels = set(labels)
	plt.figure(figsize=(15, 15))
	i = 1
	for label in unique_labels:
		#Pick the first image for each label
		image = images[labels.index(label)]
		plt.subplot(8, 8, i) #A grid of 8 rows x 8 columns
		plt.axis('off')
		plt.title("Label {0} ({1})".format(label, labels.count(label)))
		i += 1
		_ = plt.imshow(image)
	plt.show()

def display_label_images(images, label):
	"""Display images of a specific label."""
	limit = 24 # show a max of 24 images
	plt.figure(figsize=(15, 5))
	i = 1

	start = labels.index(label)
	end = start + labels.count(label)
	for image in images[start:end][:limit]:
		plt.subplot(3, 8, i) #3 rows, 8 per row
		plt.axis('off')
		i += 1
		plt.imshow(image)
	plt.show()

ROOT_PATH = "/home/arshad/traffic"
train_data_dir = os.path.join(ROOT_PATH, "datasets/BelgiumTS/Training")
test_data_dir = os.path.join(ROOT_PATH, "datasets/BelgiumTS/Testing")

images, labels = load_data(train_data_dir)

#These two function calls are to display images and labels
#display_images_and_labels(images, labels)
#display_label_images(images, 32)

for image in images[:5]:
	print("Shape: {0}, min: {1}, max: {2}".format(image.shape, image.min(), image.max()))

#resize images
images32 = [skimage.transform.resize(image, (32, 32), mode='constant')
				for image in images]

#This function calls is to display new 32x32 images and labels
#display_images_and_labels(images32, labels)

for image in images32[:5]:
	print("Shape: {0}, min: {1}, max: {2}".format(image.shape, image.min(), image.max()))

#Minimum Viable Model
labels_a = np.array(labels)
images_a = np.array(images32)
print("labels: ", labels_a.shape, "images: ", images_a.shape)

#create a graph to hold the model.
graph = tf.Graph()

#create model in the graph
with graph.as_default():
	#Placeholders for inputs and labels
	images_ph = tf.placeholder(tf.float32, [None, 32, 32, 3])
	labels_ph = tf.placeholder(tf.int32, [None])

	#Flatten input from: [None, height, width, channels]
	#To: [None, height * width * channels] == [None, 3072]
	images_flat = tf.contrib.layers.flatten(images_ph)

	#Fully connected layer
	#Generates logits of size [None, 62]
	logits = tf.contrib.layers.fully_connected(images_flat, 62, tf.nn.relu)

	#Convert logits to label indexes (int)
	#Shape [None], which is a 1D vector of length == batch_size.
	predicted_labels = tf.argmax(logits, 1)

	#Define the loss function
	#Cross-entropy is a good choice for classification
	loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=labels_ph))

	#Create training op
	train = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)

	#And, finally, an initialization op to execute before training	
	init = tf.global_variables_initializer()

print("images_flat: ", images_flat)
print("logits: ", logits)
print("loss: ", loss)
print("predicted_labels: ", predicted_labels)


#Create a session to run the graph we created.
session = tf.Session(graph=graph)

#First step is always to initialize all variables
#We don't care about the return value, though, It's None.
_ = session.run([init])

for i in range(402):
	_, loss_value = session.run([train, loss], feed_dict={images_ph: images_a, labels_ph: labels_a})

	if i % 10 == 0:
		print("Loss: ", loss_value)

#USING THE TRAINED MODEL
#pick 10 random images
sample_indexes = random.sample(range(len(images32)), 10)
sample_images = [images32[i] for i in sample_indexes]
sample_labels = [labels[i] for i in sample_indexes]

#run the "predicted_labels" op.
predicted = session.run([predicted_labels], feed_dict={images_ph: sample_images})[0]
print(sample_labels)
print(predicted)

#Display the predictions and the ground truth visually
fig = plt.figure(figsize=(10, 10))
for i in range(len(sample_images)):
	truth = sample_labels[i]
	prediction = predicted[i]
	plt.subplot(5, 2, 1+i)
	plt.axis('off')
	color='green' if truth==prediction else 'red'

	plt.text(40, 10, "Truth:	{0}\nPrediction: {1}".format(truth, prediction), fontsize=12, color=color)
	plt.imshow(sample_images[i])

plt.show()


