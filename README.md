# Dr.COM 校园网自动认证工具

一个基于 Python 的 Dr.COM 校园网自动认证工具，专为无图形界面的设备（如服务器、路由器、树莓派等）设计。

## 📋 项目简介

在使用Dr.COM校园网时，传统的Web认证方式需要通过浏览器访问认证页面，这对于无图形界面的设备（Linux服务器、OpenWrt路由器、嵌入式设备等）来说非常不便。

本工具提供了**命令行自动认证**功能，支持：
- ✅ 自动获取网络参数（AC地址、SSID、MAC地址等）
- ✅ 自动发送认证请求
- ✅ 查询在线状态
- ✅ 主动下线
- ✅ 支持有线和无线网络
- ✅ 适用于无图形界面的设备

## 🎯 适用场景

### 1. Linux服务器自动联网
```bash
# 服务器启动时自动认证
python drcom_auth.py --username your_username --password your_password
```

### 2. OpenWrt路由器
```bash
# 在路由器上定时检查并自动重连
*/5 * * * * python /root/drcom_auth.py --auto-reconnect
```

### 3. 树莓派/NAS设备
- 开机自动认证
- 掉线自动重连
- 无需手动操作

### 4. Docker容器
- 容器内网络自动认证
- 支持多容器场景

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 操作系统：Linux / Windows / macOS
- 网络：连接到Dr.COM校园网（有线或无线）

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/drcom.git
cd drcom

# 安装依赖（可选创建虚拟环境）
pip install -r requirements.txt
```

### 基本使用

#### 1. 一键认证

```bash
python drcom_auth.py --username 学号 --password 密码
```

#### 2. 交互式认证

```bash
python drcom_auth.py
# 然后按提示输入账号密码
```

#### 3. 查询在线状态

```bash
python drcom_auth.py --status
```

#### 4. 主动下线

```bash
python drcom_auth.py --logout
```

#### 5. 自动重连模式

```bash
# 持续监控，掉线自动重连
python drcom_auth.py --username 学号 --password 密码 --auto-reconnect
```

## 📖 详细功能

### 自动获取网络参数

工具会自动检测并获取：
- 本地IP地址
- MAC地址
- 网关地址
- AC控制器地址
- SSID（无线网络）
- 用户VLAN ID

### 认证流程

```
1. 检测网络环境
   ↓
2. 获取WiFi参数（如果是无线）
   ↓
3. 访问认证页面获取配置
   ↓
4. 构造认证请求
   ↓
5. 发送认证
   ↓
6. 验证认证结果
```

### 状态监控

```bash
# 查看详细状态
python drcom_auth.py --status --verbose

输出示例：
==================================================
Dr.COM 在线状态查询
==================================================
设备IP: 172.21.77.34
MAC地址: 00:90:0b:ab:13:56

正在查询在线状态...

==================================================
在线状态：已认证
==================================================
认证时间: 2025-11-10 10:30:15
在线时长: 2小时35分钟
已用流量: 1.2GB
剩余流量: 无限制
==================================================
```

## 🔧 高级配置

### 配置文件

创建 `config.yaml`：

```yaml
# 账号配置
account:
  username: "your_username"
  password: "your_password"

# 网络配置（可选，留空自动检测）
network:
  interface: "eth0"  # 指定网卡接口
  ac_ip: ""          # AC IP地址，留空自动检测
  
# 重连配置
reconnect:
  enabled: true
  check_interval: 60  # 检查间隔（秒）
  max_retries: 3      # 最大重试次数

# 日志配置
logging:
  level: "INFO"       # DEBUG, INFO, WARNING, ERROR
  file: "drcom.log"   # 日志文件路径
```

使用配置文件：

```bash
python drcom_auth.py --config config.yaml
```

### 系统服务（Linux）

创建 systemd 服务 `/etc/systemd/system/drcom-auth.service`：

```ini
[Unit]
Description=Dr.COM Auto Authentication Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/drcom
ExecStart=/usr/bin/python3 /opt/drcom/drcom_auth.py --config /opt/drcom/config.yaml --auto-reconnect
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable drcom-auth
sudo systemctl start drcom-auth

# 查看状态
sudo systemctl status drcom-auth
```

### OpenWrt集成

1. 安装Python环境：

```bash
opkg update
opkg install python3 python3-pip
pip3 install requests beautifulsoup4
```

2. 复制脚本到路由器：

```bash
scp -r drcom root@192.168.1.1:/root/
```

3. 添加定时任务（crontab）：

```bash
# 编辑定时任务
crontab -e

