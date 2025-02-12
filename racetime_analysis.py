import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")

df = pd.read_csv("./OUTPUT/CONVERTED/raceInfo_2020_to_2025_formatted.csv")
print(df)

# ダートコースの抽出（"ダ"を含む行）
df_dirt = df[df['Course'].str.contains('ダ', na=False)].copy()
df_dirt['Distance'] = df_dirt['Course'].str.extract(r'(\d+)m').astype(float)
print(df_dirt)

# 芝コースの抽出（"芝"を含む行）
df_grass = df[df['Course'].str.contains('芝', na=False)].copy()
df_grass['Distance'] = df_grass['Course'].str.extract(r'(\d+)m').astype(float)
print(df_grass)

# オプション: 分類結果の確認
print(f"ダートコース件数: {len(df_dirt)}")
print(f"芝コース件数: {len(df_grass)}")

df_dirt.plot(y="Time", x="Distance", kind="scatter")
plt.show()