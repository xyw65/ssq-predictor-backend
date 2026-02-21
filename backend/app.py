"""
智能预测实验室 - 后端服务
提供数据爬取、预测计算、战绩评估等API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
from collections import Counter, defaultdict
from itertools import combinations
import random
import math

app = Flask(__name__)
CORS(app)  # 允许跨域

# 数据存储路径
DATA_FILE = 'ssq_data.json'

def load_data():
    """加载本地数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"historical_data": {}}

def save_data(data):
    """保存数据到本地"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

@app.route('/api/data', methods=['GET'])
def get_data():
    """获取所有数据"""
    data = load_data()
    return jsonify(data)

@app.route('/api/update', methods=['POST'])
def update_data():
    """
    从网页爬取最新数据
    请求体: {"url": "https://www.55123.cn/zs/ssq_26.html?startTerm=xxx&endTerm=yyy"}
    """
    try:
        req_data = request.get_json()
        url = req_data.get('url', 'https://www.55123.cn/zs/ssq_26.html')
        
        # 爬取数据
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取期号和号码
        historical_data = {}
        
        # 查找所有包含期号的行
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 34:  # 期号 + 33个红球位置 + 蓝球
                # 提取期号
                period_text = cells[0].get_text().strip()
                if re.match(r'^\d{7}$', period_text):  # 如 2025001
                    period = period_text
                    # 提取红球（1-33列中标记有数字的）
                    red_balls = []
                    for i in range(1, 34):  # 1-33列
                        if i < len(cells):
                            cell_text = cells[i].get_text().strip()
                            if cell_text and cell_text != str(i):
                                try:
                                    num = int(cell_text)
                                    if 1 <= num <= 33:
                                        red_balls.append(num)
                                except:
                                    pass
                    
                    # 提取蓝球（最后16列）
                    blue_ball = None
                    for i in range(34, 50):  # 蓝球列
                        if i < len(cells):
                            cell_text = cells[i].get_text().strip()
                            if cell_text:
                                try:
                                    num = int(cell_text)
                                    if 1 <= num <= 16:
                                        blue_ball = num
                                        break
                                except:
                                    pass
                    
                    if len(red_balls) == 6 and blue_ball:
                        historical_data[period] = sorted(red_balls) + [blue_ball]
        
        # 保存数据
        data = load_data()
        data['historical_data'] = historical_data
        data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['data_source'] = url
        save_data(data)
        
        return jsonify({
            "success": True,
            "message": f"成功更新 {len(historical_data)} 期数据",
            "count": len(historical_data)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"更新失败: {str(e)}"
        }), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    执行预测
    请求体: {"method": "方法名"} 或不传则预测所有方法
    """
    try:
        req_data = request.get_json() or {}
        method_name = req_data.get('method')
        
        data = load_data()
        historical_data = data.get('historical_data', {})
        
        if not historical_data:
            return jsonify({"success": False, "message": "没有历史数据"}), 400
        
        predictor = AdvancedSSQPredictor(historical_data)
        
        if method_name:
            # 预测指定方法
            method_func = predictor.get_method(method_name)
            if method_func:
                prediction = method_func(predictor.get_recent_data(100))
                return jsonify({
                    "success": True,
                    "method": method_name,
                    "prediction": prediction,
                    "reds": prediction[:6],
                    "blue": prediction[6]
                })
            else:
                return jsonify({"success": False, "message": "未知方法"}), 400
        else:
            # 预测所有方法
            predictions = predictor.predict_all()
            return jsonify({
                "success": True,
                "predictions": predictions
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"预测失败: {str(e)}"
        }), 500

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    """
    评估所有方法的战绩
    """
    try:
        data = load_data()
        historical_data = data.get('historical_data', {})
        
        if len(historical_data) < 101:
            return jsonify({
                "success": False, 
                "message": f"数据不足，需要至少101期，当前只有{len(historical_data)}期"
            }), 400
        
        predictor = AdvancedSSQPredictor(historical_data)
        results = predictor.evaluate_all_methods()
        
        # 保存战绩
        data['performance_ranking'] = results[:10]
        data['eliminated_methods'] = [
            {"method": r['method'], "score": r['score'], "reason": "战绩较低，已淘汰"}
            for r in results[10:]
        ]
        save_data(data)
        
        return jsonify({
            "success": True,
            "ranking": results[:10],
            "eliminated": results[10:],
            "total_evaluated": len(historical_data) - 100
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"评估失败: {str(e)}"
        }), 500

