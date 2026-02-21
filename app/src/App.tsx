import { useState, useEffect } from 'react'
import './App.css'
import { 
  Trophy, 
  Database, 
  Globe, 
  Brain,
  Target,
  BarChart3,
  Zap,
  Activity,
  Layers,
  ArrowRightLeft,
  Divide,
  Repeat,
  Move,
  Calculator,
  Clock,
  Sparkles,
  Cpu,
  GitGraph,
  FunctionSquare,
  Sigma,
  Binary,
  Waves,
  Shuffle,
  Dices,
  Award,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Server
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'

// API配置 - 修改这里为你的后端地址
// 本地开发: http://localhost:5000
// Vercel部署: https://your-backend.vercel.app
// Render部署: https://your-backend.onrender.com
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// 预测方法图标映射
const methodIcons: Record<string, React.ReactNode> = {
  "马尔可夫链转移": <GitGraph className="w-5 h-5 text-purple-500" />,
  "神经网络模式": <Cpu className="w-5 h-5 text-cyan-500" />,
  "蒙特卡洛模拟": <Dices className="w-5 h-5 text-green-500" />,
  "遗传算法进化": <FunctionSquare className="w-5 h-5 text-orange-500" />,
  "斐波那契黄金": <Sigma className="w-5 h-5 text-yellow-500" />,
  "质数分布分析": <Binary className="w-5 h-5 text-red-500" />,
  "周期性傅里叶": <Waves className="w-5 h-5 text-blue-500" />,
  "对称性镜像": <ArrowRightLeft className="w-5 h-5 text-pink-500" />,
  "连号斜连分析": <Repeat className="w-5 h-5 text-indigo-500" />,
  "和值尾数分析": <Calculator className="w-5 h-5 text-teal-500" />,
  "等差等比数列": <BarChart3 className="w-5 h-5 text-lime-500" />,
  "区间平衡理论": <Layers className="w-5 h-5 text-amber-500" />,
  "奇偶平衡优化": <Divide className="w-5 h-5 text-rose-500" />,
  "跨度优化选择": <Move className="w-5 h-5 text-sky-500" />,
  "蓝球周期分析": <Clock className="w-5 h-5 text-violet-500" />,
  "关联规则挖掘": <Activity className="w-5 h-5 text-emerald-500" />,
  "聚类分析K均值": <Shuffle className="w-5 h-5 text-fuchsia-500" />,
  "AC值优化选择": <Zap className="w-5 h-5 text-amber-400" />,
  "混沌吸引子": <Waves className="w-5 h-5 text-cyan-400" />,
  "布朗运动随机": <Activity className="w-5 h-5 text-slate-400" />,
}

// 数据类型定义
interface PredictionRecord {
  method: string
  total: number
  score: number
  first_prize: number
  second_prize: number
  third_prize: number
  fourth_prize: number
  fifth_prize: number
  sixth_prize: number
  red_hits: number
  blue_hits: number
  avg_red_hits: number
  avg_blue_hits: number
}

interface EliminatedMethod {
  method: string
  score: number
  reason: string
}

interface SSQData {
  historical_data: Record<string, number[]>
  prediction_methods: string[]
  current_predictions: Record<string, number[]>
  performance_ranking: PredictionRecord[]
  eliminated_methods: EliminatedMethod[]
  next_period: string
  data_source: string
  last_update: string
  evaluation_periods: number
  evaluation_note: string
}

function App() {
  const [data, setData] = useState<SSQData | null>(null)
  const [dataUrl, setDataUrl] = useState('https://www.55123.cn/zs/ssq_26.html')
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [evaluating, setEvaluating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  // 加载数据
  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/data`)
      if (!response.ok) {
        throw new Error('后端服务未启动，请检查API配置')
      }
      const data = await response.json()
      setData(data)
      setError(null)
    } catch (err: any) {
      setError('数据加载失败: ' + err.message)
      // 尝试加载本地静态数据作为后备
      try {
        const localResponse = await fetch('/ssq_data.json')
        if (localResponse.ok) {
          const localData = await localResponse.json()
          setData(localData)
          setMessage('已加载本地静态数据，部分功能可能不可用')
        }
      } catch {
        // 忽略本地数据加载错误
      }
    } finally {
      setLoading(false)
    }
  }

  // 更新数据
  const handleUpdateData = async () => {
    try {
      setUpdating(true)
      setMessage(null)
      
      const response = await fetch(`${API_BASE_URL}/api/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: dataUrl })
      })
      
      const result = await response.json()
      
      if (result.success) {
        setMessage(`✅ ${result.message}`)
        // 重新加载数据
        await fetchData()
      } else {
        setError(`❌ 更新失败: ${result.message}`)
      }
    } catch (err: any) {
      setError('更新失败: ' + err.message)
    } finally {
      setUpdating(false)
    }
  }

  // 评估战绩
  const handleEvaluate = async () => {
    try {
      setEvaluating(true)
      setMessage(null)
      
      const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      const result = await response.json()
      
      if (result.success) {
        setMessage(`✅ 评估完成！共评估 ${result.total_evaluated} 期数据`)
        // 重新加载数据
        await fetchData()
      } else {
        setError(`❌ 评估失败: ${result.message}`)
      }
    } catch (err: any) {
      setError('评估失败: ' + err.message)
    } finally {
      setEvaluating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Brain className="w-16 h-16 text-cyan-400 animate-pulse mx-auto mb-4" />
          <p className="text-cyan-400 text-lg">智能预测系统加载中...</p>
        </div>
      </div>
    )
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <Alert variant="destructive" className="max-w-md">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!data) return null

  const latestPeriod = Object.keys(data.historical_data).sort().pop() || ''
  const latestNumbers = data.historical_data[latestPeriod]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <Brain className="w-10 h-10 text-cyan-400" />
                <Sparkles className="w-4 h-4 text-yellow-400 absolute -top-1 -right-1 animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                  智能预测实验室
                </h1>
                <p className="text-xs text-slate-400">支持AI建设 · 智能体协作 · 数据驱动决策</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="border-cyan-500/50 text-cyan-400">
                <Database className="w-3 h-3 mr-1" />
                {Object.keys(data.historical_data).length} 期数据
              </Badge>
              <Badge variant="outline" className="border-purple-500/50 text-purple-400">
                <Target className="w-3 h-3 mr-1" />
                预测: {data.next_period}期
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* 消息提示 */}
        {message && (
          <Alert className="mb-6 bg-green-500/10 border-green-500/30">
            <AlertDescription className="text-green-200">{message}</AlertDescription>
          </Alert>
        )}
        
        {error && !message && (
          <Alert className="mb-6 bg-red-500/10 border-red-500/30">
            <AlertDescription className="text-red-200">{error}</AlertDescription>
          </Alert>
        )}

        {/* 数据输入区域 */}
        <Card className="mb-6 bg-slate-800/50 border-slate-700/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Globe className="w-5 h-5 text-cyan-400" />
              数据源配置
            </CardTitle>
            <CardDescription className="text-slate-400">
              输入历史数据网址，系统将自动获取最新开奖记录并更新预测模型
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3 flex-wrap">
              <Input
                value={dataUrl}
                onChange={(e) => setDataUrl(e.target.value)}
                placeholder="请输入数据来源网址"
                className="flex-1 min-w-[300px] bg-slate-900/50 border-slate-700 text-white"
              />
              <Button 
                onClick={handleUpdateData}
                disabled={updating}
                className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600"
              >
                {updating ? (
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Database className="w-4 h-4 mr-2" />
                )}
                {updating ? '更新中...' : '更新数据'}
              </Button>
              <Button 
                onClick={handleEvaluate}
                disabled={evaluating}
                variant="outline"
                className="border-amber-500/50 text-amber-400 hover:bg-amber-500/10"
              >
                {evaluating ? (
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Server className="w-4 h-4 mr-2" />
                )}
                {evaluating ? '评估中...' : '评估战绩'}
              </Button>
            </div>
            
            {/* API配置提示 */}
            <div className="mt-4 p-3 rounded bg-slate-900/50 text-xs text-slate-500">
              <div className="flex items-center gap-2 mb-1">
                <Server className="w-4 h-4" />
                <span className="font-medium">后端API配置</span>
              </div>
              <div>当前API地址: {API_BASE_URL}</div>
              <div className="mt-1 text-slate-600">
                如需修改，请设置环境变量 VITE_API_URL 或修改代码中的 API_BASE_URL
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 战绩说明 */}
        <Alert className="mb-6 bg-amber-500/10 border-amber-500/30">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <AlertDescription className="text-amber-200">
            <span className="font-bold">战绩评估说明：</span>
            使用倒推验证法（前100期预测第101期），共评估 {data.evaluation_periods || 0} 期数据。
            总分 = 一等奖×1000 + 二等奖×100 + 三等奖×30 + 四等奖×10 + 五等奖×5 + 六等奖×1
          </AlertDescription>
        </Alert>

        {/* 最新开奖 */}
        <Card className="mb-6 bg-slate-800/50 border-slate-700/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-400" />
              最新开奖结果
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-6 flex-wrap">
              <div className="text-3xl font-bold text-slate-300">{latestPeriod}期</div>
              <div className="flex items-center gap-2">
                {latestNumbers?.slice(0, 6).map((num, i) => (
                  <div 
                    key={i}
                    className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center text-white font-bold shadow-lg shadow-red-500/30"
                  >
                    {num.toString().padStart(2, '0')}
                  </div>
                ))}
                <div className="mx-2 text-slate-500">|</div>
                <div 
                  className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/30"
                >
                  {latestNumbers?.[6].toString().padStart(2, '0')}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="predictions" className="space-y-4">
          <TabsList className="bg-slate-800/50 border border-slate-700/50">
            <TabsTrigger value="predictions" className="data-[state=active]:bg-cyan-500/20">
              <Target className="w-4 h-4 mr-2" />
              战绩前10预测
            </TabsTrigger>
            <TabsTrigger value="ranking" className="data-[state=active]:bg-purple-500/20">
              <Trophy className="w-4 h-4 mr-2" />
              战绩排行
            </TabsTrigger>
            <TabsTrigger value="eliminated" className="data-[state=active]:bg-red-500/20">
              <XCircle className="w-4 h-4 mr-2" />
              淘汰方法
            </TabsTrigger>
            <TabsTrigger value="data" className="data-[state=active]:bg-green-500/20">
              <Database className="w-4 h-4 mr-2" />
              历史数据
            </TabsTrigger>
          </TabsList>

          {/* 预测结果标签页 */}
          <TabsContent value="predictions">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {data.performance_ranking?.map((record, index) => {
                const prediction = data.current_predictions?.[record.method]
                if (!prediction) return null
                
                const reds = prediction.slice(0, 6)
                const blue = prediction[6]
                
                return (
                  <Card key={record.method} className="bg-slate-800/50 border-slate-700/50 hover:border-cyan-500/30 transition-colors prediction-card">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                            index < 3 ? 'bg-gradient-to-br from-yellow-400 to-orange-500' : 'bg-gradient-to-br from-cyan-500 to-purple-500'
                          }`}>
                            {index + 1}
                          </div>
                          <div className="flex items-center gap-2">
                            {methodIcons[record.method]}
                            <CardTitle className="text-base">{record.method}</CardTitle>
                          </div>
                        </div>
                        <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
                          <Award className="w-3 h-3 mr-1" />
                          战绩: {record.score}分
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-2 mb-3">
                        {reds.map((num, i) => (
                          <div 
                            key={i}
                            className="w-8 h-8 rounded-full bg-gradient-to-br from-red-500/80 to-red-700/80 flex items-center justify-center text-white text-sm font-bold"
                          >
                            {num.toString().padStart(2, '0')}
                          </div>
                        ))}
                        <div className="mx-1 text-slate-600">|</div>
                        <div 
                          className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500/80 to-blue-700/80 flex items-center justify-center text-white text-sm font-bold"
                        >
                          {blue.toString().padStart(2, '0')}
                        </div>
                      </div>
                      <div className="flex gap-3 text-xs text-slate-400">
                        <span>四等奖: {record.fourth_prize}次</span>
                        <span>五等奖: {record.fifth_prize}次</span>
                        <span>六等奖: {record.sixth_prize}次</span>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          {/* 战绩排行标签页 */}
          <TabsContent value="ranking">
            <Card className="bg-slate-800/50 border-slate-700/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-yellow-400" />
                  预测方法战绩排行榜
                </CardTitle>
                <CardDescription className="text-slate-400">
                  基于倒推验证法评估 {data.evaluation_periods || 0} 期数据，按综合得分排序
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.performance_ranking?.map((record, index) => (
                    <div key={record.method} className="flex items-center gap-4 p-3 rounded-lg bg-slate-900/50">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                        index < 3 ? 'bg-gradient-to-br from-yellow-400 to-orange-500' : 'bg-gradient-to-br from-cyan-500 to-purple-500'
                      }`}>
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          {methodIcons[record.method]}
                          <span className="font-medium">{record.method}</span>
                        </div>
                        <div className="flex gap-4 text-xs text-slate-400">
                          <span className="text-amber-400">总分: {record.score}</span>
                          <span>四等奖: {record.fourth_prize}次</span>
                          <span>五等奖: {record.fifth_prize}次</span>
                          <span>六等奖: {record.sixth_prize}次</span>
                          <span>蓝球命中: {record.blue_hits}个</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-amber-400">
                          {record.score}
                        </div>
                        <div className="text-xs text-slate-500">综合得分</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 淘汰方法标签页 */}
          <TabsContent value="eliminated">
            <Card className="bg-slate-800/50 border-slate-700/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-400">
                  <XCircle className="w-5 h-5" />
                  已淘汰的预测方法
                </CardTitle>
                <CardDescription className="text-slate-400">
                  以下方法因战绩较低已被淘汰（共{data.eliminated_methods?.length || 0}种）
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {data.eliminated_methods?.map((item) => (
                    <div key={item.method} className="flex items-center gap-3 p-3 rounded-lg bg-slate-900/30 border border-red-500/20">
                      {methodIcons[item.method]}
                      <div className="flex-1">
                        <div className="font-medium text-slate-400">{item.method}</div>
                        <div className="text-xs text-red-400/70">{item.reason} · 得分: {item.score}</div>
                      </div>
                      <XCircle className="w-5 h-5 text-red-500/50" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 历史数据标签页 */}
          <TabsContent value="data">
            <Card className="bg-slate-800/50 border-slate-700/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="w-5 h-5 text-green-400" />
                  历史开奖数据
                </CardTitle>
                <CardDescription className="text-slate-400">
                  共 {Object.keys(data.historical_data).length} 期开奖记录
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-96 overflow-y-auto">
                  {Object.entries(data.historical_data).sort().reverse().map(([period, nums]) => (
                    <div key={period} className="p-2 rounded bg-slate-900/50 text-center">
                      <div className="text-xs text-slate-400 mb-1">{period}</div>
                      <div className="flex justify-center gap-1 flex-wrap">
                        {nums.slice(0, 6).map((n, i) => (
                          <span key={i} className="text-xs text-red-400">{n.toString().padStart(2, '0')}</span>
                        ))}
                        <span className="text-xs text-blue-400">+{nums[6].toString().padStart(2, '0')}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <Separator className="my-6 bg-slate-700/50" />

        {/* 术语说明 */}
        <Card className="bg-slate-800/30 border-slate-700/30">
          <CardHeader>
            <CardTitle className="text-sm text-slate-400">术语说明</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs text-slate-500">
              <div><span className="text-cyan-400">马尔可夫链:</span> 基于状态转移概率预测</div>
              <div><span className="text-cyan-400">蒙特卡洛:</span> 随机采样模拟</div>
              <div><span className="text-cyan-400">遗传算法:</span> 优胜劣汰进化</div>
              <div><span className="text-cyan-400">斐波那契:</span> 黄金分割规律</div>
              <div><span className="text-cyan-400">质数分布:</span> 数学质数规律</div>
              <div><span className="text-cyan-400">周期性:</span> 号码出现周期</div>
              <div><span className="text-cyan-400">对称性:</span> 镜像对称模式</div>
              <div><span className="text-cyan-400">AC值:</span> 号码差值复杂度</div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <footer className="mt-8 text-center text-xs text-slate-600">
          <p>智能预测实验室 - 数据来源: {data.data_source || '未配置'}</p>
          <p className="mt-1">最后更新: {data.last_update || '未知'} | 本预测仅供参考，彩票有风险，投注需谨慎</p>
          <p className="mt-2 text-slate-700">支持AI智能体建设 · 数据驱动 · 科学决策</p>
        </footer>
      </main>
    </div>
  )
}

export default App
