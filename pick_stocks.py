#!/usr/bin/env python3
"""筛选股价<29元A股，排除科创板/北交所，按性价比排序，输出Top5代码"""
import subprocess, json, sys

PRICE_MAX = 29
TOP_N = 5

def fetch(market, page=1, num=80):
    url = f'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={page}&num={num}&sort=changepercent&asc=0&node={market}'
    r = subprocess.run(['curl', '-s', url, '-H', 'Referer: https://finance.sina.com.cn'],
                      capture_output=True, timeout=20)
    try:
        return json.loads(r.stdout.decode('gbk', errors='replace'))
    except:
        return []

def valid(code):
    return not (code.startswith('688') or code.startswith('920') or code.startswith('8'))

def score(s):
    pe = float(s.get('per', 999) or 999)
    change = float(s.get('changepercent', 0) or 0)
    pb = float(s.get('pb', 99) or 99)
    turnover = float(s.get('turnoverratio', 0) or 0)
    if pe <= 0 or pe > 500:
        return 0
    return round(
        (30 / max(pe, 1)) * 40 +
        min(max(change, -5), 10) * 3 +
        (5 / max(pb, 0.5)) * 15 +
        min(turnover, 15) * 1, 2)

def main():
    stocks = []
    for m in ['sh_a', 'sz_a']:
        for p in [1, 2, 3, 4]:
            batch = fetch(m, p, 80)
            if not batch: break
            stocks.extend(batch)
            if len(batch) < 80: break

    candidates = []
    for s in stocks:
        code = s.get('code', '')
        price = float(s.get('trade', 999) or 999)
        if not valid(code) or price >= PRICE_MAX or price <= 1:
            continue
        sc = score(s)
        if sc > 0:
            candidates.append((code, s.get('name',''), price, sc, s.get('changepercent',0)))

    candidates.sort(key=lambda x: x[3], reverse=True)
    top = candidates[:TOP_N]

    codes = ','.join(c[0] for c in top)
    print(codes)  # 输出给 main.py --stocks
    
    print(f"\n{'='*55}", file=sys.stderr)
    print(f"股价<{PRICE_MAX}元 Top{TOP_N}:", file=sys.stderr)
    for i, (c, n, p, sc, ch) in enumerate(top, 1):
        print(f"  {i}. {n}({c}) {p:.2f} PE:- 评分:{sc:.1f} {float(ch):+.2f}%", file=sys.stderr)
    print(f"{'='*55}", file=sys.stderr)

if __name__ == '__main__':
    main()
