import pandas as pd, numpy as np
from scipy import stats

df = pd.read_csv("ncr_ride_bookings.csv", na_values=["null"])

def bh(p):                                  # Benjamini-Hochberg (FDR)
    p = np.asarray(p); n = len(p); o = np.argsort(p); r = np.empty(n)
    adj = p[o] * n / (np.arange(n) + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    r[o] = np.minimum(adj, 1); return r

metrics = {"No Driver Found": "No-Driver Rate",
           "Cancelled by Driver": "Driver Cancel Rate",
           "Cancelled by Customer": "Customer Cancel Rate"}
rows = []
n_loc = df.groupby("Pickup Location").size()
for status, name in metrics.items():
    p0 = (df["Booking Status"] == status).mean()
    k = df[df["Booking Status"] == status].groupby("Pickup Location").size().reindex(n_loc.index).fillna(0)
    rate = k / n_loc
    z = (rate - p0) / np.sqrt(p0 * (1 - p0) / n_loc)
    pv = 2 * (1 - stats.norm.cdf(np.abs(z.values)))
    t = pd.DataFrame({"location": n_loc.index, "metric": name, "n": n_loc.values,
                      "rate": rate.values, "z": z.values, "p": pv})
    t["p_bonferroni"] = np.minimum(t["p"] * len(t), 1)
    t["p_fdr"] = bh(t["p"].values)
    rows.append(t)
res = pd.concat(rows)
res.to_csv("funnel_pickup.csv", index=False)