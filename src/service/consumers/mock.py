from pathlib import Path

import pandas as pd
import os

from . import DataConsumer


class MockDataConsumer(DataConsumer):

    def __init__(self):
        self._df = pd.read_csv(os.path.dirname(__file__) + "/data/income-biased.csv", index_col=False)

    def as_dataframe(self):
        return self._df