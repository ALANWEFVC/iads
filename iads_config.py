#!/usr/bin/env python3
"""
IADS Production Configuration
生产级配置文件
"""

# 系统配置
SYSTEM_CONFIG = {
    # 基础设置
    'version': '1.0.0',
    'name': 'IADS Production System',
    'description': 'Integrated Adaptive Detection System',
    
    # 网络配置
    'controller_port': 6633,
    'openflow_version': '1.3',
    
    # 监控配置
    'packet_monitoring': {
        'enable_lldp': True,
        'enable_arp': True,
        'enable_icmp': True,
        'statistics_interval': 50  # 每N个包记录一次统计
    }
}

# 探测配置
PROBE_CONFIG = {
    # 探测调度
    'initial_probe_interval': 10,  # 初始探测间隔(秒)
    'min_probe_interval': 5,      # 最小探测间隔
    'max_probe_interval': 30,     # 最大探测间隔
    'max_concurrent_probes': 5,   # 最大并发探测数
    
    # 探测优先级
    'uncertainty_weight': 0.6,    # 不确定性权重
    'anomaly_weight': 0.4,        # 异常分数权重
    'time_decay_factor': 60,      # 时间衰减因子(秒)
    
    # 模拟探测设置
    'simulation_enabled': True,
    'base_success_rate': 0.85,
    'response_time_range': (0.001, 0.100)  # 响应时间范围(秒)
}

# 异常检测配置
ANOMALY_CONFIG = {
    # 检测阈值
    'alert_threshold': 0.6,       # 异常警报阈值
    'critical_threshold': 0.8,    # 严重异常阈值
    
    # 状态管理
    'history_size': 50,           # 保存的历史记录数量
    'metrics_window': 20,         # 性能指标窗口大小
    'success_rate_window': 10,    # 成功率计算窗口
    
    # 清理配置
    'anomaly_retention_time': 300,  # 异常记录保留时间(秒)
    'analysis_interval': 60,        # 异常分析间隔(秒)
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',              # 日志级别: DEBUG, INFO, WARNING, ERROR
    'enable_file_logging': True,  # 启用文件日志
    'log_directory': './logs',    # 日志目录
    'max_log_files': 10,          # 最大日志文件数
    'log_rotation_size': '10MB'   # 日志轮转大小
}

# 性能配置
PERFORMANCE_CONFIG = {
    # 主循环间隔
    'main_loop_interval': 25,     # 主循环间隔(秒)
    'topology_update_interval': 20,  # 拓扑更新间隔(秒)
    
    # 内存管理
    'max_entity_states': 1000,    # 最大实体状态数量
    'cleanup_interval': 300,      # 清理间隔(秒)
    
    # 统计配置
    'enable_detailed_stats': True,
    'stats_report_interval': 60   # 统计报告间隔(秒)
}

# 部署配置
DEPLOYMENT_CONFIG = {
    'environment': 'production',  # development, testing, production
    'auto_start_monitoring': True,
    'startup_delay': 3,           # 启动延迟(秒)
    'shutdown_timeout': 30,       # 关闭超时(秒)
}

# 导出所有配置
ALL_CONFIGS = {
    'system': SYSTEM_CONFIG,
    'probe': PROBE_CONFIG,
    'anomaly': ANOMALY_CONFIG,
    'logging': LOGGING_CONFIG,
    'performance': PERFORMANCE_CONFIG,
    'deployment': DEPLOYMENT_CONFIG
}

def get_config(section=None):
    """获取配置"""
    if section:
        return ALL_CONFIGS.get(section, {})
    return ALL_CONFIGS

def print_config_summary():
    """打印配置摘要"""
    print("🔧 IADS Production Configuration Summary")
    print("="*50)
    print(f"System: {SYSTEM_CONFIG['name']} v{SYSTEM_CONFIG['version']}")
    print(f"Environment: {DEPLOYMENT_CONFIG['environment']}")
    print(f"Controller Port: {SYSTEM_CONFIG['controller_port']}")
    print(f"Anomaly Threshold: {ANOMALY_CONFIG['alert_threshold']}")
    print(f"Probe Interval: {PROBE_CONFIG['initial_probe_interval']}s")
    print("="*50)

if __name__ == '__main__':
    print_config_summary()
