import numpy as np
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures

class DecisionTreeNode:
    # Constructor
    # Feature index represents the index of the feature that the node uses to split the data
    # Threshold is the value used to split the data at this node
    def __init__(self, feature_index=None, threshold=None, left=None, right=None, *, value=None):
        self.feature_index = feature_index
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

def calculate_gini_index(groups, classes):
    # groups is a list containing 2 or 3 lists of lists, classes is [-1, 1]
    n_instances = 0
    for group in groups:
        n_instances += len(group)
    gini = 0.0
    for group in groups:
        size = len(group)
        if size == 0:
            continue
        score = 0.0
        for class_val in classes:
            class_labels = []
            for row in group:
                # Extract the class label (result)
                class_labels.append(row[-1])
            # How many times the class value is inside the class labels list
            p = class_labels.count(class_val) / size
            score += p * p
        # Measure the impurity of a dataset, or how well a feature splits the data in terms of separating the classes
        gini += (1.0 - score) * (size / n_instances)
    return gini

def split_node(index, value, dataset):
    # Dataset contains a number of rows
    # Value is the value used for splitting
    # Index is the index of the attribute on which the split will be based
    left = []
    right = []
    for row in dataset:
        if row[index] < value:
            left.append(row)
        else:
            right.append(row)
    # Divide the dataset into 2 subsets based on a specific feature and value
    return left, right

def get_best_split(dataset, n_features):
    # n_features is the number of features to consider
    # Extract the unique class values from the dataset
    unique_class_values = set()
    for row in dataset:
        unique_class_values.add(row[-1])
    class_values = list(unique_class_values)
    best_score = 999
    # Randomly select a subset of features (columns) to consider for splitting, excluding the class label
    features = np.random.choice(len(dataset[0]) - 1, n_features, replace=False)
    for index in features:
        for row in dataset:
            groups = split_node(index, row[index], dataset)
            gini = calculate_gini_index(groups, class_values)
            if gini < best_score:
                best_index = index
                best_value = row[index]
                best_score = gini
                best_groups = groups
    # Determine the best split for a given dataset
    return DecisionTreeNode(feature_index=best_index, threshold=best_value, left=best_groups[0], right=best_groups[1])

def to_terminal(group):
    outcomes = []
    for row in group:
        outcomes.append(row[-1])
    # Determine the most common outcome
    return max(set(outcomes), key=outcomes.count)

def split(node, max_depth, min_size, depth, n_features):
    # node is the current node in the decision tree
    # max_depth prevents the tree from growing too deep, to avoid overfitting
    # min_size is the minimum size of a group at a node
    # depth is the current depth of the tree
    # n_features is the number of features to consider
    # Extract the 2 groups from the current node
    left = node.left
    right = node.right
    # If either the left or right group is empty after a split, no meaningful split could be made
    if not left or not right:
        node.left = to_terminal(left + right)
        node.right = to_terminal(left + right)
        return
    # Check if the current depth of the tree has reached the maximum allowed depth
    if depth >= max_depth:
        # Both are set to the same terminal node
        node.left = to_terminal(left)
        node.right = to_terminal(right)
        return
    # Check if the size of the left group is less than or equal to the minimum size
    if len(left) <= min_size:
        node.left = to_terminal(left)
    else:
        # Find the best split of the left group
        node.left = get_best_split(left, n_features)
        # Recursively call split on the resulting node, increasing the depth by 1
        split(node.left, max_depth, min_size, depth + 1, n_features)
    # So split methodically splits the data, building up a tree structure that will be used for predictive modelling
    if len(right) <= min_size:
        node.right = to_terminal(right)
    else:
        node.right = get_best_split(right, n_features)
        split(node.right, max_depth, min_size, depth + 1, n_features)

def build_decision_tree(train, max_depth, min_size, n_features):
    root = get_best_split(train, n_features)
    # Depth is 1 to start the split from the root
    split(root, max_depth, min_size, 1, n_features)
    # Return the decision tree root
    return root

def predict(node, row):
    # node is the current node in the decision tree
    # row is a single data point from the tesing dataset
    # Check if it is a leaf
    if not isinstance(node, DecisionTreeNode):
        return node
    # Check if the value of the input data is less than the threshold value 
    if row[node.feature_index] < node.threshold:
        # Traverse down until we reach a leaf
        return predict(node.left, row)
    else:
        # So predict classifies a new data point by traversing the decision tree until it reaches a leaf, at which point it returns the class label associated with that leaf node
        return predict(node.right, row)

def subsample(dataset, ratio):
    # ratio is the proportion of the dataset to include in the sample
    sample = []
    n_sample = round(len(dataset) * ratio)
    while len(sample) < n_sample:
        index = np.random.randint(len(dataset))
        sample.append(dataset[index])
    # Create a random subset of the original dataset, for training each decision tree within the Random Forest (bootstrap sample)
    return sample

def bagging_predict(trees, row):
    predictions = []
    for tree in trees:
        predictions.append(predict(tree, row))
    # Return the most common prediction among all the trees' predictions
    return max(set(predictions), key=predictions.count)

def random_forest(train, max_depth, min_size, sample_size, n_trees, n_features, n_jobs):
    # train is the training dataset
    # max_depth is the maximum depth of the trees
    # min_size is the minimum number of samples required to split an internal node
    # sample_size is the proportion of the dataset to include in each bootstrap sample
    # n_trees is the number of trees in the forest
    # n_features is the number of features to consider when looking for the best split
    # n_jobs is the number of jobs to run in parallel
    trees = []
    samples = []
    for i in range(n_trees):
        # Create n_trees samples and append them to the samples list
        samples.append(subsample(train, sample_size))
    # Use parallel execution for more efficiency (speed up)
    with ProcessPoolExecutor(max_workers=n_jobs) as executor:
        futures = []
        for sample in samples:
            # Submit the build_decision_tree function for asynchronous execution and append to the futures list
            futures.append(executor.submit(build_decision_tree, sample, max_depth, min_size, n_features))
        # Wait for each task to complete
        for future in concurrent.futures.as_completed(futures):
            # The resulting decision tree is appended to the trees list
            trees.append(future.result())
    # Return the list of decision trees
    return trees
