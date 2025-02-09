import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import xgboost as xgb

# データの読み込み
input_rawdata_path = './OUTPUT/CONVERTED/raceInfo_2020_to_2025_labelEncoded.csv'
df = pd.read_csv(input_rawdata_path)

# 目的変数の設定
df["Top3"] = df["Top3"].astype(int)

# オッズのlog変換
df["Log_Odds"] = np.log1p(df["Odds"])

# 特徴量の再定義（リーク要因を排除）
feature_columns = [
    "Waku", "Num", "Weight_for_Age", "Jockey", "Popularity",
    "Log_Odds", "Stable", "Horse_Weight", "Race_Month",
    "Racetime_Class", "Horse_Sex", "Horse_Old", "Course_Status",
    "Weather", "Course"
]

# 不要なカラムの削除（Race_Idと日付関連を削除）
drop_columns = ["Horse_Name", "Time", "Race_Date", "Race_Time", "Result_Num", "Race_Id"]
df = df.drop(columns=drop_columns)

# 時系列を考慮した分割（年別分割などが望ましいが、ここでは簡易的に）
# 元のデータが時系列順に並んでいることを前提に80-20分割
train_size = int(len(df) * 0.9)
train = df.iloc[:train_size]
# test = df.iloc[train_size:]

input_testdata_path = './OUTPUT/CONVERTED/test.csv'
df_test = pd.read_csv(input_testdata_path)
df_test["Top3"] = df_test["Top3"].astype(int)
df_test["Log_Odds"] = np.log1p(df_test["Odds"])
df_test = df_test.drop(columns=drop_columns)
test = df_test

# 特徴量と目的変数の分割
X_train = train[feature_columns]
y_train = train["Top3"]
X_test = test[feature_columns]
y_test = test["Top3"]

# XGBoostのデータセット作成
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# パラメータ調整（過学習防止策を追加）
params = {
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "learning_rate": 0.05,
    "max_depth": 4,  # 深さを制限
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "seed": 42,
    "scale_pos_weight": len(y_train[y_train==0])/len(y_train[y_train==1])  # クラス不均衡対策
}

# 学習
num_round = 100
watchlist = [(dtrain, "train"), (dtest, "eval")]
model = xgb.train(params, dtrain, num_round, evals=watchlist, early_stopping_rounds=20)

# 予測と評価
y_pred = model.predict(dtest)
y_pred_class = (y_pred > 0.5).astype(int)

from sklearn.metrics import accuracy_score, confusion_matrix
acc = accuracy_score(y_test, y_pred_class)
cm = confusion_matrix(y_test, y_pred_class)

print(f"Accuracy: {acc:.4f}")
print("Confusion Matrix:")
print(cm)