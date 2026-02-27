import requests
import json

def fetch_via_subgraph():
    # Polymarket 在 Polygon 上的官方子图地址
    SUBGRAPH_URL = "https://api.thegraph.com"
    
    # 想要查询的城市关键字
    cities = ["NYC", "Chicago", "Dallas", "Miami", "Seattle", "Atlanta"]
    target_date = "February 27, 2026"
    
    # GraphQL 查询语句：寻找包含城市名和日期的活跃市场
    query_template = """
    {
      conditions(where: {question_contains: "%s", question_contains_nocase: "%s", resolved: false}) {
        question
        outcomeSlotCount
        fpmm {
          id
          currentOdds
          outcomes
        }
      }
    }
    """

    results = []

    for city in cities:
        # 构建搜索词，例如 "Highest temperature in NYC on February 27"
        search_term = f"Highest temperature in {city} on {target_date}"
        
        try:
            # 发送 GraphQL 请求
            response = requests.post(SUBGRAPH_URL, json={'query': query_template % (city, target_date)})
            
            if response.status_code != 200:
                results.append({"city": city, "error": f"Subgraph Error {response.status_code}"})
                continue
                
            data = response.json().get('data', {}).get('conditions', [])
            
            if not data:
                results.append({"city": city, "error": "No matching market found on-chain"})
                continue

            # 取匹配度最高的一个（通常是第一个）
            market = data[0]
            outcomes = market['fpmm']['outcomes']
            odds = market['fpmm']['currentOdds'] # 这是一个数组，对应每个桶的概率
            
            buckets = []
            for i, label in enumerate(outcomes):
                # 这里的 odds 是从 0-1 的浮点数
                prob = float(odds[i]) * 100
                buckets.append({"range": label, "prob": f"{prob:.1f}%"})
            
            results.append({
                "city": city,
                "question": market['question'],
                "data": sorted(buckets, key=lambda x: float(x['prob'].replace('%','')), reverse=True)
            })

        except Exception as e:
            results.append({"city": city, "error": str(e)})

    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    fetch_via_subgraph()
