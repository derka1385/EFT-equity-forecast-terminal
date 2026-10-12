# Fetches 2 years of daily Yahoo Finance closes for TICKERS into data/, which GitHub Pages serves same-origin,
# so the app does not depend on public CORS relays for these tickers. Run by .github/workflows/pages.yml.
import json, pathlib, re, sys, time, urllib.parse, urllib.request

TICKERS = """
AAPL MSFT NVDA AMZN GOOGL META TSLA NFLX AMD INTC JPM GS MS BAC C UBS BRK-B V MA KO PEP MCD DIS XOM
RACE STLA TM F GM ASML SAP
UBSG.SW NESN.SW NOVN.SW
MC.PA AIR.PA TTE.PA BNP.PA RMS.PA OR.PA
BMW.DE MBG.DE VOW3.DE P911.DE SIE.DE
VOLV-B.ST VOLCAR-B.ST ERIC-B.ST
HSBA.L BARC.L AZN.L SHEL.L
^GSPC ^NDX ^DJI ^STOXX50E ^FTSE ^GDAXI ^FCHI ^OMX
BTC-USD ETH-USD SOL-USD XRP-USD EURUSD=X GBPUSD=X USDCHF=X GC=F SI=F CL=F
""".split()

OUT = pathlib.Path(__file__).resolve().parent.parent / "data"


def file_name(ticker):  # must match snapshotName() in index.html
    return re.sub(r"[^A-Z0-9.\-]", "_", ticker) + ".json"


def fetch(ticker):
    for host in ("query1", "query2"):
        url = (f"https://{host}.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}"
               "?range=2y&interval=1d&includeAdjustedClose=true&events=div%2Csplits")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                res = json.load(r)["chart"]["result"][0]
            meta = res.get("meta", {})
            ts = res["timestamp"]
            quote = res["indicators"]["quote"][0]
            adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose") or [None] * len(ts)
            pairs = []
            for t, close, a, vol in zip(ts, quote["close"], adj, quote.get("volume") or [None] * len(ts)):
                px = a if a is not None else close
                if px and px > 0:
                    pairs.append({"date": time.strftime("%Y-%m-%d", time.gmtime(t)), "close": round(px, 6), "vol": vol})
            if len(pairs) >= 3:
                exchange = meta.get("fullExchangeName")
                return pairs, {"t": ticker, "n": meta.get("longName") or meta.get("shortName") or ticker,
                               "k": meta.get("instrumentType"), "c": meta.get("currency"),
                               "x": None if exchange in ("CCC", "CCY") else exchange}
        except Exception as e:  # keep going: one bad ticker must not stop the others
            print(f"{ticker} via {host}: {e}", file=sys.stderr)
        time.sleep(0.5)
    return None, None


def main():
    OUT.mkdir(exist_ok=True)
    catalog = []
    for ticker in TICKERS:
        pairs, entry = fetch(ticker)
        if pairs:
            out = {"source": "Yahoo Finance", "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pairs": pairs}
            (OUT / file_name(ticker)).write_text(json.dumps(out, separators=(",", ":")))
            catalog.append(entry)
        time.sleep(0.3)
    (OUT / "index.json").write_text(json.dumps({"catalog": catalog}, ensure_ascii=False))
    saved = {e["t"] for e in catalog}
    print(f"{len(saved)}/{len(TICKERS)} tickers saved; missing: {sorted(set(TICKERS) - saved)}")


if __name__ == "__main__":
    main()
