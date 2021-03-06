"""
Study model
"""
import pickle
import pandas as pd
import xgboost as xgb
import numpy as np
# from matplotlib import pyplot

from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from tpot import TPOTClassifier


class Model(object):
    def __init__(self):
        self.train_data = self.load('pickle/train_data_set.pkl')
        self.train_answer = self.load('pickle/train_answer.pkl')
        self.test_data = [test_id for test_id in pd.read_csv("data/test.csv", sep=',')['bidder_id']]
        self.mapper = None
        self.feature_engineering_column = None
        self.poly = None
        self.model = None
        self.n_comp = 3
        self.pca = None
        self.t_svd = None

    @staticmethod
    def load(pickle_name):
        with open(pickle_name, 'rb') as data_file:
            data = pickle.load(data_file)
        return data

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

            # tSVD
            # self.t_svd = KernelPCA(n_components=self.n_comp, random_state=420)
            # t_svd_results_train = self.t_svd.fit_transform((np.nan_to_num(data)))

            data = pd.DataFrame(data)

            for i in range(1, self.n_comp + 1):
                data['pca_' + str(i)] = pca_results_train[:, i - 1]
                # data['t_svd_' + str(i)] = t_svd_results_train[:, i - 1]
        else:

            pca_results_test = self.pca.transform(np.nan_to_num(data))

            # t_svd_results_test = self.t_svd.transform(np.nan_to_num(data))

            data = pd.DataFrame(data)

            for i in range(1, self.n_comp + 1):
                data['pca_' + str(i)] = pca_results_test[:, i - 1]
                # data['t_svd_' + str(i)] = t_svd_results_test[:, i - 1]

        return data

    @staticmethod
    def feature_selection(data):
        """
        This list has been build by analysis of xgb features importance
        """
        return data[
            [8395, 1, 8404, 4358, 'pca_1', 8385, 6894, 2, 8387, 8393, 4360, 0, 3689, 'pca_2', 4251, 2797, 8392, 4025, 3690,
             6891, 3, 8389, 8390, 8391, 4255, 8384, 3691, 8405, 6893, 8394, 8398, 8403, 4303, 4260, 4261, 8396, 8397,
             3151, 8400, 'pca_3', 4361, 8386, 6892, 4258, 4331, 8401, 7698, 3688, 3974, 4254, 8402, 4259, 4359, 4257,
             8388, 4300, 6571, 7710, 3938, 4352, 4060, 4253]

        ]

    def train(self):
        """
        Train the model
        """
        train = pd.DataFrame(data=self.train_data, index=self.train_answer.keys())
        answer = [int(value) for value in self.train_answer.values()]
        train = self.feature_engineering(train, answer)
        self.feature_engineering_column = train.columns.tolist()
        train = pd.DataFrame(data=train, columns=self.feature_engineering_column, index=self.train_answer.keys())
        train = self.feature_selection(train)

        self.poly = PolynomialFeatures(2)
        train = self.poly.fit_transform(np.nan_to_num(train))

        print(len(train), len(answer))

        y_mean = np.mean([int(value) for value in self.train_answer.values()])
        num_boost_rounds = 1250

        xgb_params = {
            'n_trees': 9000,
            'eta': 0.06,
            'max_depth': 5,
            'subsample': 0.89,
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'base_score': y_mean,  # base prediction = mean(target)
            'silent': 1
        }

        d_matrix_train = xgb.DMatrix(train, answer)
        self.model = xgb.train(dict(xgb_params, silent=0), d_matrix_train, num_boost_round=num_boost_rounds)

        # print(self.model.get_fscore().items())
        # xgb.plot_importance(self.model)
        # pyplot.show()

    def test(self):
        """
        Predict answer for test data
        :return: result.csv
        """
        test = pd.DataFrame(data=self.train_data, index=self.test_data)
        test = self.feature_engineering(test)
        test = pd.DataFrame(data=test, columns=self.feature_engineering_column, index=self.test_data)
        test = self.feature_selection(test)
        test = self.poly.transform(np.nan_to_num(test))
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
        train = pd.DataFrame(data=self.train_data, index=self.train_answer.keys()).values
        answer = [int(value) for value in self.train_answer.values()]

        x_train, x_test, y_train, y_test = train_test_split(
                                                    train.astype(np.float64),
                                                    answer,
                                                    train_size=0.75,
                                                    test_size=0.25
        )

        t_pot = TPOTClassifier(generations=5, population_size=50, verbosity=2)
        t_pot.fit(x_train, y_train)
        t_pot.export('tpot_model/tpot_pipeline.py')
