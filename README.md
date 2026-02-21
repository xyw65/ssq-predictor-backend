# 智能预测实验室

> 支持AI建设 · 智能体协作 · 数据驱动决策

## 🎯 项目简介

这是一个基于20种高级数学算法的双色球预测系统，支持实时数据更新和战绩评估。

## 📁 项目结构

```
.
├── backend/          # Python Flask后端
│   ├── app.py        # 主程序（含爬虫+预测算法）
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── vercel.json
│   └── render.yaml
├── app/              # React前端
│   ├── src/
│   │   └── App.tsx   # 主界面
│   └── ...
├── start.sh          # 快速启动脚本
├── DEPLOY_GUIDE.md   # 部署教程
└── README.md         # 本文件
```

## 🚀 快速开始

### 方式1：一键启动（推荐）

```bash
./start.sh
```

### 方式2：手动启动

**后端：**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**前端：**
```bash
cd app
npm install
npm run dev
```

## 📡 API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/data` | GET | 获取所有数据 |
| `/api/update` | POST | 更新数据（爬取网页） |
| `/api/predict` | POST | 执行预测 |
| `/api/evaluate` | POST | 评估战绩 |

## 🎨 20种预测算法

1. **马尔可夫链转移** - 状态转移概率
2. **神经网络模式** - 模式识别
3. **蒙特卡洛模拟** - 随机采样
4. **遗传算法进化** - 优胜劣汰
5. **斐波那契黄金** - 黄金分割
6. **质数分布分析** - 数论规律
7. **周期性傅里叶** - 周期分析
8. **对称性镜像** - 对称模式
9. **连号斜连分析** - 相邻规律
10. **和值尾数分析** - 尾数规律
11. **等差等比数列** - 数列规律
12. **区间平衡理论** - 三区均衡
13. **奇偶平衡优化** - 奇偶均衡
14. **跨度优化选择** - 跨度分布
15. **蓝球周期分析** - 周期预测
16. **关联规则挖掘** - 号码关联
17. **聚类分析K均值** - 机器学习
18. **AC值优化选择** - 组合数学
19. **混沌吸引子** - 混沌理论
20. **布朗运动随机** - 随机过程

## 🏆 战绩排行榜

系统使用倒推验证法评估各方法的战绩：
- 总分 = 一等奖×1000 + 二等奖×100 + 三等奖×30 + 四等奖×10 + 五等奖×5 + 六等奖×1
- 战绩前10的方法会被保留用于预测
- 战绩较低的方法会被淘汰

## 🌐 部署

详见 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)

### 推荐平台

- **Render** - 免费，适合个人项目
- **Vercel** - 适合前端部署
- **Docker** - 适合自建服务器

## ⚙️ 环境变量

### 前端
```
VITE_API_URL=http://localhost:5000
```

### 后端
```
FLASK_ENV=production
PORT=5000
```

## 📄 许可证

MIT License

---

**支持AI智能体建设 · 数据驱动 · 科学决策**
