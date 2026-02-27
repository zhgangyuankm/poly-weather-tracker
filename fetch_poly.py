import requests
import json
import time

def fetch_data():
    # 六大城市
    cities = ["NYC", "Chicago", "Dallas", "Miami", "Seattle", "Atlanta"]
    # 今天日期
    target_date = "February 27, 2026"
    results = []

    # 关键：模拟真实的 Chrome 浏览器请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://polymarket.com",
        "Referer": "https://polymarket.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }

    session = requests.Session()
    session.headers.update(headers)

    for city in cities:
        # 使用模糊查询，增加搜索命中率
        url = "https://gamma-api.polymarket.com"
        params = {
            "query": f"Highest temperature in {city}",
            "limit": 10,
            "active": "true"
        }
        
        try:
            # 增加重试逻辑和延迟，防止被识别为爬虫
            time.sleep(1) 
            response = session.get(url, params=params, timeout=20)
            
            # 如果不是 200，说明被拦截了
            if response.status_code != 200:
                results.append({"city": city, "error": f"HTTP {response.status_code}"})
                continue
            
            # 检查返回内容是否为 JSON
            try:
                events = response.json()
            except Exception:
                results.append({"city": city, "error": "Cloudflare Blocked (HTML returned)"})
                continue

            # 筛选出匹配今天日期的活动
            matching_event = next((e for e in events if target_date in e.get('title', '')), None)
            
            if matching_event:
                markets_data = []
                for m in matching_event.get('markets', []):
                    # 获取该桶的价格/概率
                    prices = json.loads(m.get('outcomePrices', '["0"]'))
                    prob = float(prices[0]) * 100 if prices else 0
                    markets_data.append({
                        "range": m.get('groupItemTitle'),
                        "prob": f"{prob:.1f}%"
                    })
                results.append({"city": city, "data": markets_data})
            else:
                results.append({"city": city, "error": "No matching date found"})

        except Exception as e:
            results.append({"city": city, "error": str(e)})

    # 输出结果
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    fetch_data()
