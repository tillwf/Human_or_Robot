"""
Study model
"""
import pickle
import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.decomposition import PCA
from tpot import TPOTClassifier
from sklearn.model_selection import train_test_split


class Model(object):
    def __init__(self):
        self.train_data = self.load('pickle/train_data_set.pkl')
        self.train_answer = self.load('pickle/train_answer.pkl')
        self.test_data = [test_id for test_id in pd.read_csv("data/test.csv", sep=',')['bidder_id']]
        self.model = None
        self.n_comp = 3
        self.pca = None

    @staticmethod
    def load(pickle_name):
        with open(pickle_name, 'rb') as data_file:
            data = pickle.load(data_file)
        return data

    def return_statistical_data(self):
        """
        Return numerical data
        """
        return self.train_data[[
                    'nb_unique_ip', 'low_freq_ip', 'high_freq_ip', 'std_freq_ip',
                    'nb_unique_device', 'low_freq_device', 'high_freq_device', 'std_freq_device',
                    'nb_unique_merchandise', 'low_freq_merchandise', 'high_freq_merchandise', 'std_freq_merchandise',
                    'nb_unique_country', 'low_freq_country', 'high_freq_country', 'std_freq_country',
                    'nb_unique_url', 'low_freq_url', 'high_freq_url', 'std_freq_url',
                    'nb_unique_auction', 'low_freq_auction', 'high_freq_auction', 'std_freq_auction',
                    "bid_nb", "min_time", "max_time", "range_time", "min_time_interval",
                    "max_time_interval", "mean_time_interval", "std_time_interval", "time_interval_25",
                    "time_interval_50", "time_interval_75", "mean_of_auction_bid_nb", "std_of_auction_bid_nb",
                    "mean_of_auction_range_time", "std_of_auction_range_time",
                    "min_of_auction_min_time_interval", "mean_of_auction_min_time_interval",
                    "max_auction_max_time_interval", "mean_auction_max_time_interval",
                    "mean_auction_mean_time_interval", "std_auction_mean_time_interval",
                    "mean_auction_std_time_interval"
                    ]]

    def feature_engineering(self, data, answer=None):
        """
        Feature engineering for data (PCA, etc...)
        :param data: Data to fit_transform
        :param answer: Answer series for data
        :return: Data with new features
        """
        if answer:
            # PCA
            self.pca = PCA(n_components=self.n_comp, random_state=420)
            self.pca.fit(np.nan_to_num(data), answer)
            pca_results_train = self.pca.transform(np.nan_to_num(data))
            data = pd.DataFrame(data)

            for i in range(1, self.n_comp + 1):
                data['pca_' + str(i)] = pca_results_train[:, i - 1]
        else:
            pca2_results_test = self.pca.transform(np.nan_to_num(data))
            data = pd.DataFrame(data)
            for i in range(1, self.n_comp + 1):
                data['pca_' + str(i)] = pca2_results_test[:, i - 1]

        return data

    def train(self):
        """
        Train the model
        """
        train = pd.DataFrame(data=self.return_statistical_data(), index=self.train_answer.keys()).values
        answer = [int(value) for value in self.train_answer.values()]
        train = self.feature_engineering(train, answer)

        y_mean = np.mean([int(value) for value in self.train_answer.values()])
        num_boost_rounds = 1250

        xgb_params = {
            'n_trees': 10000,
            'eta': 0.05,
            'max_depth': 5,
            'subsample': 0.90,
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'base_score': y_mean,  # base prediction = mean(target)
            'silent': 1
        }

        d_matrix_train = xgb.DMatrix(train, answer)
        self.model = xgb.train(dict(xgb_params, silent=0), d_matrix_train, num_boost_round=num_boost_rounds)

    def test(self):
        """
        Predict answer for test data
        :return: result.csv
        """
        test = pd.DataFrame(data=self.return_statistical_data(), index=self.test_data).values
        test = self.feature_engineering(test)

        d_matrix_test = xgb.DMatrix(test)
        y_predicted = self.model.predict(d_matrix_test)

        test_answer = pd.concat([pd.DataFrame(self.test_data), pd.DataFrame(y_predicted)], ignore_index=True, axis=1)
        final_result = pd.DataFrame(test_answer)
        final_result.to_csv('result/result.csv', index=False)

    def tpot_search(self):
        """
        Search model with TPOT
        :return: tpot_pipeline.py
        """
        train = pd.DataFrame(data=self.return_statistical_data(), index=self.train_answer.keys()).values
        answer = [np.float64(value) for value in self.train_answer.values()]

        x_train, x_test, y_train, y_test = train_test_split(
                                                    train.astype(np.float64),
                                                    answer,
                                                    train_size=0.75,
                                                    test_size=0.25
        )

        tpot = TPOTClassifier(generations=5, population_size=50, verbosity=2)
        tpot.fit(x_train, y_train)
        tpot.export('tpot_model/tpot_pipeline.py')
