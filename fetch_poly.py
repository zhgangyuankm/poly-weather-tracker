import requests
import json
import os

def fetch_data():
    cities = ["NYC", "Chicago", "Dallas", "Miami", "Seattle", "Atlanta"]
    target_date = "February 27, 2026"
    results = []

    for city in cities:
        url = "https://gamma-api.polymarket.com"
        params = {
            "query": f"Highest temperature in {city} on {target_date}",
            "limit": 1
        }
        try:
            # GitHub 服务器位于美国，通常不会被屏蔽
            response = requests.get(url, params=params, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if data:
                    event = data[0]
                    markets_data = []
                    for m in event.get('markets', []):
                        price = json.loads(m.get('outcomePrices', '["0"]'))[0]
                        markets_data.append({
                            "range": m.get('groupItemTitle'),
                            "prob": f"{float(price)*100:.1f}%"
                        })
                    results.append({"city": city, "data": markets_data})
            else:
                results.append({"city": city, "error": f"Status {response.status_code}"})
        except Exception as e:
            results.append({"city": city, "error": str(e)})

    # 将结果打印出来，方便在 GitHub Action 日志查看
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # 也可以保存到文件
    with open("weather_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fetch_data()
