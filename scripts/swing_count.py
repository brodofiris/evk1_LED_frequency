import argparse, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

ap = argparse.ArgumentParser()
ap.add_argument("csv")
ap.add_argument("--roi", type=int, nargs=4, metavar=("X0", "X1", "Y0", "Y1"),
                help="only use events inside this box (the LED's path)")
ap.add_argument("--bin-ms", type=float, default=2.0)
ap.add_argument("--min-events", type=int, default=15)
ap.add_argument("--smooth-ms", type=float, default=40.0)
ap.add_argument("--prominence", type=float, default=0.4)
a = ap.parse_args()

path = os.path.expanduser(a.csv)
ev = pd.read_csv(path, header=None, names=["x", "y", "p", "t"])
if a.roi:
    x0, x1, y0, y1 = a.roi
    ev = ev[(ev.x >= x0) & (ev.x <= x1) & (ev.y >= y0) & (ev.y <= y1)]
bin_us = a.bin_ms * 1000
b = (ev.t.values // bin_us).astype(int)
g = pd.DataFrame({"b": b, "x": ev.x.values, "y": ev.y.values}).groupby("b")
cnt = g.size()
ok = cnt[cnt >= a.min_events].index
t_ok = ok.values * bin_us / 1e6
xy = np.column_stack([g["x"].mean()[ok].values, g["y"].mean()[ok].values])
xy = xy - xy.mean(axis=0)
_, _, vt = np.linalg.svd(xy, full_matrices=False)
pos = xy @ vt[0]

dt = bin_us / 1e6
t = np.arange(t_ok[0], t_ok[-1], dt)
pos = np.interp(t, t_ok, pos)
k = max(1, int(a.smooth_ms / a.bin_ms))
pos_s = np.convolve(pos, np.ones(k) / k, mode="same")
amp = np.percentile(pos_s, 95) - np.percentile(pos_s, 5)

spec = np.abs(np.fft.rfft((pos_s - pos_s.mean()) * np.hanning(len(pos_s))))
fr = np.fft.rfftfreq(len(pos_s), dt)
m = fr > 0.1
f_fft = fr[m][np.argmax(spec[m])] if m.any() else float("nan")
min_dist = max(1, int(0.5 / f_fft / dt)) if f_fft == f_fft else 1

hi, _ = find_peaks(pos_s, prominence=a.prominence * amp, distance=min_dist)
lo, _ = find_peaks(-pos_s, prominence=a.prominence * amp, distance=min_dist)

print(f"events used: {len(ev)}, usable slices: {len(ok)}, length: {t[-1]-t[0]:.2f} s, swing amplitude: {amp:.0f} px")
print(f"maxima (cycles): {len(hi)}, minima: {len(lo)}, single sweeps: {max(0, len(hi)+len(lo)-1)}")
if len(hi) > 1:
    per = np.diff(t[hi])
    print(f"period from peaks: median {np.median(per):.3f} s (range {per.min():.3f} to {per.max():.3f}), {1/np.median(per):.3f} Hz")
print(f"frequency from FFT: {f_fft:.3f} Hz")

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(t, pos, lw=0.5, alpha=0.5, label="raw")
ax.plot(t, pos_s, lw=1.5, label="smoothed")
ax.plot(t[hi], pos_s[hi], "rv", label="maxima")
ax.plot(t[lo], pos_s[lo], "g^", label="minima")
ax.set_xlabel("time (s)"); ax.set_ylabel("position along motion (px)"); ax.legend()
out = os.path.splitext(path)[0] + "_swing.png"
fig.tight_layout(); fig.savefig(out, dpi=100)
print("graph saved to", out)
