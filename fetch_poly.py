import requests
import json

def fetch_via_subgraph():
    # 使用 The Graph 的去中心化或公共节点，绕过主站防火墙
    SUBGRAPH_URL = "https://gateway.thegraph.com/api/subgraphs/id/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC"
    
    cities = ["NYC", "Chicago", "Dallas", "Miami", "Seattle", "Atlanta"]
    # 2026年2月27日
    target_date = "February 27, 2026"
    
    # GraphQL 查询语句：搜索包含城市名和日期的未结算条件
    query = """
    query GetWeatherMarkets($searchTerm: String!) {
      conditions(where: {
        question_contains: $searchTerm,
        resolved: False
      }, first: 5) {
        question
        fpmm {
          id
          currentOdds
          outcomes
        }
      }
    }
    """

    results = []
    print(f"--- 正在通过 Subgraph 获取 {target_date} 数据 ---")

    for city in cities:
        search_str = f"Highest temperature in {city} on {target_date}"
        variables = {"searchTerm": search_str}
        
        try:
            response = requests.post(SUBGRAPH_URL, json={'query': query, 'variables': variables}, timeout=30)
            
            if response.status_code != 200:
                results.append({"city": city, "error": f"HTTP {response.status_code}"})
                continue
                
            data = response.json().get('data', {}).get('conditions', [])
            
            if not data:
                results.append({"city": city, "error": "No matching market found on-chain"})
                continue

            # 获取第一个匹配结果
            market = data[0]
            fpmm = market.get('fpmm')
            if not fpmm:
                results.append({"city": city, "error": "Market data (FPMM) missing"})
                continue
                
            outcomes = fpmm['outcomes'] # 温度桶标签
            odds = fpmm['currentOdds'] # 对应概率 (0-1)
            
            buckets = []
            for i, label in enumerate(outcomes):
                prob = float(odds[i]) * 100
                buckets.append({"range": label, "prob": f"{prob:.1f}%"})
            
            # 按概率从高到低排序
            buckets.sort(key=lambda x: float(x['prob'].replace('%','')), reverse=True)
            
            results.append({
                "city": city,
                "question": market['question'],
                "predictions": buckets[:3]
            })

        except Exception as e:
            results.append({"city": city, "error": str(e)})

    # 输出格式化结果
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    fetch_via_subgraph()
