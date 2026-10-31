import pandas as pd, numpy as np
from scipy import stats

df = pd.read_csv("ncr_ride_bookings.csv", na_values=["null"])
df["Date"] = pd.to_datetime(df["Date"])
df["Hour"] = pd.to_datetime(df["Time"]).dt.hour

# 1) Tỷ lệ trạng thái có đổi theo giờ không? (chi bình phương)
p_hour = stats.chi2_contingency(pd.crosstab(df["Hour"], df["Booking Status"]))[1]

# 2) Cuối tuần có cao hơn ngày thường không? (t-test)
daily = df.groupby("Date").size()
wkend = daily[daily.index.dayofweek >= 5]
wkday = daily[daily.index.dayofweek < 5]
p_week = stats.ttest_ind(wkend, wkday)[1]

# 3) Số booking mỗi ngày có giống nhiễu ngẫu nhiên không?
sd, mean = daily.std(), daily.mean()
res = pd.DataFrame({
    "kiem_dinh": ["Gio x trang thai (chi2)", "Cuoi tuan vs ngay thuong (t-test)", "SD so booking/ngay", "Can bac hai trung binh"],
    "gia_tri":   [p_hour, p_week, sd, np.sqrt(mean)]
})
res.to_csv("stats_week3.csv", index=False)
print(res)