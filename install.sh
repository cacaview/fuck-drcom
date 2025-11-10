#!/bin/bash
# Dr.COM 自动认证工具 - 安装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_warn "建议使用root权限运行此脚本"
        print_warn "某些功能可能需要root权限"
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_error "无法检测操作系统"
        exit 1
    fi
    print_info "检测到系统: $OS $VER"
}

# 检查Python
check_python() {
    print_info "检查Python环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_info "Python版本: $PYTHON_VERSION"
        
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 7 ]; then
            print_info "Python版本满足要求 (>=3.7)"
        else
            print_error "Python版本过低，需要 >= 3.7"
            exit 1
        fi
    else
        print_error "未找到Python 3"
        print_info "请先安装Python 3.7+"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    print_info "安装Python依赖包..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_info "依赖安装完成"
    else
        print_warn "未找到requirements.txt"
    fi
}

# 创建配置文件
create_config() {
    print_info "创建配置文件..."
    
    if [ ! -f "config.yaml" ]; then
        if [ -f "config.yaml.example" ]; then
            cp config.yaml.example config.yaml
            print_info "已创建config.yaml"
            print_warn "请编辑config.yaml填入你的账号信息"
        else
            print_warn "未找到config.yaml.example"
        fi
    else
        print_info "config.yaml已存在，跳过"
    fi
}

# 安装systemd服务
install_service() {
    if [ "$EUID" -ne 0 ]; then
        print_warn "需要root权限安装systemd服务，跳过"
        return
    fi
    
    print_info "安装systemd服务..."
    
    read -p "是否安装为systemd服务？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "跳过服务安装"
        return
    fi
    
    # 获取当前目录
    INSTALL_DIR=$(pwd)
    
    # 复制服务文件
    if [ -f "drcom-auth.service" ]; then
        # 修改服务文件中的路径
        sed "s|/opt/drcom|$INSTALL_DIR|g" drcom-auth.service > /tmp/drcom-auth.service
        
        # 复制到systemd目录
        cp /tmp/drcom-auth.service /etc/systemd/system/drcom-auth.service
        rm /tmp/drcom-auth.service
        
        # 重新加载systemd
        systemctl daemon-reload
        
        print_info "服务已安装"
        print_info "使用以下命令管理服务:"
        echo "  启动: sudo systemctl start drcom-auth"
        echo "  停止: sudo systemctl stop drcom-auth"
        echo "  开机自启: sudo systemctl enable drcom-auth"
        echo "  查看状态: sudo systemctl status drcom-auth"
        echo "  查看日志: sudo journalctl -u drcom-auth -f"
    else
        print_warn "未找到drcom-auth.service"
    fi
}

# 测试认证
test_auth() {
    print_info "测试认证功能..."
    
    read -p "是否测试认证？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "跳过测试"
        return
    fi
    
    read -p "请输入用户名: " USERNAME
    read -s -p "请输入密码: " PASSWORD
    echo
    
    print_info "开始测试..."
    python3 drcom_auth.py -u "$USERNAME" -p "$PASSWORD"
}

# 主函数
main() {
    echo "======================================================"
    echo "  Dr.COM 校园网自动认证工具 - 安装脚本"
    echo "======================================================"
    echo
    
    check_root
    detect_os
    check_python
    install_dependencies
    create_config
    install_service
    test_auth
    
    echo
    echo "======================================================"
    print_info "安装完成！"
    echo "======================================================"
    echo
    print_info "快速开始:"
    echo "  1. 编辑配置: vi config.yaml"
    echo "  2. 测试认证: python3 drcom_auth.py -u 用户名 -p 密码"
    echo "  3. 查看状态: python3 drcom_auth.py --status"
    echo "  4. 自动重连: python3 drcom_auth.py --auto-reconnect"
    echo
    print_info "文档地址: README.md"
    echo
}

# 运行主函数
main

