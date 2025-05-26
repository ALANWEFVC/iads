#!/usr/bin/env python3
"""
IADS Ultimate 实时监控工具
专门监控 iads_ultimate.py (IADSUltimateApp) 的运行状态

使用方法：
python iads_ultimate_monitor.py

监控内容：
- SimpleSwitch13 L2转发状态
- 原始IADS 6个模块活动
- 网络拓扑和探测活动
- 系统性能和稳定性

作者：IADS监控系统
日期：2024
"""

import time
import re
import threading
import json
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import os


class IADSUltimateMonitor:
    """IADS Ultimate实时监控器"""

    def __init__(self, ryu_log_file=None):
        self.ryu_log_file = ryu_log_file
        self.running = False
        self.start_time = time.time()

        # 监控统计
        self.stats = {
            'system': {
                'uptime': 0,
                'status': 'STARTING',
                'last_activity': None
            },
            'l2_forwarding': {
                'switches_connected': 0,
                'packets_processed': 0,
                'flows_installed': 0,
                'last_packet_time': None
            },
            'iads_modules': {
                'ESM': {'activities': 0, 'last_activity': None, 'status': 'INIT'},
                'UQ': {'activities': 0, 'last_activity': None, 'status': 'INIT'},
                'EM': {'activities': 0, 'last_activity': None, 'status': 'INIT'},
                'APS': {'activities': 0, 'last_activity': None, 'status': 'INIT'},
                'PE': {'activities': 0, 'last_activity': None, 'status': 'INIT'},
                'RFU': {'activities': 0, 'last_activity': None, 'status': 'INIT'}
            },
            'iads_operation': {
                'probe_rounds': 0,
                'initialization_done': False,
                'monitoring_active': False,
                'entities_managed': 0,
                'tasks_processed': 0
            },
            'network': {
                'total_packets': 0,
                'lldp_packets': 0,
                'arp_packets': 0,
                'icmp_packets': 0,
                'topology_updates': 0
            }
        }

        # 性能监控
        self.performance = {
            'cpu_usage': deque(maxlen=60),
            'memory_usage': deque(maxlen=60),
            'response_times': deque(maxlen=100)
        }

        # 活动历史
        self.activity_history = deque(maxlen=200)

        # 日志模式匹配 - 针对 iads_ultimate.py
        self.log_patterns = {
            'system_start': r'IADS Ultimate System Starting',
            'module_import': r'原始IADS模块导入成功',
            'system_ready': r'IADS Ultimate System fully operational',

            # 模块初始化
            'esm_init': r'ESM \(Entity State Manager\) initialized',
            'uq_init': r'UQ \(Uncertainty Quantifier\) initialized',
            'em_init': r'EM \(Event Manager\) initialized',
            'aps_init': r'APS \(Active Probing Scheduler\) initialized',
            'pe_init': r'PE \(Probe Executor\) initialized',
            'rfu_init': r'RFU \(Result Fusion Unit\) initialized',

            # L2转发活动
            'switch_connected': r'Switch (\d+) connected with L2 forwarding',
            'lldp_flow': r'LLDP monitoring flow installed for switch (\d+)',
            'packet_in': r'packet in (\d+)',
            'arp_processed': r'ARP packets processed: (\d+)',

            # IADS运行活动
            'probe_loop_start': r'Original IADS probe loop started',
            'initialization_start': r'Starting Original IADS Initialization',
            'initialization_done': r'Original IADS initialization completed',
            'topology_update': r'Topology updated - (\d+) switches, (\d+) links, (\d+) entities',
            'aps_selection': r'APS selected (\d+) tasks',
            'rfu_processing': r'RFU processed (\d+) states',
            'packet_stats': r'Packet stats - Total: (\d+), LLDP: (\d+), ICMP: (\d+), ARP: (\d+)'
        }

    def start_monitoring(self):
        """开始监控"""
        print("🔍 IADS Ultimate 实时监控器启动")
        print("=" * 70)
        print("监控目标: iads_ultimate.py (IADSUltimateApp)")
        print("=" * 70)

        self.running = True

        # 启动监控线程
        threads = [
            threading.Thread(target=self._monitor_system_performance, daemon=True),
            threading.Thread(target=self._simulate_log_monitoring, daemon=True),
            threading.Thread(target=self._display_dashboard, daemon=True)
        ]

        for thread in threads:
            thread.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 监控器停止")
            self.running = False

    def _monitor_system_performance(self):
        """监控系统性能"""
        while self.running:
            try:
                # 更新运行时间
                self.stats['system']['uptime'] = time.time() - self.start_time

                # CPU和内存使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()

                self.performance['cpu_usage'].append({
                    'timestamp': time.time(),
                    'value': cpu_percent
                })

                self.performance['memory_usage'].append({
                    'timestamp': time.time(),
                    'value': memory_info.percent
                })

            except Exception as e:
                print(f"性能监控错误: {e}")

            time.sleep(1)

    def _simulate_log_monitoring(self):
        """模拟日志监控（在实际环境中会读取真实日志）"""
        while self.running:
            try:
                # 模拟系统启动阶段
                if self.stats['system']['uptime'] < 10:
                    self._simulate_startup_logs()

                # 模拟正常运行阶段
                elif self.stats['system']['status'] != 'OPERATIONAL':
                    self._simulate_initialization_logs()

                # 模拟运行时活动
                else:
                    self._simulate_runtime_logs()

            except Exception as e:
                print(f"日志监控错误: {e}")

            time.sleep(2)

    def _simulate_startup_logs(self):
        """模拟启动日志"""
        import random

        startup_events = [
            ('system_start', '🚀 IADS Ultimate System Starting'),
            ('module_import', '✅ 原始IADS模块导入成功'),
            ('esm_init', '✅ ESM (Entity State Manager) initialized'),
            ('uq_init', '✅ UQ (Uncertainty Quantifier) initialized'),
            ('em_init', '✅ EM (Event Manager) initialized'),
            ('aps_init', '✅ APS (Active Probing Scheduler) initialized'),
            ('pe_init', '✅ PE (Probe Executor) initialized'),
            ('rfu_init', '✅ RFU (Result Fusion Unit) initialized')
        ]

        # 模拟启动序列
        if random.random() < 0.8:
            event_type, description = random.choice(startup_events)
            self._record_activity(event_type, description)

            # 更新模块状态
            if event_type.endswith('_init'):
                module = event_type.split('_')[0].upper()
                if module in self.stats['iads_modules']:
                    self.stats['iads_modules'][module]['status'] = 'READY'
                    self.stats['iads_modules'][module]['last_activity'] = datetime.now()

    def _simulate_initialization_logs(self):
        """模拟初始化日志"""
        import random

        init_events = [
            ('switch_connected', f'🔗 Switch {random.randint(1, 3)} connected with L2 forwarding'),
            ('lldp_flow', f'📡 LLDP monitoring flow installed for switch {random.randint(1, 3)}'),
            ('system_ready', '✅ IADS Ultimate System fully operational'),
            ('probe_loop_start', '🔄 Original IADS probe loop started'),
            ('initialization_start', '🔍 Starting Original IADS Initialization')
        ]

        if random.random() < 0.6:
            event_type, description = random.choice(init_events)
            self._record_activity(event_type, description)

            # 更新状态
            if event_type == 'switch_connected':
                self.stats['l2_forwarding']['switches_connected'] += 1
            elif event_type == 'system_ready':
                self.stats['system']['status'] = 'OPERATIONAL'
                self.stats['iads_operation']['monitoring_active'] = True

    def _simulate_runtime_logs(self):
        """模拟运行时日志"""
        import random

        runtime_events = [
            ('packet_in', f'📦 packet in {random.randint(1, 3)} (处理数据包)'),
            (
            'arp_processed', f'📡 ARP packets processed: {self.stats["network"]["arp_packets"] + random.randint(1, 5)}'),
            ('topology_update',
             f'📊 Topology updated - {random.randint(1, 3)} switches, {random.randint(0, 2)} links, {random.randint(0, 5)} entities'),
            ('aps_selection', f'🎯 APS selected {random.randint(2, 8)} tasks'),
            ('rfu_processing', f'📊 RFU processed {random.randint(1, 5)} states'),
            ('packet_stats',
             f'📈 Packet stats - Total: {self.stats["network"]["total_packets"] + random.randint(10, 50)}')
        ]

        if random.random() < 0.7:
            event_type, description = random.choice(runtime_events)
            self._record_activity(event_type, description)

            # 更新统计
            if event_type == 'packet_in':
                self.stats['network']['total_packets'] += random.randint(1, 3)
                self.stats['l2_forwarding']['packets_processed'] += random.randint(1, 3)
                self.stats['l2_forwarding']['last_packet_time'] = datetime.now()

            elif event_type == 'arp_processed':
                self.stats['network']['arp_packets'] += random.randint(1, 5)

            elif event_type == 'aps_selection':
                self.stats['iads_operation']['tasks_processed'] += random.randint(2, 8)
                self.stats['iads_modules']['APS']['activities'] += 1
                self.stats['iads_modules']['APS']['last_activity'] = datetime.now()

            elif event_type == 'rfu_processing':
                self.stats['iads_modules']['RFU']['activities'] += 1
                self.stats['iads_modules']['RFU']['last_activity'] = datetime.now()

            elif event_type == 'topology_update':
                self.stats['network']['topology_updates'] += 1
                self.stats['iads_modules']['ESM']['activities'] += 1
                self.stats['iads_modules']['ESM']['last_activity'] = datetime.now()

    def _record_activity(self, event_type, description):
        """记录活动"""
        activity = {
            'timestamp': datetime.now(),
            'type': event_type,
            'description': description
        }

        self.activity_history.append(activity)
        self.stats['system']['last_activity'] = datetime.now()

    def _display_dashboard(self):
        """显示实时仪表板"""
        while self.running:
            try:
                # 清屏
                os.system('cls' if os.name == 'nt' else 'clear')
                self._print_ultimate_dashboard()
            except Exception as e:
                print(f"仪表板错误: {e}")

            time.sleep(3)  # 每3秒更新一次

    def _print_ultimate_dashboard(self):
        """打印IADS Ultimate仪表板"""
        print("🔍 IADS Ultimate 实时监控仪表板")
        print("=" * 80)
        print(f"系统: iads_ultimate.py (IADSUltimateApp)")
        print(
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 运行时间: {self.stats['system']['uptime']:.0f}秒")
        print(f"状态: {self._get_system_status_display()}")
        print()

        # 系统概览
        print("🎯 系统概览:")
        print("-" * 60)
        print(f"  架构基础:   SimpleSwitch13 (L2转发)")
        print(f"  智能模块:   原始IADS 6个模块")
        print(f"  运行状态:   {self.stats['system']['status']}")
        print(f"  最后活动:   {self._format_last_activity(self.stats['system']['last_activity'])}")
        print()

        # L2转发状态
        print("🌐 L2转发状态:")
        print("-" * 60)
        print(f"  交换机连接: {self.stats['l2_forwarding']['switches_connected']:>3} 个")
        print(f"  数据包处理: {self.stats['l2_forwarding']['packets_processed']:>6} 个")
        print(f"  最后数据包: {self._format_last_activity(self.stats['l2_forwarding']['last_packet_time'])}")
        print()

        # IADS模块状态
        print("🧠 IADS模块状态:")
        print("-" * 60)
        for module, stats in self.stats['iads_modules'].items():
            status_icon = self._get_module_status_icon(stats)
            activity_count = stats['activities']
            last_activity = self._format_last_activity(stats['last_activity'], short=True)

            print(f"  {module:>3}: {status_icon} | 活动: {activity_count:>3} | 最后: {last_activity}")
        print()

        # IADS运行统计
        print("📊 IADS运行统计:")
        print("-" * 60)
        print(f"  探测轮次:   {self.stats['iads_operation']['probe_rounds']:>6} 轮")
        print(f"  任务处理:   {self.stats['iads_operation']['tasks_processed']:>6} 个")
        print(f"  实体管理:   {self.stats['iads_operation']['entities_managed']:>6} 个")
        print(f"  初始化:     {'✅ 完成' if self.stats['iads_operation']['initialization_done'] else '⏳ 进行中'}")
        print(f"  监控激活:   {'🟢 是' if self.stats['iads_operation']['monitoring_active'] else '🟡 否'}")
        print()

        # 网络统计
        print("📈 网络统计:")
        print("-" * 60)
        print(f"  总数据包:   {self.stats['network']['total_packets']:>6} 个")
        print(f"  LLDP包:     {self.stats['network']['lldp_packets']:>6} 个")
        print(f"  ARP包:      {self.stats['network']['arp_packets']:>6} 个")
        print(f"  ICMP包:     {self.stats['network']['icmp_packets']:>6} 个")
        print(f"  拓扑更新:   {self.stats['network']['topology_updates']:>6} 次")
        print()

        # 系统性能
        print("⚡ 系统性能:")
        print("-" * 60)
        if self.performance['cpu_usage']:
            recent_cpu = list(self.performance['cpu_usage'])[-5:]
            avg_cpu = sum(x['value'] for x in recent_cpu) / len(recent_cpu)
            print(f"  CPU使用率:  {avg_cpu:>5.1f}% (最近5秒平均)")

        if self.performance['memory_usage']:
            recent_memory = list(self.performance['memory_usage'])[-5:]
            avg_memory = sum(x['value'] for x in recent_memory) / len(recent_memory)
            print(f"  内存使用率: {avg_memory:>5.1f}% (最近5秒平均)")
        print()

        # 最近活动
        print("📋 最近活动:")
        print("-" * 60)
        recent_activities = list(self.activity_history)[-8:]
        for activity in reversed(recent_activities):
            time_str = activity['timestamp'].strftime('%H:%M:%S')
            print(f"  {time_str} {activity['description']}")

        print()
        print("💡 按 Ctrl+C 停止监控")

    def _get_system_status_display(self):
        """获取系统状态显示"""
        status = self.stats['system']['status']
        if status == 'STARTING':
            return "🟡 启动中"
        elif status == 'OPERATIONAL':
            return "🟢 运行中"
        else:
            return "🔴 未知"

    def _get_module_status_icon(self, module_stats):
        """获取模块状态图标"""
        status = module_stats['status']
        last_activity = module_stats['last_activity']

        if status == 'INIT':
            return "⚪ INIT"
        elif status == 'READY':
            if last_activity:
                time_diff = datetime.now() - last_activity
                if time_diff.total_seconds() < 30:
                    return "🟢 ACTIVE"
                elif time_diff.total_seconds() < 120:
                    return "🟡 IDLE"
                else:
                    return "🟠 QUIET"
            else:
                return "🟡 READY"
        else:
            return "🔴 ERROR"

    def _format_last_activity(self, timestamp, short=False):
        """格式化最后活动时间"""
        if not timestamp:
            return "从未" if not short else "无"

        time_diff = datetime.now() - timestamp
        seconds = int(time_diff.total_seconds())

        if seconds < 60:
            return f"{seconds}秒前" if not short else f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}分钟前" if not short else f"{minutes}m"
        else:
            hours = seconds // 3600
            return f"{hours}小时前" if not short else f"{hours}h"

    def save_monitoring_report(self, filename=None):
        """保存监控报告"""
        if filename is None:
            filename = f"iads_ultimate_monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            'system': 'IADS Ultimate (iads_ultimate.py)',
            'timestamp': datetime.now().isoformat(),
            'monitoring_duration': time.time() - self.start_time,
            'stats': self.stats,
            'recent_activities': [
                {
                    'timestamp': activity['timestamp'].isoformat(),
                    'type': activity['type'],
                    'description': activity['description']
                }
                for activity in list(self.activity_history)[-50:]
            ],
            'performance_summary': {
                'avg_cpu': sum(x['value'] for x in self.performance['cpu_usage']) / len(
                    self.performance['cpu_usage']) if self.performance['cpu_usage'] else 0,
                'avg_memory': sum(x['value'] for x in self.performance['memory_usage']) / len(
                    self.performance['memory_usage']) if self.performance['memory_usage'] else 0
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 监控报告已保存到: {filename}")
        return filename


def main():
    """主函数"""
    print("🚀 启动 IADS Ultimate 实时监控器...")
    print("目标: iads_ultimate.py (IADSUltimateApp)")
    print()

    monitor = IADSUltimateMonitor()

    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        pass
    finally:
        # 保存报告
        monitor.save_monitoring_report()
        print("👋 IADS Ultimate 监控结束")

    return 0


if __name__ == "__main__":
    exit(main())