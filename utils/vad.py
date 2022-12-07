from math import ceil


def resample(ts, max_gap=3, max_len=30):
    """Implementation with fix for overlong segments from
    https://github.com/danijel3/CroatianSpeech/blob/main/feb2017/vad.py"""
    new_ts = []
    for s in ts:
        if s["end"] - s["start"] > max_len:
            print(
                f"Error: max_len ({max_len}) is smaller than one of the segments ({s})!"
            )
            L = s["end"] - s["start"]
            N = ceil(L / max_len)
            P = L / N
            for p in range(N - 1):
                ss = s["start"] + p * P
                new_ts.append({"start": ss, "end": ss + P})
                print(f"Added {new_ts[-1]}")
            new_ts.append({"start": s["start"] + (N - 1) * P, "end": s["end"]})
            print(f"Added {new_ts[-1]}")
        else:
            new_ts.append(s)
    ts = new_ts
    gts = []
    g = [ts[0]]
    for s in ts[1:]:
        if s["start"] - g[-1]["end"] < max_gap:
            g.append(s)
        else:
            gts.append(g)
            g = [s]
    gts.append(g)
    ret = []
    for g in gts:
        l = g[-1]["end"] - g[0]["start"]
        split_num = ceil(l / max_len)
        if split_num > 1:
            min_len = l / split_num
            start = g[0]["start"]
            end = g[0]["end"]
            for s in g[1:]:
                if s["end"] - start > max_len or end - start > min_len:
                    ret.append({"start": start, "end": end})
                    start = s["start"]
                    end = s["end"]
                else:
                    end = s["end"]
            ret.append({"start": start, "end": end})
        else:
            ret.append({"start": g[0]["start"], "end": g[-1]["end"]})
    return ret
