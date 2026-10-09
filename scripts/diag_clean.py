"""Diagnose noise in an event CSV (hot pixels, edge rows, periodic flicker) and write a cleaned CSV."""
import os, argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("csv")
ap.add_argument("--ymin", type=int, default=0)       # drop events with y below this
ap.add_argument("--ymax", type=int, default=479)     # drop events with y above this
ap.add_argument("--hot", type=float, default=20.0)   # hot pixel: count > hot * median active count
ap.add_argument("--radius", type=float, default=0)   # 0 = off; else drop events farther than R px from the 1 ms median position
a = ap.parse_args()

path = os.path.expanduser(a.csv)
ev = pd.read_csv(path, header=None, names=["x", "y", "p", "t"])
print("events:", len(ev), " duration: %.1f s" % (ev.t.max() / 1e6))

cnt = np.zeros((480, 640), dtype=np.int64)
np.add.at(cnt, (ev.y.values, ev.x.values), 1)
active = cnt[cnt > 0]
thr = a.hot * np.median(active)
hot = cnt > thr
print("active pixels: %d, hot pixels (> %.0f events): %d, events in hot pixels: %.1f%%"
      % (len(active), thr, hot.sum(), 100 * cnt[hot].sum() / len(ev)))

rows = np.bincount(ev.y.values, minlength=480)
print("events in top 30 rows: %.1f%%, bottom 30 rows: %.1f%%"
      % (100 * rows[:30].sum() / len(ev), 100 * rows[-30:].sum() / len(ev)))

r = np.bincount((ev.t.values // 500).astype(int))
sp = np.abs(np.fft.rfft(r - r.mean()))
fr = np.fft.rfftfreq(len(r), 0.0005)
m = (fr > 2) & (fr < 500)
print("strongest periodic component of the whole event rate: %.1f Hz" % fr[m][np.argmax(sp[m])])

keep = (ev.y >= a.ymin) & (ev.y <= a.ymax) & ~hot[ev.y.values, ev.x.values]
if a.radius > 0:
    med = ev.groupby(ev.t.values // 1000)[["x", "y"]].transform("median")
    keep &= (np.hypot(ev.x - med.x, ev.y - med.y) <= a.radius)
clean = ev[keep]
out = os.path.splitext(path)[0] + "_clean.csv"
clean.to_csv(out, header=False, index=False)
print("kept %d of %d events (%.1f%%) -> %s" % (len(clean), len(ev), 100 * len(clean) / len(ev), out))

fig, ax = plt.subplots(1, 3, figsize=(16, 4))
ax[0].imshow(np.log1p(cnt), cmap="gray"); ax[0].set_title("events per pixel (log)")
ax[1].plot(rows); ax[1].set_title("events per row (y)"); ax[1].set_xlabel("y")
ax[2].plot(np.bincount((ev.t.values // 10000).astype(int))); ax[2].set_title("events per 10 ms")
fig.tight_layout()
png = os.path.splitext(path)[0] + "_diag.png"
fig.savefig(png, dpi=110)
print("picture saved:", png)
