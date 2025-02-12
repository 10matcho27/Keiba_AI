import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, f1_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import matplotlib
import matplotlib.pyplot as plt
import os
matplotlib.use('TkAgg')

### LOAD DATA ###
input_rawdata_path = './OUTPUT/CONVERTED/raceInfo_2020_to_2025_labelEncoded.csv'
df = pd.read_csv(input_rawdata_path)
df_initial_header = df.columns.values.tolist()
### DATA PREPROCESSING ###
df["Top3"] = df["Top3"].astype(int)
df["Log_Odds"] = np.log1p(df["Odds"])
# Feature selection
feature_columns = [
    "Horse_Name", "Waku", "Num", "Weight_for_Age", "Jockey",
    "Log_Odds", "Stable", "Horse_Weight", "Race_Month",
    "Racetime_Class", "Horse_Sex", "Horse_Old", "Course_Status",
    "Weather", "Course"
]
categorical_columns = [
    "Horse_Name", "Waku", "Num", "Jockey", "Stable", "Horse_Sex",
    "Course_Status", "Weather", "Course", "Race_Month", "Racetime_Class", "Horse_Old"
]
numerical_columns = feature_columns - categorical_columns
drop_columns = df_initial_header + ["Log_Odds"] - feature_columns - ["Top3"]
df.drop(columns=drop_columns, inplace=True)

# Feature and target split
X = df[feature_columns]
y = df["Top3"]

# Feature scaling
scaler = StandardScaler()
df[numerical_columns] = scaler.fit_transform(df[numerical_columns])
X_cat = pd.DataFrame()
for col in categorical_columns:
    X_cat[col] = X[col].astype('category')

X = pd.concat([df[numerical_columns], X_cat], axis=1)

print(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train, X_eval, y_train, y_eval = train_test_split(X_train, y_train, test_size=0.2, random_state=42, stratify=y_train)

# XGBoost dataset creation
dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_columns, enable_categorical=True)
deval = xgb.DMatrix(X_eval, label=y_eval, feature_names=feature_columns, enable_categorical=True)
dtest = xgb.DMatrix(X_test, label=y_test, feature_names=feature_columns, enable_categorical=True)

### HYPERPARAMETER TUNING ###
param_grid = {
    'max_depth': [4, 6, 8],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.7, 0.8, 0.9],
    'colsample_bytree': [0.7, 0.8, 0.9],
}

xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', enable_categorical=True)
grid_search = GridSearchCV(estimator=xgb_clf, param_grid=param_grid, scoring='roc_auc', cv=3, verbose=1)
grid_search.fit(X_train, y_train)
grid_serch_result_path = './OUTPUT/GRID_SEARCH/'
os.makedirs(grid_serch_result_path, exist_ok=True)
pd.DataFrame.from_dict(grid_search.cv_results_).to_csv(grid_serch_result_path + 'gs_results.csv')

print(f"Best Parameters: {grid_search.best_params_}")
# Best Parameters: {'colsample_bytree': 0.8, 'learning_rate': 0.01, 'max_depth': 4, 'subsample': 0.8}

### MODEL TRAINING WITH BEST PARAMETERS ###
params = grid_search.best_params_
params.update({"device": "cuda", "seed": 42})

watchlist = [(dtrain, "train"), (deval, "eval")]
evaluation_results = {}

model = xgb.train(
    params,
    dtrain=dtrain,
    evals=watchlist,
    evals_result=evaluation_results,
    early_stopping_rounds=30,
    verbose_eval=10,  # 10ブーストごとに学習過程を表示
    num_boost_round=1000
)

### EVALUATION ###
y_pred_prob = model.predict(dtest)
y_pred_class = (y_pred_prob > 0.4).astype(int)

accuracy = accuracy_score(y_test, y_pred_class)
roc_auc = roc_auc_score(y_test, y_pred_prob)
f1 = f1_score(y_test, y_pred_class)

print(f"Accuracy: {accuracy:.4f}")
print(f"ROC-AUC: {roc_auc:.4f}")
print(f"F1 Score: {f1:.4f}")

cm = confusion_matrix(y_test, y_pred_class)
print("Confusion Matrix:\n", cm)

### FEATURE IMPORTANCE ###
xgb.plot_importance(model, max_num_features=10, importance_type='gain', title='Top 10 Feature Importances')
plt.show()

### TRAINING PERFORMANCE VISUALIZATION ###
plt.figure(figsize=(10, 5))
plt.plot(evaluation_results['train']['rmse'], label='Train Log Loss')
plt.plot(evaluation_results['eval']['rmse'], label='Validation Log Loss')
plt.xlabel('Boosting Rounds')
plt.ylabel('Log Loss')
plt.title('Training and Validation Log Loss over Boosting Rounds')
plt.legend()
plt.show()
