# IADS - Integrated Adaptive Detection System

🚀 **企业级SDN智能网络监控系统**

## 概述

IADS是一个基于Ryu SDN框架的智能网络监控和异常检测系统，提供：

- 🔍 **智能拓扑发现**：自动发现网络交换机和链路
- 📊 **实体状态管理**：跟踪网络实体的不确定性和稳定性
- 🎯 **异常检测**：实时分析和报告网络异常
- ⚡ **自适应探测**：基于优先级的智能探测调度
- 📈 **性能分析**：详细的统计和趋势分析

## 快速开始

### 1. 环境要求
- Python 3.7+
- Ryu SDN Framework
- OpenFlow 1.3支持的交换机
- (可选) Mininet用于测试

### 2. 安装依赖
```bash
pip install ryu
```

### 3. 启动系统
```bash
# 快速启动
./start_iads.sh

# 完整部署
./deploy_iads.sh

# 测试模式
./deploy_iads.sh test
```

### 4. 测试连接
```bash
# 在另一个终端启动测试拓扑
sudo mn --topo single,2 --controller remote,ip=127.0.0.1,port=6633 --switch ovsk,protocols=OpenFlow13

# 在Mininet中测试
mininet> pingall
```

## 系统架构

## 配置文件

系统配置在 `iads_config.py` 中：

```python
# 主要配置项
ANOMALY_CONFIG = {
    'alert_threshold': 0.6,      # 异常警报阈值
    'critical_threshold': 0.8,   # 严重异常阈值
}

PROBE_CONFIG = {
    'initial_probe_interval': 10, # 探测间隔
    'max_concurrent_probes': 5,   # 最大并发探测
}
```

## 命令参考

### 部署脚本
```bash
./deploy_iads.sh start    # 启动系统
./deploy_iads.sh test     # 测试模式
./deploy_iads.sh status   # 检查状态
./deploy_iads.sh config   # 显示配置
./deploy_iads.sh cleanup  # 清理文件
```

### 直接启动
```bash
# 基本启动
ryu-manager iads_main.py

# 详细日志
ryu-manager --verbose --observe-links iads_main.py

# 指定端口
ryu-manager --ofp-tcp-listen-port 6633 iads_main.py
```

## 监控和日志

- **日志目录**: `./logs/`
- **配置文件**: `iads_config.py`
- **主应用**: `iads_main.py`

### 日志级别
- **INFO**: 常规操作信息
- **WARNING**: 异常警报
- **ERROR**: 系统错误
- **DEBUG**: 详细调试信息

## 故障排除

### 常见问题

1. **端口已被占用**
   ```bash
   # 检查端口使用
   netstat -tuln | grep 6633
   
   # 杀死占用进程
   sudo pkill -f ryu-manager
   ```

2. **Mininet连接失败**
   ```bash
   # 清理Mininet
   sudo mn -c
   
   # 重启OVS
   sudo service openvswitch-switch restart
   ```

3. **Python依赖问题**
   ```bash
   # 重新安装Ryu
   pip uninstall ryu
   pip install ryu
   ```

## 性能优化

### 大规模网络
- 调整 `max_entity_states` 参数
- 增加 `probe_interval` 降低负载
- 启用日志轮转

### 高精度监控
- 降低 `alert_threshold`
- 增加 `history_size`
- 启用详细统计

## 开发和扩展

### 添加新的异常检测算法
```python
def custom_anomaly_detector(entity_state):
    # 自定义异常检测逻辑
    return anomaly_score
```

### 集成外部监控系统
```python
def send_to_external_system(anomaly_data):
    # 发送到外部监控系统
    pass
```

## 许可证

本项目基于开源许可证发布。

## 支持

如有问题或建议，请查看日志文件或联系开发团队。

---

🌟 **IADS - 智能网络的未来！**
