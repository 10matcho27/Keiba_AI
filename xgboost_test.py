import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

### LOAD DATA ###
input_rawdata_path = './OUTPUT/CONVERTED/raceInfo_2020_to_2025_labelEncoded.csv'
df = pd.read_csv(input_rawdata_path)

### FORMATTING DATA ###
df["Top3"] = df["Top3"].astype(int)
df["Log_Odds"] = np.log1p(df["Odds"])

feature_columns = [
    "Horse_Name",
    "Waku",
    "Num",
    "Weight_for_Age",
    "Jockey",
    # "Popularity",
    "Log_Odds",
    "Stable",
    "Horse_Weight",
    "Race_Month",
    "Racetime_Class",
    "Horse_Sex",
    "Horse_Old",
    "Course_Status",
    "Weather",
    "Course"
]
drop_columns = [
    # "Horse_Name",
    "Popularity",
    "Time",
    "Race_Date",
    "Race_Time",
    "Result_Num",
    "Race_Id"
    ]
df = df.drop(columns=drop_columns)

### SPLIT DATA to TARGET AND FEATURE VALUABLES
X = df[feature_columns] 
y = df["Top3"]

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.2, 
                                                    random_state=0, 
                                                    stratify=y)
X_train, X_eval, y_train, y_eval = train_test_split(X_train, y_train,
                                                    test_size=0.2,
                                                    random_state=1,
                                                    stratify=y_train)

print(df)
print('X.shape = {}'.format(X.shape))
print('y.shape = {}'.format(y.shape))
print('X_train.shape = {}'.format(X_train.shape))
print('y_train.shape = {}'.format(y_train.shape))
print('X_test.shape = {}'.format(X_test.shape))
print('y_test.shape = {}'.format(y_test.shape))

# XGBoostのデータセット作成
dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_columns)
deval = xgb.DMatrix(X_eval, label=y_eval, feature_names=feature_columns)
dtest = xgb.DMatrix(X_test, label=y_test, feature_names=feature_columns)

# パラメータ調整（過学習防止策を追加）
num_round = 50000
params = {
    "device": "cuda",
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "booster": "gbtree",
    # "learning_rate": 0.05,
    "eta": "0.005",
    "max_depth": 8,  # 深さを制限
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "seed": 42,
    "scale_pos_weight": len(y_train[y_train==0])/len(y_train[y_train==1])  # クラス不均衡対策
}
# 学習
watchlist = [(dtrain, "train"), (deval, "eval")]
evaluation_results = {}  
model = xgb.train(params,
                dtrain=dtrain,
                evals=watchlist,
                evals_result=evaluation_results,
                early_stopping_rounds=30,
                verbose_eval=10,
                num_boost_round=num_round
                )

# 予測と評価
y_pred = model.predict(dtest)
print(y_pred)
y_pred_class = (y_pred > 0.6).astype(int)
print(y_pred_class)


acc = accuracy_score(y_test, y_pred_class)
cm = confusion_matrix(y_test, y_pred_class)

df_accuracy = pd.DataFrame({'va_y': y_test,
                            'y_pred_max': y_pred_class})
pd.crosstab(df_accuracy['va_y'], df_accuracy['y_pred_max'])

print(f"Accuracy: {acc:.4f}")
print("Confusion Matrix:")
print(cm)
print(df_accuracy)

xgb.plot_importance(model)
plt.show()


# 学習過程の可視化
plt.plot(evaluation_results['train']['logloss'], label='train')
plt.plot(evaluation_results['eval']['logloss'], label='eval')
plt.ylabel('Log loss')
plt.xlabel('Boosting round')
plt.title('Training performance')
plt.legend()
plt.show()