from typing import Dict
from typing import List

import numpy as np
import pandas as pd
from IPython.display import display


class Dataset:
    """Dataset that contains features, labels, meta data and scalers.

    Attributes:
        X (Dict of np.ndarray and/or pd.DataFrame): features
        Y (pd.DataFrame): labels
        Z (pd.DataFrame): description/meta data
        df (DataFrame): labels and meta data
        x_cols (Dict of str: List[str]): feature names
        y_cols (List[str]): label names
        z_cols (List[str]): meta data names
        n_records (int): number of records in dataset
        n_X (int): number of X array(s)
        X_dim (List[Tuple[int]): dimension(s) of X array(s) with n_records removed
    """
    def __init__(
        self,
        X: Dict[str, np.array],
        Y: pd.DataFrame,
        Z: pd.DataFrame,
        x_cols: Dict[str, List[str]],
        scalers: Dict = None,
        # scaler_team=None,
        # scaler_player=None,
        # scaler_y=None,
        train_val_test_idx: list = None,
    ):

        self.X = X
        self.n_X = len(X.keys())
        self.X_dim = [arr.shape[1:] for name, arr in X.items()]

        # confirm all X has same number of records
        assert len(set([arr.shape[0] for name, arr in X.items()])) == 1

        self.n_records = Y.shape[0]

        self.x_cols = x_cols
        self.y_cols = Y.columns
        self.z_cols = Z.columns

        self.Y = Y
        self.Z = Z
        self.df = pd.merge(
            Z, Y, left_index=True, right_index=True, validate='1:1'
        )

        self.scalers = scalers
        # self.scaler_team = scaler_team
        # self.scaler_player = scaler_player
        # self.scaler_y = scaler_y

        self.train_val_test_idx = train_val_test_idx
        self.x_train = None
        self.y_train = None
        self.df_train = None
        self.x_val = None
        self.y_val = None
        self.df_val = None
        self.x_test = None
        self.y_test = None
        self.df_test = None

        # self.team_size = int(self.X_dim[0][-2] / 2)

    def peek(self, n: int = None):
        """Previews the n-th record of the dataset in IPython."""
        if n is None:
            n = np.random.randint(self.n_records)

        print(f'Peeks the {n}-th record among {self.n_records} records.')

        print('Z / meta data:')
        display(self.Z.iloc[n].to_frame().T)

        print('Y / labels:')
        display(self.Y.iloc[n].to_frame().T)

        for name, arr in self.X.items():

            print(f'X_{name} has shape{arr.shape}')

            # 2D - tabular data: print a row
            if len(arr.shape) == 2:
                print(f'X_{name}[{n}, :] is')
                display(
                    pd.DataFrame(
                        np.reshape(arr[n], (1, -1)), columns=self.x_cols[name]
                    )
                )

            # 3D - input for RNN: print rows, a matrix of time series
            elif len(arr.shape) == 3:
                print(f'X_{name}[{n}, :, :] is')
                display(pd.DataFrame(arr[n], columns=self.x_cols[name]))

            # 4D/5D - input for ConvLSTM2D: print first slice of the record, which will be one of the time series
            elif len(arr.shape) == 4:
                max_dim = arr.shape[-2]
                idx = np.random.randint(0, max_dim)
                print(f'X_{name}[{n}, :, {idx}, :] is')
                display(
                    pd.DataFrame(arr[n, :, idx, :], columns=self.x_cols[name])
                )

            else:
                print(f'failed to print X_{name} with shape {arr.shape}')

        return None

    def split_train_val_test_set(self):
        labels = list(self.Y.columns)
        idx_train, idx_val, idx_test = self.train_val_test_idx

        self.x_train = {k: v[idx_train] for k, v in self.X.items()}
        self.x_val = {k: v[idx_val] for k, v in self.X.items()}
        self.x_test = {k: v[idx_test] for k, v in self.X.items()}

        self.df_train = self.df.loc[idx_train]
        self.df_val = self.df.loc[idx_val]
        self.df_test = self.df.loc[idx_test]

        self.y_train = self.df_train[labels]
        self.y_val = self.df_val[labels]
        self.y_test = self.df_test[labels]
        n_train = self.df_train.shape[0]
        n_val = self.df_val.shape[0]
        n_test = self.df_test.shape[0]
        n_total = self.df.shape[0]

        print(
            f'train/validation/test set have ratios: '
            f'{n_train / n_total:.2%}/{n_val / n_total:.2%}/{n_test / n_total:.2%}'
        )
        print(
            f'train/validation/test set have size: {n_train}/{n_val}/{n_test}'
        )
        #print(self.df.columns)

        print(
            f"""
            training set has {n_train} records from {self.df_train['start_datetime'].min()} to {self.df_train['start_datetime'].max()}
            validation set has {n_val} records from {self.df_val['start_datetime'].min()} to {self.df_val['start_datetime'].max()}
            testing set has {n_test} records from {self.df_test['start_datetime'].min()} to {self.df_test['start_datetime'].max()}
        """
        )
