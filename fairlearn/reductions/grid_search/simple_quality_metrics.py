# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import copy
import pandas as pd

from fairlearn.reductions.grid_search import QualityMetric

from fairlearn.reductions.moments import DemographicParity, MisclassificationError


class SimpleClassificationQualityMetric(QualityMetric):
    """Class to calculate a metric for comparing models produced
    by GridSearch
    The metric produced is simply the sum of error and disparity
    for the given model
    """

    def __init__(self):
        self.error_metric = MisclassificationError()
        self.disparity_metric = DemographicParity()

    def set_data(self, X, Y, bin_id):
        self.X = X
        self.Y = Y
        self.bin_id = bin_id

        self.error_metric.load_data(X, pd.Series(Y), sensitive_features=bin_id)
        self.disparity_metric.load_data(X, pd.Series(Y), sensitive_features=bin_id)

    def get_quality(self, model):
        current_error_metric = copy.deepcopy(self.error_metric)
        current_disparity_metric = copy.deepcopy(self.disparity_metric)

        def classifier(X): return model.predict(X)
        current_error = current_error_metric.gamma(classifier)[0]
        current_disparity = current_disparity_metric.gamma(classifier).max()

        return -(current_error+current_disparity)


class SimpleRegressionQualityMetric(QualityMetric):
    """Simple class to produce a quality metric for regression models
    produced by GridSearch, to enable one to be selected for the
    predict methods
    """

    def set_data(self, X, Y, bin_id):
        self.X = X
        self.Y = Y
        self.bin_id = bin_id

    def get_quality(self, model):
        labels = pd.Series(self.Y)
        preds = pd.Series(model.predict(self.X))
        attrs = pd.Series(self.bin_id)
        attr_vals = attrs.unique()
        errors = (preds-labels)**2
        error = errors.mean()
        error0 = errors[attrs == attr_vals[0]].mean()
        error1 = errors[attrs == attr_vals[1]].mean()
        return -(error+max(error0, error1))
