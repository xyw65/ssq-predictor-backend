# 智能预测实验室 - 部署教程

## 📋 项目结构

```
/output/
├── backend/          # Python后端服务
│   ├── app.py        # Flask主程序（直接入口）
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── vercel.json
│   └── render.yaml
├── app/              # React前端
│   ├── src/
│   ├── dist/         # 构建输出
│   └── ...
└── DEPLOY_GUIDE.md   # 本教程
```

## 🚀 部署方式一：Render（推荐）

Render提供免费的后端服务部署，适合个人项目。

### 步骤1：部署后端

1. 访问 [Render](https://render.com) 并注册账号
2. 点击 "New +" → "Web Service"
3. 连接你的GitHub仓库，或直接上传代码
4. 配置如下：
   - **Name**: `ssq-predictor-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 app:app`
5. 添加环境变量（可选）：
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.11.0`
6. 点击 "Create Web Service"
7. 等待部署完成，记录下你的服务URL（如 `https://ssq-predictor-backend.onrender.com`）

### 步骤2：部署前端

1. 在Render上点击 "New +" → "Static Site"
2. 连接同一仓库
3. 配置如下：
   - **Name**: `ssq-predictor-frontend`
   - **Build Command**: `cd app && npm install && npm run build`
   - **Publish Directory**: `app/dist`
4. 添加环境变量：
   - **Key**: `VITE_API_URL`
   - **Value**: `https://ssq-predictor-backend.onrender.com`（你的后端URL）
5. 点击 "Create Static Site"

### 步骤3：配置CORS（如果需要）

修改 `backend/app.py` 中的CORS配置：

```python
CORS(app, origins=["https://your-frontend-url.onrender.com"])
```

---

## 🚀 部署方式二：Vercel

Vercel适合部署前端，后端需要额外配置。

### 步骤1：部署后端

1. 访问 [Vercel](https://vercel.com) 并注册账号
2. 导入你的GitHub仓库
3. 在Vercel项目设置中：
   - **Framework Preset**: `Other`
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: `.`
   - **Install Command**: 留空
4. 添加环境变量：
   - `FLASK_ENV`: `production`
5. 部署

⚠️ **注意**: Vercel的免费版对Python后端有一些限制，可能不适合长时间运行的爬虫任务。

### 步骤2：部署前端

1. 在Vercel上创建新项目
2. 导入前端代码（`app`目录）
3. 配置：
   - **Framework Preset**: `Vite`
   - **Root Directory**: `app`
4. 添加环境变量：
   - `VITE_API_URL`: 你的后端URL
5. 部署

---

## 🚀 部署方式三：本地运行

适合开发和测试。

### 步骤1：启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

后端将在 `http://localhost:5000` 运行

### 步骤2：启动前端

```bash
cd app

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 运行

---

## 🐳 部署方式四：Docker

适合有服务器环境的用户。

### 构建并运行

```bash
cd backend

# 构建镜像
docker build -t ssq-predictor .

# 运行容器
docker run -p 5000:5000 ssq-predictor
```

---

## 📡 API接口说明

后端提供以下API：

### 1. 健康检查
```
GET /api/health
```

### 2. 获取数据
```
GET /api/data
```

### 3. 更新数据（爬取网页）
```
POST /api/update
Body: {"url": "https://www.55123.cn/zs/ssq_26.html"}
```

### 4. 执行预测
```
POST /api/predict
Body: {"method": "马尔可夫链转移"}  // 可选，不传则预测所有方法
```

### 5. 评估战绩
```
POST /api/evaluate
```

---

## ⚙️ 环境变量配置

### 前端 (.env 文件)

```
VITE_API_URL=http://localhost:5000  # 你的后端地址
```

### 后端

```
FLASK_ENV=production
PORT=5000
```

---

## 🔧 常见问题

### Q1: 更新数据失败？

- 检查目标网站是否可以访问
- 检查URL格式是否正确
- 查看后端日志获取详细错误信息

### Q2: 跨域错误？

- 确保后端CORS配置正确
- 检查前端API地址是否正确

### Q3: 战绩评估为0？

- 确保数据量足够（至少101期）
- 点击"评估战绩"按钮重新计算

### Q4: 前端无法连接后端？

- 检查 `VITE_API_URL` 是否设置正确
- 确保后端服务已启动
- 检查网络连接

### Q5: ModuleNotFoundError: No module named 'wsgi'

- 已修复：直接使用 `app:app` 作为入口，无需 wsgi.py
- 确保 render.yaml 中的 startCommand 是 `gunicorn --bind 0.0.0.0:$PORT app:app`

---

## 📞 技术支持

如有问题，请检查：
1. 后端日志输出
2. 浏览器开发者工具的网络请求
3. 环境变量配置

祝部署顺利！🎉