# ==================== 预测算法类 ====================

class AdvancedSSQPredictor:
    def __init__(self, historical_data):
        self.data = historical_data
        self.sorted_periods = sorted(historical_data.keys())
        
        # 定义所有预测方法
        self.methods = {
            "马尔可夫链转移": self.predict_markov_chain,
            "神经网络模式": self.predict_neural_pattern,
            "蒙特卡洛模拟": self.predict_monte_carlo,
            "遗传算法进化": self.predict_genetic_algorithm,
            "斐波那契黄金": self.predict_fibonacci_golden,
            "质数分布分析": self.predict_prime_analysis,
            "周期性傅里叶": self.predict_periodic_analysis,
            "对称性镜像": self.predict_symmetry_mirror,
            "连号斜连分析": self.predict_consecutive_slant,
            "和值尾数分析": self.predict_sum_tail,
            "等差等比数列": self.predict_arithmetic_geometric,
            "区间平衡理论": self.predict_zone_balance,
            "奇偶平衡优化": self.predict_odd_even_balance,
            "跨度优化选择": self.predict_span_optimized,
            "蓝球周期分析": self.predict_blue_cycle,
            "关联规则挖掘": self.predict_association_rules,
            "聚类分析K均值": self.predict_kmeans_clustering,
            "AC值优化选择": self.predict_ac_value,
            "混沌吸引子": self.predict_chaos_attractor,
            "布朗运动随机": self.predict_brownian_motion,
        }
    
    def get_method(self, name):
        return self.methods.get(name)
    
    def get_recent_data(self, n_periods, end_period=None):
        if end_period is None:
            end_period = self.sorted_periods[-1]
        end_idx = self.sorted_periods.index(end_period)
        start_idx = max(0, end_idx - n_periods + 1)
        periods = self.sorted_periods[start_idx:end_idx+1]
        return {p: self.data[p] for p in periods}
    
    def predict_all(self):
        data = self.get_recent_data(100)
        predictions = {}
        for name, func in self.methods.items():
            try:
                predictions[name] = func(data)
            except:
                predictions[name] = [1,2,3,4,5,6,1]  # 默认值
        return predictions
    
    def evaluate_all_methods(self):
        sorted_periods = self.sorted_periods
        records = {name: {
            "total": 0, "score": 0,
            "first_prize": 0, "second_prize": 0, "third_prize": 0,
            "fourth_prize": 0, "fifth_prize": 0, "sixth_prize": 0,
            "red_hits": 0, "blue_hits": 0
        } for name in self.methods.keys()}
        
        start_idx = 100
        for i in range(start_idx, len(sorted_periods)):
            target_period = sorted_periods[i]
            end_period = sorted_periods[i-1]
            data = self.get_recent_data(100, end_period)
            
            actual = self.data[target_period]
            actual_reds = set(actual[:6])
            actual_blue = actual[6]
            
            for method_name, method_func in self.methods.items():
                try:
                    pred = method_func(data)
                    pred_reds = set(pred[:6])
                    pred_blue = pred[6]
                    
                    records[method_name]["total"] += 1
                    red_hit = len(actual_reds & pred_reds)
                    blue_hit = 1 if actual_blue == pred_blue else 0
                    records[method_name]["red_hits"] += red_hit
                    records[method_name]["blue_hits"] += blue_hit
                    
                    if red_hit == 6 and blue_hit == 1:
                        records[method_name]["first_prize"] += 1
                        records[method_name]["score"] += 1000
                    elif red_hit == 6 and blue_hit == 0:
                        records[method_name]["second_prize"] += 1
                        records[method_name]["score"] += 100
                    elif red_hit == 5 and blue_hit == 1:
                        records[method_name]["third_prize"] += 1
                        records[method_name]["score"] += 30
                    elif (red_hit == 5 and blue_hit == 0) or (red_hit == 4 and blue_hit == 1):
                        records[method_name]["fourth_prize"] += 1
                        records[method_name]["score"] += 10
                    elif (red_hit == 4 and blue_hit == 0) or (red_hit == 3 and blue_hit == 1):
                        records[method_name]["fifth_prize"] += 1
                        records[method_name]["score"] += 5
                    elif blue_hit == 1 and red_hit <= 2:
                        records[method_name]["sixth_prize"] += 1
                        records[method_name]["score"] += 1
                except:
                    continue
        
        results = []
        for method_name, record in records.items():
            if record["total"] > 0:
                results.append({
                    "method": method_name,
                    "total": record["total"],
                    "score": record["score"],
                    "first_prize": record["first_prize"],
                    "second_prize": record["second_prize"],
                    "third_prize": record["third_prize"],
                    "fourth_prize": record["fourth_prize"],
                    "fifth_prize": record["fifth_prize"],
                    "sixth_prize": record["sixth_prize"],
                    "red_hits": record["red_hits"],
                    "blue_hits": record["blue_hits"],
                    "avg_red_hits": record["red_hits"] / record["total"],
                    "avg_blue_hits": record["blue_hits"] / record["total"],
                })
        
        results.sort(key=lambda x: (x["score"], x["avg_red_hits"], x["avg_blue_hits"]), reverse=True)
        return results

    # ===== 所有预测方法实现 =====
    def predict_markov_chain(self, data):
        periods = sorted(data.keys())
        transition_count = defaultdict(lambda: defaultdict(int))
        for i in range(1, len(periods)):
            prev_reds = set(data[periods[i-1]][:6])
            curr_reds = set(data[periods[i]][:6])
            for prev in prev_reds:
                for curr in curr_reds:
                    transition_count[prev][curr] += 1
        last_period = periods[-1]
        last_reds = data[last_period][:6]
        scores = defaultdict(float)
        for last_num in last_reds:
            if last_num in transition_count:
                total = sum(transition_count[last_num].values())
                for next_num, count in transition_count[last_num].items():
                    scores[next_num] += count / total
        selected_reds = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:6]
        if len(selected_reds) < 6:
            all_reds = [n for nums in data.values() for n in nums[:6]]
            freq = Counter(all_reds)
            remaining = [n for n in range(1, 34) if n not in selected_reds]
            remaining.sort(key=lambda x: freq[x], reverse=True)
            selected_reds.extend(remaining[:6-len(selected_reds)])
        blue_transition = defaultdict(lambda: defaultdict(int))
        for i in range(1, len(periods)):
            prev_blue = data[periods[i-1]][6]
            curr_blue = data[periods[i]][6]
            blue_transition[prev_blue][curr_blue] += 1
        last_blue = data[last_period][6]
        if last_blue in blue_transition and blue_transition[last_blue]:
            blue_scores = {k: v/sum(blue_transition[last_blue].values()) for k, v in blue_transition[last_blue].items()}
            selected_blue = max(blue_scores.keys(), key=lambda x: blue_scores[x])
        else:
            all_blues = [data[p][6] for p in periods]
            selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds[:6]) + [selected_blue]

    def predict_neural_pattern(self, data):
        periods = sorted(data.keys())
        recent = periods[-10:]
        features = defaultdict(float)
        for idx, p in enumerate(recent):
            weight = (idx + 1) / len(recent)
            for red in data[p][:6]:
                features[red] += weight
        for i in range(1, len(recent)):
            prev_reds = data[recent[i-1]][:6]
            curr_reds = data[recent[i]][:6]
            for pr in prev_reds:
                for cr in curr_reds:
                    if abs(pr - cr) <= 3:
                        features[cr] += 0.3
        selected_reds = sorted(features.keys(), key=lambda x: features[x], reverse=True)[:6]
        blue_features = defaultdict(float)
        for idx, p in enumerate(recent):
            weight = (idx + 1) / len(recent)
            blue = data[p][6]
            blue_features[blue] += weight
        selected_blue = max(blue_features.keys(), key=lambda x: blue_features[x])
        return sorted(selected_reds) + [selected_blue]

    def predict_monte_carlo(self, data):
        all_reds = [n for nums in data.values() for n in nums[:6]]
        red_freq = Counter(all_reds)
        numbers = list(range(1, 34))
        weights = [red_freq.get(n, 0) + 1 for n in numbers]
        total_weight = sum(weights)
        probs = [w / total_weight for w in weights]
        selected_reds = []
        available = numbers.copy()
        available_probs = probs.copy()
        for _ in range(6):
            if not available:
                break
            idx = random.choices(range(len(available)), weights=available_probs)[0]
            selected_reds.append(available.pop(idx))
            available_probs.pop(idx)
        all_blues = [nums[6] for nums in data.values()]
        blue_freq = Counter(all_blues)
        blue_numbers = list(range(1, 17))
        blue_weights = [blue_freq.get(n, 0) + 1 for n in blue_numbers]
        blue_total = sum(blue_weights)
        blue_probs = [w / blue_total for w in blue_weights]
        selected_blue = random.choices(blue_numbers, weights=blue_probs)[0]
        return sorted(selected_reds) + [selected_blue]

    def predict_genetic_algorithm(self, data):
        all_reds = [n for nums in data.values() for n in nums[:6]]
        red_freq = Counter(all_reds)
        population = []
        hot_numbers = [n for n, _ in red_freq.most_common(15)]
        for _ in range(20):
            combo = random.sample(hot_numbers, 6)
            population.append(combo)
        def fitness(combo):
            score = 0
            for nums in list(data.values())[-20:]:
                matches = len(set(combo) & set(nums[:6]))
                score += matches
            return score
        for generation in range(10):
            population.sort(key=fitness, reverse=True)
            survivors = population[:10]
            new_generation = survivors.copy()
            while len(new_generation) < 20:
                parent1, parent2 = random.sample(survivors, 2)
                child = list(set(parent1[:3] + parent2[3:]))
                if len(child) < 6:
                    remaining = [n for n in hot_numbers if n not in child]
                    child.extend(random.sample(remaining, 6-len(child)))
                elif len(child) > 6:
                    child = random.sample(child, 6)
                if random.random() < 0.1:
                    idx = random.randint(0, 5)
                    child[idx] = random.choice([n for n in range(1, 34) if n not in child])
                new_generation.append(child)
            population = new_generation
        population.sort(key=fitness, reverse=True)
        selected_reds = population[0]
        all_blues = [nums[6] for nums in data.values()]
        blue_freq = Counter(all_blues)
        selected_blue = blue_freq.most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_fibonacci_golden(self, data):
        phi = (1 + math.sqrt(5)) / 2
        periods = sorted(data.keys())
        last_period = periods[-1]
        last_reds = data[last_period][:6]
        selected_reds = []
        for num in last_reds:
            up = min(33, int(num * phi) % 33 + 1)
            down = max(1, int(num / phi) % 33 + 1)
            selected_reds.extend([up, down])
        selected_reds = list(set(selected_reds))
        if len(selected_reds) < 6:
            all_reds = [n for nums in data.values() for n in nums[:6]]
            freq = Counter(all_reds)
            remaining = [n for n in range(1, 34) if n not in selected_reds]
            remaining.sort(key=lambda x: freq[x], reverse=True)
            selected_reds.extend(remaining[:6-len(selected_reds)])
        selected_reds = selected_reds[:6]
        last_blue = data[last_period][6]
        blue_up = min(16, int(last_blue * phi) % 16 + 1)
        blue_down = max(1, int(last_blue / phi) % 16 + 1)
        selected_blue = blue_up if random.random() > 0.5 else blue_down
        return sorted(selected_reds) + [selected_blue]

    def predict_prime_analysis(self, data):
        primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31}
        prime_counts = defaultdict(int)
        non_prime_counts = defaultdict(int)
        for nums in data.values():
            for red in nums[:6]:
                if red in primes:
                    prime_counts[red] += 1
                else:
                    non_prime_counts[red] += 1
        sorted_primes = sorted(prime_counts.keys(), key=lambda x: prime_counts[x], reverse=True)
        sorted_non_primes = sorted(non_prime_counts.keys(), key=lambda x: non_prime_counts[x], reverse=True)
        selected_reds = sorted_primes[:4] + sorted_non_primes[:2]
        blue_primes = {2, 3, 5, 7, 11, 13}
        all_blues = [nums[6] for nums in data.values()]
        blue_freq = Counter(all_blues)
        blue_prime_freq = [(b, blue_freq[b]) for b in blue_primes if b in blue_freq]
        if blue_prime_freq and random.random() > 0.3:
            selected_blue = max(blue_prime_freq, key=lambda x: x[1])[0]
        else:
            selected_blue = blue_freq.most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_periodic_analysis(self, data):
        periods = sorted(data.keys())
        number_periods = defaultdict(list)
        for num in range(1, 34):
            last_seen = -1
            for idx, p in enumerate(periods):
                if num in data[p][:6]:
                    if last_seen >= 0:
                        number_periods[num].append(idx - last_seen)
                    last_seen = idx
        selected_reds = []
        for num in range(1, 34):
            if num in number_periods and number_periods[num]:
                avg_period = sum(number_periods[num]) / len(number_periods[num])
                last_pos = -1
                for idx, p in enumerate(periods):
                    if num in data[p][:6]:
                        last_pos = idx
                if last_pos >= 0 and len(periods) - last_pos >= avg_period * 0.8:
                    selected_reds.append(num)
        if len(selected_reds) < 6:
            all_reds = [n for nums in data.values() for n in nums[:6]]
            freq = Counter(all_reds)
            remaining = [n for n in range(1, 34) if n not in selected_reds]
            remaining.sort(key=lambda x: freq[x], reverse=True)
            selected_reds.extend(remaining[:6-len(selected_reds)])
        selected_reds = selected_reds[:6]
        all_blues = [data[p][6] for p in periods]
        selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_symmetry_mirror(self, data):
        periods = sorted(data.keys())
        last_period = periods[-1]
        last_reds = data[last_period][:6]
        mirrored = [34 - num for num in last_reds]
        all_reds = [n for nums in data.values() for n in nums[:6]]
        freq = Counter(all_reds)
        scores = defaultdict(float)
        for num in range(1, 34):
            scores[num] = freq.get(num, 0)
            if num in mirrored:
                scores[num] += 5
        selected_reds = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:6]
        last_blue = data[last_period][6]
        blue_mirror = 17 - last_blue
        all_blues = [data[p][6] for p in periods]
        if blue_mirror in all_blues and random.random() > 0.5:
            selected_blue = blue_mirror
        else:
            selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_consecutive_slant(self, data):
        periods = sorted(data.keys())
        consecutive_patterns = defaultdict(int)
        for nums in data.values():
            reds = sorted(nums[:6])
            for i in range(len(reds) - 1):
                if reds[i+1] - reds[i] == 1:
                    consecutive_patterns[reds[i]] += 1
        last_period = periods[-1]
        last_reds = data[last_period][:6]
        selected_reds = list(last_reds)
        for num in last_reds:
            if num + 1 <= 33 and consecutive_patterns.get(num, 0) > 2:
                if num + 1 not in selected_reds:
                    selected_reds.append(num + 1)
            if num - 1 >= 1 and consecutive_patterns.get(num - 1, 0) > 2:
                if num - 1 not in selected_reds:
                    selected_reds.append(num - 1)
        selected_reds = list(set(selected_reds))
        if len(selected_reds) < 6:
            all_reds = [n for nums in data.values() for n in nums[:6]]
            freq = Counter(all_reds)
            remaining = [n for n in range(1, 34) if n not in selected_reds]
            remaining.sort(key=lambda x: freq[x], reverse=True)
            selected_reds.extend(remaining[:6-len(selected_reds)])
        selected_reds = selected_reds[:6]
        all_blues = [data[p][6] for p in periods]
        selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_sum_tail(self, data):
        tail_counts = defaultdict(int)
        for nums in data.values():
            total = sum(nums[:6])
            tail = total % 10
            tail_counts[tail] += 1
        common_tail = max(tail_counts.keys(), key=lambda x: tail_counts[x])
        all_reds = [n for nums in data.values() for n in nums[:6]]
        freq = Counter(all_reds)
        hot_numbers = [n for n, _ in freq.most_common(20)]
        best_combo = None
        best_score = -1
        for combo in combinations(hot_numbers, 6):
            if sum(combo) % 10 == common_tail:
                score = sum(freq[n] for n in combo)
                if score > best_score:
                    best_score = score
                    best_combo = combo
        if best_combo is None:
            best_combo = hot_numbers[:6]
        selected_reds = list(best_combo)
        blue_tail_counts = defaultdict(int)
        for nums in data.values():
            blue_tail_counts[nums[6] % 10] += 1
        common_blue_tail = max(blue_tail_counts.keys(), key=lambda x: blue_tail_counts[x])
        all_blues = [data[p][6] for p in sorted(data.keys())]
        candidates = [b for b in range(1, 17) if b % 10 == common_blue_tail]
        if candidates:
            blue_freq = Counter(all_blues)
            selected_blue = max(candidates, key=lambda x: blue_freq.get(x, 0))
        else:
            selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_arithmetic_geometric(self, data):
        periods = sorted(data.keys())
        last_period = periods[-1]
        last_reds = sorted(data[last_period][:6])
        selected_reds = []
        for i in range(len(last_reds) - 1):
            diff = last_reds[i+1] - last_reds[i]
            next_num = last_reds[i+1] + diff
            if 1 <= next_num <= 33 and next_num not in selected_reds:
                selected_reds.append(next_num)
        if len(selected_reds) < 6:
            all_reds = [n for nums in data.values() for n in nums[:6]]
            freq = Counter(all_reds)
            remaining = [n for n in range(1, 34) if n not in selected_reds]
            remaining.sort(key=lambda x: freq[x], reverse=True)
            selected_reds.extend(remaining[:6-len(selected_reds)])
        selected_reds = selected_reds[:6]
        last_blue = data[last_period][6]
        blue_candidates = [(last_blue + i) % 16 + 1 for i in range(1, 4)]
        all_blues = [data[p][6] for p in periods]
        blue_freq = Counter(all_blues)
        selected_blue = max(blue_candidates, key=lambda x: blue_freq.get(x, 0))
        return sorted(selected_reds) + [selected_blue]

    def predict_zone_balance(self, data):
        zones = {1: list(range(1, 12)), 2: list(range(12, 23)), 3: list(range(23, 34))}
        zone_counts = {1: [], 2: [], 3: []}
        for nums in data.values():
            reds = nums[:6]
            for z, zone_nums in zones.items():
                count = sum(1 for r in reds if r in zone_nums)
                zone_counts[z].append(count)
        avg_counts = {z: sum(counts)/len(counts) for z, counts in zone_counts.items()}
        target = {z: round(avg_counts[z]) for z in zones}
        total = sum(target.values())
        if total != 6:
            diff = 6 - total
            zone_freq = {z: sum(zone_counts[z]) for z in zones}
            max_zone = max(zone_freq.keys(), key=lambda x: zone_freq[x])
            target[max_zone] += diff
        all_reds = [n for nums in data.values() for n in nums[:6]]
        freq = Counter(all_reds)
        selected_reds = []
        for z, zone_nums in zones.items():
            zone_freq = [(n, freq.get(n, 0)) for n in zone_nums]
            zone_freq.sort(key=lambda x: x[1], reverse=True)
            selected_reds.extend([n for n, _ in zone_freq[:max(0, target[z])]])
        selected_reds = selected_reds[:6]
        if len(selected_reds) < 6:
            remaining = [n for n in range(1, 34) if n not in selected_reds]
            remaining.sort(key=lambda x: freq[x], reverse=True)
            selected_reds.extend(remaining[:6-len(selected_reds)])
        all_blues = [data[p][6] for p in sorted(data.keys())]
        selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds[:6]) + [selected_blue]

    def predict_odd_even_balance(self, data):
        odd_even_ratios = []
        for nums in data.values():
            reds = nums[:6]
            odd_count = sum(1 for r in reds if r % 2 == 1)
            odd_even_ratios.append((odd_count, 6 - odd_count))
        ratio_freq = Counter(odd_even_ratios)
        most_common = ratio_freq.most_common(1)[0][0]
        target_odd, target_even = most_common
        all_reds = [n for nums in data.values() for n in nums[:6]]
        freq = Counter(all_reds)
        odd_numbers = [i for i in range(1, 34) if i % 2 == 1]
        even_numbers = [i for i in range(1, 34) if i % 2 == 0]
        odd_freq = [(n, freq.get(n, 0)) for n in odd_numbers]
        odd_freq.sort(key=lambda x: x[1], reverse=True)
        selected_odd = [n for n, _ in odd_freq[:target_odd]]
        even_freq = [(n, freq.get(n, 0)) for n in even_numbers]
        even_freq.sort(key=lambda x: x[1], reverse=True)
        selected_even = [n for n, _ in even_freq[:target_even]]
        selected_reds = selected_odd + selected_even
        all_blues = [data[p][6] for p in sorted(data.keys())]
        blue_freq = Counter(all_blues)
        odd_blues = [b for b in range(1, 17) if b % 2 == 1]
        even_blues = [b for b in range(1, 17) if b % 2 == 0]
        odd_blue_freq = sum(blue_freq.get(b, 0) for b in odd_blues)
        even_blue_freq = sum(blue_freq.get(b, 0) for b in even_blues)
        if odd_blue_freq > even_blue_freq:
            selected_blue = max(odd_blues, key=lambda x: blue_freq.get(x, 0))
        else:
            selected_blue = max(even_blues, key=lambda x: blue_freq.get(x, 0))
        return sorted(selected_reds) + [selected_blue]

    def predict_span_optimized(self, data):
        spans = []
        for nums in data.values():
            reds = nums[:6]
            span = max(reds) - min(reds)
            spans.append(span)
        span_freq = Counter(spans)
        common_span = span_freq.most_common(1)[0][0]
        all_reds = [n for nums in data.values() for n in nums[:6]]
        freq = Counter(all_reds)
        hot_numbers = [n for n, _ in freq.most_common(25)]
        best_combo = None
        best_diff = float('inf')
        for combo in combinations(hot_numbers, 6):
            span = max(combo) - min(combo)
            diff = abs(span - common_span)
            if diff < best_diff:
                best_diff = diff
                best_combo = combo
        if best_combo is None:
            best_combo = hot_numbers[:6]
        selected_reds = list(best_combo)
        all_blues = [data[p][6] for p in sorted(data.keys())]
        selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_blue_cycle(self, data):
        periods = sorted(data.keys())
        blue_sequence = [data[p][6] for p in periods]
        blue_freq = Counter(blue_sequence)
        last_blue = blue_sequence[-1]
        blue_transitions = defaultdict(list)
        for i in range(len(blue_sequence) - 1):
            blue_transitions[blue_sequence[i]].append(blue_sequence[i+1])
        if last_blue in blue_transitions and blue_transitions[last_blue]:
            next_blue_candidates = blue_transitions[last_blue]
            selected_blue = Counter(next_blue_candidates).most_common(1)[0][0]
        else:
            selected_blue = blue_freq.most_common(1)[0][0]
        all_reds = [n for nums in data.values() for n in nums[:6]]
        red_freq = Counter(all_reds)
        selected_reds = [n for n, _ in red_freq.most_common(6)]
        return sorted(selected_reds) + [selected_blue]

    def predict_association_rules(self, data):
        pair_counts = defaultdict(int)
        for nums in data.values():
            reds = nums[:6]
            for i in range(len(reds)):
                for j in range(i+1, len(reds)):
                    pair = tuple(sorted([reds[i], reds[j]]))
                    pair_counts[pair] += 1
        periods = sorted(data.keys())
        last_period = periods[-1]
        last_reds = data[last_period][:6]
        associated_scores = defaultdict(float)
        for num in range(1, 34):
            for last_num in last_reds:
                pair = tuple(sorted([num, last_num]))
                if pair in pair_counts:
                    associated_scores[num] += pair_counts[pair]
        all_reds = [n for nums in data.values() for n in nums[:6]]
        freq = Counter(all_reds)
        for num in range(1, 34):
            associated_scores[num] += freq.get(num, 0) * 0.5
        selected_reds = sorted(associated_scores.keys(), key=lambda x: associated_scores[x], reverse=True)[:6]
        all_blues = [data[p][6] for p in periods]
        selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_kmeans_clustering(self, data):
        all_reds = [n for nums in data.values() for n in nums[:6]]
        freq = Counter(all_reds)
        sorted_nums = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)
        cluster_size = len(sorted_nums) // 3
        high_freq = set(sorted_nums[:cluster_size])
        mid_freq = set(sorted_nums[cluster_size:2*cluster_size])
        low_freq = set(sorted_nums[2*cluster_size:])
        selected_reds = []
        selected_reds.extend(random.sample(list(high_freq), min(3, len(high_freq))))
        selected_reds.extend(random.sample(list(mid_freq), min(2, len(mid_freq))))
        selected_reds.extend(random.sample(list(low_freq), min(1, len(low_freq))))
        if len(selected_reds) < 6:
            remaining = [n for n in range(1, 34) if n not in selected_reds]
            remaining.sort(key=lambda x: freq[x], reverse=True)
            selected_reds.extend(remaining[:6-len(selected_reds)])
        selected_reds = selected_reds[:6]
        all_blues = [data[p][6] for p in sorted(data.keys())]
        selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_ac_value(self, data):
        def calculate_ac_value(nums):
            diffs = set()
            for i in range(len(nums)):
                for j in range(i+1, len(nums)):
                    diffs.add(abs(nums[j] - nums[i]))
            return len(diffs) - 5
        ac_values = []
        for nums in data.values():
            ac = calculate_ac_value(nums[:6])
            ac_values.append(ac)
        ac_freq = Counter(ac_values)
        target_ac = ac_freq.most_common(1)[0][0]
        all_reds = [n for nums in data.values() for n in nums[:6]]
        freq = Counter(all_reds)
        hot_numbers = [n for n, _ in freq.most_common(20)]
        best_combo = None
        best_diff = float('inf')
        for combo in combinations(hot_numbers, 6):
            ac = calculate_ac_value(list(combo))
            diff = abs(ac - target_ac)
            if diff < best_diff:
                best_diff = diff
                best_combo = combo
        if best_combo is None:
            best_combo = hot_numbers[:6]
        selected_reds = list(best_combo)
        all_blues = [data[p][6] for p in sorted(data.keys())]
        selected_blue = Counter(all_blues).most_common(1)[0][0]
        return sorted(selected_reds) + [selected_blue]

    def predict_chaos_attractor(self, data):
        periods = sorted(data.keys())
        last_period = periods[-1]
        last_reds = data[last_period][:6]
        selected_reds = []
        sigma, rho, beta = 10, 28, 8/3
        for i, num in enumerate(last_reds):
            x = num / 33.0
            dx = sigma * (x - x**2)
            new_num = int((x + dx * 0.1) * 33) % 33 + 1
            if new_num not in selected_reds:
                selected_reds.append(new_num)
        if len(selected_reds) < 6:
            all_reds = [n for nums in data.values() for n in nums[:6]]
            freq = Counter(all_reds)
            remaining = [n for n in range(1, 34) if n not in selected_reds]
            remaining.sort(key=lambda x: freq[x], reverse=True)
            selected_reds.extend(remaining[:6-len(selected_reds)])
        selected_reds = selected_reds[:6]
        last_blue = data[last_period][6]
        y = last_blue / 16.0
        dy = rho * y - y**2
        selected_blue = int((y + dy * 0.1) * 16) % 16 + 1
        return sorted(selected_reds) + [selected_blue]

    def predict_brownian_motion(self, data):
        periods = sorted(data.keys())
        last_period = periods[-1]
        last_reds = data[last_period][:6]
        selected_reds = []
        for num in last_reds:
            step = random.randint(-3, 3)
            new_num = max(1, min(33, num + step))
            if new_num not in selected_reds:
                selected_reds.append(new_num)
        if len(selected_reds) < 6:
            all_reds = [n for nums in data.values() for n in nums[:6]]
            freq = Counter(all_reds)
            remaining = [n for n in range(1, 34) if n not in selected_reds]
            remaining.sort(key=lambda x: freq[x], reverse=True)
            selected_reds.extend(remaining[:6-len(selected_reds)])
        selected_reds = selected_reds[:6]
        last_blue = data[last_period][6]
        blue_step = random.randint(-2, 2)
        selected_blue = max(1, min(16, last_blue + blue_step))
        return sorted(selected_reds) + [selected_blue]


if __name__ == '__main__':
    # 初始化数据文件
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "historical_data": {},
            "prediction_methods": [],
            "current_predictions": {},
            "performance_ranking": [],
            "eliminated_methods": [],
            "next_period": "2026017",
            "data_source": "",
            "last_update": "",
            "evaluation_periods": 0,
            "evaluation_note": ""
        }
        save_data(initial_data)
    
    # 启动服务
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