# 添加以下行（每5分钟检查一次）
*/5 * * * * /usr/bin/python3 /root/drcom/drcom_auth.py --config /root/drcom/config.yaml --auto-reconnect >> /tmp/drcom.log 2>&1
```

## 📊 命令行参数

```
使用方法: drcom_auth.py [选项]

认证选项:
  -u, --username TEXT       用户名（学号）
  -p, --password TEXT       密码
  -c, --config PATH         配置文件路径
  
操作选项:
  --login                   执行登录认证（默认）
  --logout                  主动下线
  --status                  查询在线状态
  
网络选项:
  -i, --interface TEXT      指定网络接口（如eth0, wlan0）
  --ac-ip TEXT             指定AC IP地址
  
行为选项:
  --auto-reconnect         自动重连模式
  --daemon                 后台运行
  --check-interval INT     检查间隔（秒），默认60
  
输出选项:
  -v, --verbose            详细输出
  -q, --quiet              静默模式
  --log-file PATH          日志文件路径
  
其他:
  -h, --help               显示帮助信息
  --version                显示版本信息
```

## 🔍 故障排查

### 常见问题

#### 1. 认证失败

**问题**: "认证失败，请检查用户名和密码"

**解决**:
- 检查用户名和密码是否正确
- 确认账号是否欠费
- 检查是否已达设备上限

#### 2. 网络参数获取失败

**问题**: "无法获取网络参数"

**解决**:
```bash
# 手动指定网络接口
python drcom_auth.py --interface eth0

# 或查看可用接口
ip addr show  # Linux
ipconfig      # Windows
```

#### 3. AC地址检测失败

**问题**: "无法检测AC地址"

**解决**:
```bash
# 手动指定AC IP
python drcom_auth.py --ac-ip 10.252.252.5
```

#### 4. 权限问题（Linux）

**问题**: "Permission denied"

**解决**:
```bash
# 使用sudo运行
sudo python drcom_auth.py

# 或修改文件权限
chmod +x drcom_auth.py
```

### 调试模式

启用详细日志：

```bash
python drcom_auth.py --verbose --log-file debug.log
```

查看完整请求信息：

```bash
python drcom_auth.py --debug
```

## 📁 项目结构

```
drcom/
├── drcom_auth.py           # 主程序
├── common/
│   ├── drcom_login.py      # Dr.COM认证模块
│   ├── wifi_params.py      # WiFi参数获取
│   └── network_utils.py    # 网络工具函数
├── config.yaml.example     # 配置文件示例
├── requirements.txt        # 依赖列表
├── README.md              # 本文件
├── CHANGELOG.md           # 更新日志
└── 免责声明.md            # 免责声明

docs/                      # 文档目录
├── API文档.md
└── 常见问题.md
```

## ⚙️ 核心模块说明

### 1. `common/drcom_login.py`

Dr.COM认证核心模块，包含：
- `get_wifi_params()` - 获取WiFi参数
- `get_local_ip()` - 获取本地IP
- `get_page_config()` - 获取页面配置
- `login()` - 执行登录
- `check_online_status()` - 检查在线状态
- `logout()` - 下线

### 2. `common/wifi_params.py`

WiFi参数获取模块，支持：
- Windows (netsh)
- Linux (iwconfig, nmcli)
- macOS (airport)

### 3. `common/network_utils.py`

网络工具函数：
- IP地址检测
- MAC地址获取
- 网关检测
- AC地址探测

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/yourusername/drcom.git
cd drcom

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/
```

### 代码规范

- 遵循 PEP 8 代码风格
- 添加必要的注释和文档字符串
- 提交前运行 `black` 和 `flake8`

## ⚠️ 免责声明

**本工具仅供学习和技术研究使用。**

- 📄 请查看完整的 [免责声明.md](./免责声明.md)
- ⚖️ 使用本工具产生的一切后果由使用者自行承担
- 📚 请遵守学校网络使用规定和相关法律法规
- 🔐 妥善保管账号密码，不要在公共场合明文输入
- ⚠️ 如学校明确禁止使用自动认证工具，请立即停止使用

## 📝 许可证

MIT License

## 🔗 相关链接

- [项目主页](https://github.com/yourusername/drcom)
- [问题反馈](https://github.com/yourusername/drcom/issues)
- [更新日志](CHANGELOG.md)
- [API文档](docs/API文档.md)

## 📮 联系方式

- 邮箱: your.email@example.com
- Issue: https://github.com/yourusername/drcom/issues

## 🙏 致谢

感谢所有贡献者和使用者的支持！

---

**版本**: v2.0.0  
**发布日期**: 2025-11-10  
**项目类型**: 校园网自动认证工具
