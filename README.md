# IADS - 集成自适应检测系统

# IADS - 集成自适应检测系统

## 📖 项目简介

IADS (Integrated Adaptive Detection System) 是一个基于Ryu SDN控制器的**智能网络监测框架**，专门用于软件定义网络中的自适应网络状态检测和异常监控。

**最新版本**: 使用 `iads_ultimate.py` 作为主程序，提供更稳定的L2转发和完整的IADS功能集成。

## 🚀 快速开始

### 方式1：使用Ryu控制器（推荐）

```bash
# 1. 激活conda环境
conda activate sdn2

# 2. 进入项目目录
cd /home/sdn/IADS/iads_ryu_app

# 3. 启动IADS Ultimate控制器
ryu-manager --verbose iads_ultimate.py

# 4. 在另一个终端启动Mininet
sudo python3 test_topology.py

## 🏗️ 系统架构

### 核心模块

```
┌─────────────────────────────────────────┐
│              IADS Main App              │
│         (Ryu SDN Controller)           │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
   ESM           UQ            APS
 (状态管理)    (不确定性)     (调度器)
    │             │             │
    └─────────────┼─────────────┘
                  │
        ┌─────────┼─────────┐
       PE                 RFU
   (探测执行)          (结果融合)
        │                 │
        └─────────┼───────┘
                  │
                 EM
             (事件管理)
```

### 模块说明

- **ESM (EntityStateManager)**: 实体状态管理器 - 管理网络实体状态
- **UQ (UncertaintyQuantifier)**: 不确定性量化器 - 计算状态不确定性
- **APS (ActiveProbingScheduler)**: 主动探测调度器 - 智能任务选择
- **PE (ProbeExecutor)**: 探测执行器 - 执行网络探测
- **RFU (ResultFusionUnit)**: 结果融合单元 - 处理探测结果
- **EM (EventManager)**: 事件管理器 - 异常检测和事件管理

## 🚀 使用方法

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 快速演示（推荐）

由于Ryu在某些环境下可能存在兼容性问题，我们提供了独立演示：

```bash
# 运行核心功能演示
python demo_standalone.py
```

### 3. REST API服务器

启动Web API服务器进行监控：

```bash
# 启动API服务器
python iads_rest_server.py

# 测试API接口
python test_api.py
```

### 4. 完整SDN环境（需要Ryu和Mininet）

```bash
# 1. 启动测试拓扑
sudo python3 test_topology.py

# 2. 启动IADS控制器（另一个终端）
./run.sh --with-rest

# 3. 监控系统状态
curl http://localhost:8080/iads/status
```

## 📊 演示结果

运行 `python demo_standalone.py` 后，您将看到：

### 系统初始化
- ✅ 6个网络实体（链路）
- ✅ 24个状态监控点
- ✅ 核心模块加载完成

### 不确定性量化
- 📊 生成探测任务池
- 📈 按EIG排序的任务优先级
- 🎯 智能任务选择策略

### 事件检测
- 🚨 实时异常检测
- 🔴 链路故障识别
- 📡 存活性监控

### 主动探测调度
- 🎲 多策略任务选择
- 📊 上下文感知决策
- ⚖️ 不确定性与成本权衡

## 🌐 REST API 接口

### 可用端点

```
GET  /                     - API文档
GET  /health              - 健康检查
GET  /iads/status         - 系统状态
GET  /iads/entities       - 实体列表
GET  /iads/events         - 事件列表
GET  /iads/tasks          - 任务列表
GET  /iads/statistics     - 统计信息
POST /iads/probe          - 手动探测
```

### 示例响应

#### 系统状态
```json
{
  "timestamp": "2025-05-23T10:14:36.327693",
  "status": "running",
  "entities": 6,
  "recent_events": 6,
  "modules_loaded": true
}
```

#### 实体列表
```json
{
  "total": 6,
  "entities": [
    {
      "id": "link-s1-s2",
      "is_core": true,
      "metrics": {
        "rtt": {"uncertainty": 1.2345, "stability": 0.1234},
        "plr": {"uncertainty": 2.3456, "stability": 0.2345}
      }
    }
  ]
}
```

## 🛠️ 技术栈

- **核心框架**: Ryu SDN Controller
- **科学计算**: NumPy, SciPy
- **Web框架**: Flask, Flask-RESTful
- **网络库**: eventlet, netaddr
- **测试框架**: pytest
- **可视化**: matplotlib

## 🎯 核心算法

### 1. 不确定性建模
- **Beta分布**: 建模二值状态（存活性）
- **高斯分布**: 建模连续值状态（RTT、带宽）

### 2. 自适应探测策略
- **多臂赌博机**: 动态策略选择
- **上下文感知**: 基于网络状态调整
- **预期信息增益**: 量化探测价值

### 3. 奖励机制
```
奖励 = 0.7 × 不确定性减少 - 0.3 × 探测成本
```

## 📈 系统特点

- ✅ **自适应**: 根据网络状态自动调整
- ✅ **智能**: 机器学习优化探测效率
- ✅ **实时**: 事件驱动的实时监测
- ✅ **可扩展**: 模块化设计易于扩展
- ✅ **可视化**: REST API和统计报告

## 🔧 故障排除

### Ryu安装问题
如果遇到Ryu安装失败，请使用独立演示：
```bash
python demo_standalone.py
```

### 端口占用问题
如果8080端口被占用，修改 `iads_rest_server.py` 中的端口：
```python
app.run(host='0.0.0.0', port=8081, debug=False)
```

### 依赖问题
确保安装所需依赖：
```bash
pip install numpy scipy flask flask-restful requests
```

## 📝 配置文件

主要配置在 `iads_ryu_app/config.py`：

```python
SYSTEM_CONFIG = {
    'top_k': 5,                    # 每轮选择任务数
    'probe_interval_default': 10.0, # 默认探测间隔
    'sliding_window': 300.0         # 滑动窗口大小
}

APS_CONFIG = {
    'max_uncertainty': 2.0,         # 最大不确定性
    'max_stability': 5.0,           # 最大稳定性
    'target_stability': 1.0         # 目标稳定性
}
```

## 🎓 学术价值

本项目实现了以下研究领域的前沿算法：
- **主动学习**: 智能样本选择
- **不确定性量化**: 贝叶斯状态估计
- **多臂赌博机**: 在线决策优化
- **SDN监控**: 软件定义网络管理

## 📄 许可证

MIT License

## 👥 贡献者

IADS Team

---

🚀 **开始使用**: `python demo_standalone.py`

📊 **监控系统**: `python iads_rest_server.py`

🔍 **查看API**: `http://localhost:8080/`
