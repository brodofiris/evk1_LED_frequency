"""Load a CSV of events (x, y, polarity, timestamp_us) and print basic statistics."""
import os, sys
import pandas as pd

path = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/evk1_data/test.csv")
ev = pd.read_csv(path, header=None, names=["x", "y", "p", "t"])
print(ev.head())
print("events:", len(ev), " x range:", ev.x.min(), ev.x.max(), " y range:", ev.y.min(), ev.y.max())
