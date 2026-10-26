
from pathlib import Path
import pandas as pd

# 1. Đọc dữ liệu
BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "ncr_ride_bookings.csv")

# 2. Chuẩn hóa dữ liệu
df["Booking Status"] = df["Booking Status"].str.strip()
df["Booking Value"] = pd.to_numeric(
    df["Booking Value"], errors="coerce"
)
df["Hour"] = pd.to_datetime(
    df["Time"], format="%H:%M:%S", errors="coerce"
).dt.hour

# 3. Kiểm định KPI cơ bản
total_bookings = len(df)
unique_bookings = df["Booking ID"].nunique()

completed = df["Booking Status"].eq("Completed")
completed_bookings = int(completed.sum())

completion_rate = completed_bookings / total_bookings * 100

revenue = df.loc[completed, "Booking Value"].sum()
aov = revenue / completed_bookings

# 4. Kiểm định Peak Hour
hourly = df.groupby("Hour").size()
peak_hour = int(hourly.idxmax())
peak_bookings = int(hourly.max())

peak_17_19 = df["Hour"].between(17, 19).sum()
peak_share = peak_17_19 / total_bookings * 100


# Kiểm định Revenue at Risk
driver_cancels = df["Booking Status"].eq(
    "Cancelled by Driver"
).sum()

customer_cancels = df["Booking Status"].eq(
    "Cancelled by Customer"
).sum()

no_driver_found = df["Booking Status"].eq(
    "No Driver Found"
).sum()

revenue_at_risk = (
    driver_cancels + customer_cancels + no_driver_found
) * aov

# Kiểm định Avg VTAT
df["Avg VTAT"] = pd.to_numeric(
    df["Avg VTAT"], errors="coerce"
)

avg_vtat = df["Avg VTAT"].mean()

print("\n===== ADDITIONAL KPI VALIDATION =====")
print(f"Revenue at Risk: {revenue_at_risk:,.2f}")
print(f"Avg VTAT: {avg_vtat:.2f}")
print(f"Valid VTAT Records: {df['Avg VTAT'].count()}")


# Kiểm định Weekend Uplift
df["Date"] = pd.to_datetime(
    df["Date"], errors="coerce"
)

# Thứ Hai = 0, Chủ Nhật = 6
df["IsWeekend"] = df["Date"].dt.dayofweek >= 5

daily_bookings = (
    df.groupby(["Date", "IsWeekend"])
      .size()
      .reset_index(name="Bookings")
)

avg_weekend = daily_bookings.loc[
    daily_bookings["IsWeekend"], "Bookings"
].mean()

avg_weekday = daily_bookings.loc[
    ~daily_bookings["IsWeekend"], "Bookings"
].mean()

weekend_uplift = (avg_weekend / avg_weekday - 1) * 100

print("\n===== WEEKEND VALIDATION =====")
print(f"Avg Weekend Day: {avg_weekend:.4f}")
print(f"Avg Weekday: {avg_weekday:.4f}")
print(f"Weekend Uplift: {weekend_uplift:.2f}%")



# 5. Xuất kết quả
results = {
    "Total Bookings (COUNTROWS)": total_bookings,
    "Unique Booking IDs": unique_bookings,
    "Completed Bookings": completed_bookings,
    "Completion Rate (%)": round(completion_rate, 2),
    "Completed Revenue": round(revenue, 2),
    "AOV Completed": round(aov, 2),
    "Peak Hour": peak_hour,
    "Peak Hour Bookings": peak_bookings,
    "Peak Share 17-19 (%)": round(peak_share, 2),
    "Revenue at Risk": round(revenue_at_risk, 2),
    "Avg VTAT": round(avg_vtat, 2),
    "Weekend Uplift (%)": round(weekend_uplift, 2)
}

print("\n===== KPI VALIDATION =====")
for name, value in results.items():
    print(f"{name}: {value}")

# 6. Lưu kết quả ra CSV
output_dir = BASE_DIR / "validation_results"
output_dir.mkdir(exist_ok=True)

pd.DataFrame(
    list(results.items()),
    columns=["KPI", "Python Value"]
).to_csv(output_dir / "kpi_validation.csv", index=False)

hourly.rename("Bookings").to_csv(
    output_dir / "hourly_bookings.csv"
)

print("\nĐã lưu kết quả vào validation_results/")
