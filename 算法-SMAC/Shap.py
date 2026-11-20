import xgboost as xgb
import shap
import csv
import pandas as pd
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# shap.initjs()

df = pd.read_csv("record.csv", sep=",")
X = df.iloc[:, :-1]  # 特征
y = df.iloc[:, -1]   # 目标变量
print(y[9])