"""IADS配置文件"""

# 指标定义
METRICS = {
    'RTT': 'rtt',
    'PLR': 'plr', 
    'BANDWIDTH': 'bandwidth',
    'LIVENESS': 'liveness'
}

# 系统配置
SYSTEM_CONFIG = {
    'top_k': 5,  # 每轮选择的任务数
    'probe_interval_default': 10.0,  # 默认探测间隔(秒)
    'probe_interval_min': 1.0,  # 最小探测间隔
    'probe_interval_max': 60.0,  # 最大探测间隔
    'sliding_window': 300.0,  # 滑动窗口大小(秒)
    'max_parallel_probes': 10  # 最大并行探测数
}

# 测量噪声配置
MEASUREMENT_NOISE = {
    'rtt': 1.0,          # RTT测量噪声方差
    'plr': 0.001,        # PLR测量噪声方差
    'bandwidth': 10.0,   # 带宽测量噪声方差
    'liveness': 1.0      # Liveness测量噪声方差
}

# 分布初始化参数
DISTRIBUTION_INIT = {
    'liveness': {
        'type': 'beta',
        'alpha': 1.0,
        'beta': 1.0
    },
    'rtt': {
        'type': 'gaussian',
        'mu': 10.0,
        'sigma2': 100.0
    },
    'plr': {
        'type': 'gaussian', 
        'mu': 0.01,
        'sigma2': 0.001
    },
    'bandwidth': {
        'type': 'gaussian',
        'mu': 100.0,
        'sigma2': 1000.0
    }
}

# APS配置
APS_CONFIG = {
    'max_uncertainty': 2.0,  # 最大不确定性
    'max_stability': 5.0,  # 最大稳定性
    'target_stability': 1.0,  # 目标稳定性
    'kp': 0.1,  # 比例控制增益
    'priority_weights': {
        'eig': 0.4,           # 预期信息增益权重
        'urgency': 0.3,       # 紧急度权重
        'policy_match': 0.2,  # 策略匹配度权重
        'event_trig': 0.1     # 事件触发权重
    }
}

# CMAB策略
CMAB_STRATEGIES = {
    'FOCUS_UNCERTAINTY': 'focus_uncertainty',
    'HIGHFREQ_UNSTABLE': 'highfreq_unstable', 
    'COVERAGE_BALANCER': 'coverage_balancer',
    'EVENT_TRIGGER': 'event_trigger'
}

# 事件阈值
EVENT_THRESHOLDS = {
    'liveness_threshold': 0.8,  # 存活性阈值
    'stability_threshold': 3.0,  # 稳定性阈值
    'rtt_spike_factor': 3.0,     # RTT峰值因子
    'max_recent_events': 100  # 最大最近事件数
}

# 奖励配置
REWARD_CONFIG = {
    'uncertainty_weight': 0.7,  # 不确定性权重
    'cost_weight': 0.3,  # 成本权重
    'max_uncertainty_reduction': 1.0  # 最大不确定性减少
}
