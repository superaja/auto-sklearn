import numpy as np

from HPOlibConfigSpace.configuration_space import ConfigurationSpace
from HPOlibConfigSpace.hyperparameters import UniformFloatHyperparameter, \
    UniformIntegerHyperparameter, CategoricalHyperparameter, \
    UnParametrizedHyperparameter, Constant

from ParamSklearn.components.base import \
    ParamSklearnRegressionAlgorithm
from ParamSklearn.util import DENSE, PREDICTIONS, SPARSE
# get our own forests to replace the sklearn ones
from sklearn.tree import DecisionTreeRegressor


class DecisionTree(ParamSklearnRegressionAlgorithm):
    def __init__(self, criterion, splitter, max_features, max_depth,
                 min_samples_split, min_samples_leaf, min_weight_fraction_leaf,
                 max_leaf_nodes, random_state=None):
        self.criterion = criterion
        self.splitter = splitter
        self.max_features = max_features
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_leaf_nodes = max_leaf_nodes
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.random_state = random_state
        self.estimator = None

    def fit(self, X, y, sample_weight=None):
        self.max_features = float(self.max_features)
        if self.max_depth == "None":
            self.max_depth = None
        else:
            num_features = X.shape[1]
            max_depth = max(1, int(np.round(self.max_depth * num_features, 0)))
        self.min_samples_split = int(self.min_samples_split)
        self.min_samples_leaf = int(self.min_samples_leaf)
        if self.max_leaf_nodes == "None":
            self.max_leaf_nodes = None
        else:
            self.max_leaf_nodes = int(self.max_leaf_nodes)
        self.min_weight_fraction_leaf = float(self.min_weight_fraction_leaf)

        self.estimator = DecisionTreeRegressor(
            criterion=self.criterion,
            max_depth=max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            max_leaf_nodes=self.max_leaf_nodes,
            random_state=self.random_state)
        self.estimator.fit(X, y, sample_weight=sample_weight)
        return self

    def predict(self, X):
        if self.estimator is None:
            raise NotImplementedError
        return self.estimator.predict(X)

    @staticmethod
    def get_properties():
        return {'shortname': 'DT',
                'name': 'Decision Tree Classifier',
                'handles_missing_values': False,
                'handles_nominal_values': False,
                'handles_numerical_features': True,
                'prefers_data_scaled': False,
                # TODO find out if this is good because of sparcity...
                'prefers_data_normalized': False,
                'handles_regression': True,
                'handles_classification': False,
                'handles_multiclass': False,
                'handles_multilabel': False,
                'is_deterministic': False,
                'handles_sparse': True,
                'input': (DENSE, SPARSE),
                'output': PREDICTIONS,
                # TODO find out what is best used here!
                # But rather fortran or C-contiguous?
                'preferred_dtype': np.float32}

    @staticmethod
    def get_hyperparameter_search_space(dataset_properties=None):
        cs = ConfigurationSpace()

        criterion = cs.add_hyperparameter(Constant('criterion', 'mse'))
        splitter = cs.add_hyperparameter(Constant("splitter", "best"))
        max_features = cs.add_hyperparameter(Constant('max_features', 1.0))
        max_depth = cs.add_hyperparameter(UniformFloatHyperparameter(
            'max_depth', 0., 2., default=0.5))
        min_samples_split = cs.add_hyperparameter(UniformIntegerHyperparameter(
            "min_samples_split", 2, 20, default=2))
        min_samples_leaf = cs.add_hyperparameter(UniformIntegerHyperparameter(
            "min_samples_leaf", 1, 20, default=1))
        min_weight_fraction_leaf = cs.add_hyperparameter(
            Constant("min_weight_fraction_leaf", 0.0))
        max_leaf_nodes = cs.add_hyperparameter(
            UnParametrizedHyperparameter("max_leaf_nodes", "None"))

        return cs
