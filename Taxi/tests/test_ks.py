import pandas as pd

import detectors.ks

assert detectors.ks.strict_objective(pd.Series([0, 0, 1, 1, 0, 1]), pd.Series([0, 0, 1, 1, 0, 1])) == 1.0
assert detectors.ks.strict_objective(pd.Series([0, 0, 1, 1, 0, 1]), pd.Series([0, 0, 0, 1, 0, 1])) == 2/3
assert detectors.ks.strict_objective(pd.Series([0, 0, 1, 1, 0, 1]), pd.Series([1, 0, 0, 1, 0, 1])) == 0

assert detectors.ks.anomaly_objective(pd.Series([0, 0, 1, 1, 0, 1]), pd.Series([1, 0, 0, 1, 0, 1])) == 1/3
assert detectors.ks.anomaly_objective(pd.Series([0, 0, 1, 1, 0, 1]), pd.Series([1, 0, 0, 1, 0, 0])) == -1.0
assert detectors.ks.anomaly_objective(pd.Series([0, 0, 1, 1, 0, 1]), pd.Series([0, 0, 1, 1, 0, 1])) == 1.0
