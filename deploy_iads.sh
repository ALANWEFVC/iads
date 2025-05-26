#!/bin/bash

# IADS Production Deployment Script
# 综合部署和管理脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
IADS_APP="iads_main.py"
IADS_CONFIG="iads_config.py"
LOG_DIR="./logs"
RYU_PORT="6633"

# 打印彩色标题
print_title() {
    echo -e "${PURPLE}"
    echo "🚀 IADS Production Deployment System"
    echo "======================================"
    echo "   Integrated Adaptive Detection System v1.0"
    echo "   Enterprise SDN Network Intelligence Platform"
    echo -e "======================================${NC}"
    echo ""
}

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}🔍 Checking Dependencies...${NC}"
    
    # Python检查
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "   ✅ Python3: ${GREEN}${PYTHON_VERSION}${NC}"
    else
        echo -e "   ❌ ${RED}Python3 not found${NC}"
        return 1
    fi
    
    # Ryu检查
    if python3 -c "import ryu" 2>/dev/null; then
        RYU_VERSION=$(python3 -c "import ryu; print(ryu.__version__)" 2>/dev/null || echo "Unknown")
        echo -e "   ✅ Ryu Framework: ${GREEN}v${RYU_VERSION}${NC}"
    else
        echo -e "   ❌ ${RED}Ryu Framework not found${NC}"
        echo -e "      Install with: ${YELLOW}pip install ryu${NC}"
        return 1
    fi
    
    # SimpleSwitch13检查
    if python3 -c "from ryu.app import simple_switch_13" 2>/dev/null; then
        echo -e "   ✅ SimpleSwitch13: ${GREEN}Available${NC}"
    else
        echo -e "   ❌ ${RED}SimpleSwitch13 not available${NC}"
        return 1
    fi
    
    # Mininet检查 (可选)
    if command -v mn &> /dev/null; then
        MN_VERSION=$(mn --version 2>&1 | head -1)
        echo -e "   ✅ Mininet: ${GREEN}${MN_VERSION}${NC}"
    else
        echo -e "   ⚠️  ${YELLOW}Mininet not found (optional for testing)${NC}"
    fi
    
    echo ""
    return 0
}

# 环境准备
prepare_environment() {
    echo -e "${BLUE}🛠️  Preparing Environment...${NC}"
    
    # 创建日志目录
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        echo -e "   ✅ Created log directory: ${GREEN}$LOG_DIR${NC}"
    else
        echo -e "   ✅ Log directory exists: ${GREEN}$LOG_DIR${NC}"
    fi
    
    # 检查IADS应用文件
    if [ -f "$IADS_APP" ]; then
        echo -e "   ✅ IADS Application: ${GREEN}$IADS_APP${NC}"
        
        # 语法检查
        if python3 -m py_compile "$IADS_APP" 2>/dev/null; then
            echo -e "   ✅ Syntax Check: ${GREEN}Passed${NC}"
        else
            echo -e "   ❌ ${RED}Syntax Error in $IADS_APP${NC}"
            return 1
        fi
    else
        echo -e "   ❌ ${RED}IADS Application not found: $IADS_APP${NC}"
        return 1
    fi
    
    # 检查配置文件
    if [ -f "$IADS_CONFIG" ]; then
        echo -e "   ✅ Configuration: ${GREEN}$IADS_CONFIG${NC}"
    else
        echo -e "   ⚠️  ${YELLOW}Configuration file not found (using defaults)${NC}"
    fi
    
    echo ""
    return 0
}

# 显示系统信息
show_system_info() {
    echo -e "${BLUE}📊 System Information${NC}"
    echo -e "   OS: ${GREEN}$(uname -s) $(uname -r)${NC}"
    echo -e "   Python Path: ${GREEN}$(which python3)${NC}"
    echo -e "   Current User: ${GREEN}$(whoami)${NC}"
    echo -e "   Working Directory: ${GREEN}$(pwd)${NC}"
    echo -e "   Controller Port: ${GREEN}$RYU_PORT${NC}"
    echo ""
}

# 启动IADS
start_iads() {
    echo -e "${GREEN}🚀 Starting IADS System...${NC}"
    echo -e "   Application: ${CYAN}$IADS_APP${NC}"
    echo -e "   Port: ${CYAN}$RYU_PORT${NC}"
    echo ""
    
    # 显示启动命令
    echo -e "${YELLOW}Starting command:${NC}"
    echo -e "   ${CYAN}ryu-manager --verbose --observe-links $IADS_APP${NC}"
    echo ""
    
    # 启动建议
    echo -e "${BLUE}💡 Usage Tips:${NC}"
    echo -e "   • Press ${YELLOW}Ctrl+C${NC} to stop the controller"
    echo -e "   • Monitor logs in: ${GREEN}$LOG_DIR${NC}"
    echo -e "   • Test with Mininet in another terminal"
    echo ""
    
    # 测试命令提示
    echo -e "${BLUE}🧪 Test Command (run in another terminal):${NC}"
    echo -e "   ${CYAN}sudo mn --topo single,2 --controller remote,ip=127.0.0.1,port=$RYU_PORT --switch ovsk,protocols=OpenFlow13${NC}"
    echo ""
    
    echo -e "${GREEN}▶️  Starting IADS Controller...${NC}"
    echo ""
    
    # 启动Ryu控制器
    ryu-manager --verbose --observe-links --ofp-tcp-listen-port $RYU_PORT "$IADS_APP"
}

