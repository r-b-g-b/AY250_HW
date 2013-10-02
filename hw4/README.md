This code trains an image classifier on a set of images stored in the directory '50_categories.' The features used are correlation coefficients between the three color channels (1-3), a 2-D FFT-based estimate of spectral power in 12 spectral frequency bins (4-16), and the first 15 principal components of the histogram of gradients (HOG).

runClassifier.py
	
	train : this function trains the classifier on the full set of images in 50 categories. It prints the output of classification and computes an accuracy estimate using 5-Fold cross-validation. Prints the Top 3 Most Informative Features. The output is saved to "trained_classifier.p"
	Input:
		load_precomputed : default True. if true it loads precomputed features, if false it computes the features from scratch

	run_final_classifier : this function loads the previously calculated features from the training set to generate a mode. it then runs the model on a set of validation images stored in the testimgdir.
	Input:
		testimgdir : absolute path to the test images

calcFeatures.py
	Contains the code used to calculate all of the features used for classification. See internal documentation for descriptions of the code. The features are the correlation coefficients between each of the color channels, a histogram of spatial frequency content, and the first 15 principal components of a histogram of gradients measure (HOG) from skimage.
