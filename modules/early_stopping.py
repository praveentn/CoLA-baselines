from __future__ import print_function
import os
import numpy as np
import torch

from utils import Checkpoint


class EarlyStopping:
    """
    Provides early stopping functionality. Keeps track of model metrics,
    and if it doesn't improve over time restores last best performing
    parameters.
    """

    def __init__(self, model: torch.nn.Module, checkpoint_instance: Checkpoint,
                 patience=100, minimize=False):
        self.minimize = minimize
        self.patience = patience
        self.model = model
        self.checkpoint = checkpoint_instance
        self.best_monitored_metric = 0. if not minimize else np.inf
        self.other_metrics = {
            'acc': 0,
            'val_loss': np.inf
        }
        self.best_monitored_epoch = 0

    def __call__(self, value, other_metrics, epoch):
        """
        Method to be called everytime you need to check whether to early stop or not


        Arguments:
            value {number} -- Metric to be used for early stopping
            other_metrics {dict} -- Any other metrics that need to be tracked
            epoch {number} -- Current epoch number

        Returns:
            bool -- Tells whether early stopping occurred or not
        """
        if (self.minimize and value < self.best_monitored_metric) or \
                (not self.minimize and value > self.best_monitored_metric):
            self.best_monitored_metric = value
            self.other_metrics = other_metrics
            self.best_monitored_epoch = epoch
            self.checkpoint.save(self.model)

        elif self.best_monitored_epoch + self.patience < epoch:
            self.checkpoint.restore(self.model)
            return True

        return False

    def init_from_checkpoint(self):
        # Maybe do something later if expected
        return

    def print_info(self):
        print("Best Matthews: %.5f, Best Accuracy: %.5f, Best Loss: %.9f at epoch %d"
              % (self.best_monitored_metric,
                 self.other_metrics['acc'],
                 self.other_metrics['val_loss'],
                 self.best_monitored_epoch))