# 显示配置
show_config() {
    echo -e "${BLUE}⚙️  IADS Configuration${NC}"
    if [ -f "$IADS_CONFIG" ]; then
        python3 "$IADS_CONFIG"
    else
        echo -e "   ${YELLOW}Using default configuration${NC}"
    fi
    echo ""
}

# 测试模式
test_mode() {
    echo -e "${YELLOW}🧪 IADS Test Mode${NC}"
    echo -e "   This will start IADS in test mode with verbose logging"
    echo ""
    
    # 确认
    read -p "Continue with test mode? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Starting test mode...${NC}"
        ryu-manager --verbose --observe-links --ofp-tcp-listen-port $RYU_PORT "$IADS_APP" 2>&1 | tee "$LOG_DIR/iads_test_$(date +%Y%m%d_%H%M%S).log"
    else
        echo -e "${YELLOW}Test mode cancelled.${NC}"
    fi
}

# 状态检查
check_status() {
    echo -e "${BLUE}📊 IADS Status Check${NC}"
    
    # 检查端口
    if netstat -tuln 2>/dev/null | grep -q ":$RYU_PORT "; then
        echo -e "   ✅ Controller Port $RYU_PORT: ${GREEN}Active${NC}"
    else
        echo -e "   ❌ Controller Port $RYU_PORT: ${RED}Not Active${NC}"
    fi
    
    # 检查进程
    if pgrep -f "ryu-manager.*$IADS_APP" > /dev/null; then
        echo -e "   ✅ IADS Process: ${GREEN}Running${NC}"
        echo -e "      PID: ${CYAN}$(pgrep -f "ryu-manager.*$IADS_APP")${NC}"
    else
        echo -e "   ❌ IADS Process: ${RED}Not Running${NC}"
    fi
    
    # 检查日志
    if [ -d "$LOG_DIR" ] && [ "$(ls -A $LOG_DIR 2>/dev/null)" ]; then
        LOG_COUNT=$(ls -1 "$LOG_DIR"/*.log 2>/dev/null | wc -l)
        echo -e "   📁 Log Files: ${GREEN}$LOG_COUNT files in $LOG_DIR${NC}"
    else
        echo -e "   📁 Log Files: ${YELLOW}No logs found${NC}"
    fi
    
    echo ""
}

# 清理
cleanup() {
    echo -e "${YELLOW}🧹 Cleanup Options${NC}"
    echo "1) Clear logs"
    echo "2) Remove backup files"
    echo "3) Full cleanup"
    echo "4) Cancel"
    
    read -p "Select option (1-4): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            if [ -d "$LOG_DIR" ]; then
                rm -rf "$LOG_DIR"/*
                echo -e "   ✅ ${GREEN}Logs cleared${NC}"
            fi
            ;;
        2)
            rm -f *.backup *_backup_* iads_step*.py
            echo -e "   ✅ ${GREEN}Backup files removed${NC}"
            ;;
        3)
            rm -rf "$LOG_DIR"/*
            rm -f *.backup *_backup_* iads_step*.py
            echo -e "   ✅ ${GREEN}Full cleanup completed${NC}"
            ;;
        4)
            echo -e "   ${YELLOW}Cleanup cancelled${NC}"
            ;;
        *)
            echo -e "   ${RED}Invalid option${NC}"
            ;;
    esac
    echo ""
}

# 显示帮助
show_help() {
    echo -e "${CYAN}📖 IADS Help${NC}"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     Start IADS system (default)"
    echo "  test      Start in test mode with logging"
    echo "  config    Show configuration"
    echo "  status    Check system status"
    echo "  cleanup   Clean up logs and temporary files"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Start IADS system"
    echo "  $0 test          # Start in test mode"
    echo "  $0 status        # Check status"
    echo ""
}

# 主函数
main() {
    print_title
    
    case "${1:-start}" in
        "start")
            check_dependencies && prepare_environment && show_system_info && start_iads
            ;;
        "test")
            check_dependencies && prepare_environment && test_mode
            ;;
        "config")
            show_config
            ;;
        "status")
            check_status
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
