# Dr.COM VPN 网络共享系统

一个基于 Python 的 C/S 架构网络共享系统，用于突破校园网多设备限制。

## ⚠️ 免责声明

**此软件仅供学习用途使用。**

使用此软件则代表您愿意承担所造成的法律问题，开发者不为此承担任何法律义务。

请严格遵守相关法律法规和学校网络使用规定。因使用本软件造成的任何后果由使用者自行承担。

## 📋 项目背景

在某些校园网环境中，一个账户只能同时使用有限数量的设备（如1台PC + 1台手机）。本项目利用"被踢下线的设备仍可访问内网"的特性，通过 VPN 技术实现多设备网络共享。

## 🎯 核心原理

1. **服务端**：首先登录校园网，获得互联网访问权限
2. **客户端**：登录校园网（此时服务端被踢下线，但仍可访问内网）
3. **握手通信**：客户端通过内网连接到服务端
4. **服务端重登**：服务端重新登录校园网（客户端被踢下线）
5. **VPN建立**：客户端通过内网 VPN 连接到服务端，共享网络

## 🚀 功能特性

- ✅ 自动模拟网页登录 Dr.COM 系统
- ✅ 智能重试机制（最多5次，间隔30秒）
- ✅ 详细的日志记录功能
- ✅ 支持命令行和 GUI 两种客户端
- ✅ 多平台兼容（Windows/Linux/macOS/OpenWrt）
- ✅ 心跳保活机制
- ✅ 异常自动恢复

## 📦 项目结构

```
drcom/
├── common/                # 公共模块
│   ├── config.py         # 配置文件
│   ├── logger.py         # 日志模块
│   └── drcom_login.py    # Dr.COM登录模块
├── server/                # 服务端模块
│   └── vpn_server.py     # VPN服务端程序
├── client/                # 客户端模块（命令行版）
│   └── vpn_client.py     # VPN客户端程序
├── client_gui/            # 客户端模块（GUI版）
│   └── vpn_client_gui.py # VPN客户端GUI程序
├── docs/                  # 文档目录
│   ├── 快速开始.md
│   ├── 使用示例.md
│   ├── 开发说明.md
│   └── 验证逻辑分析.md
├── start_server.py        # 服务端启动脚本
├── start_client.py        # 客户端启动脚本（命令行版）
├── start_client_gui.py    # 客户端启动脚本（GUI版）
├── requirements.txt       # Python依赖
├── README.md              # 说明文档
└── logs/                  # 日志目录（自动创建）
```

## 🔧 安装步骤

### 1. 下载项目

```bash
cd drcom
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或使用虚拟环境（推荐）：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 📖 使用指南

### 服务端部署

选择一台稳定的设备作为服务器（建议使用开发板或不常移动的设备）：

**使用启动脚本（推荐）**：
```bash
python start_server.py <用户名> <密码> [端口]
```

**示例**：
```bash
python start_server.py MR646C80105795 mypassword 8888
```

**成功启动后会显示**：
```
============================================================
VPN服务器启动中...
============================================================
步骤1: 登录Dr.COM网络
✓ 登录成功！服务器内网IP: 172.21.77.34
步骤2: 启动VPN服务，监听端口 8888
✓ VPN服务已启动，监听 0.0.0.0:8888
============================================================
服务器信息:
  内网IP: 172.21.77.34
  监听端口: 8888
  请在客户端使用以下信息连接:
    服务器IP: 172.21.77.34
    端口: 8888
============================================================
```

**记下服务器的内网IP地址**（如 `172.21.77.34`），客户端需要用到。

### 客户端连接

#### 方式1: 命令行版本（适用于所有平台）

**使用启动脚本（推荐）**：
```bash
python start_client.py <用户名> <密码> <服务器IP> [服务器端口]
```

**或直接运行**：
```bash
python -m client.vpn_client <用户名> <密码> <服务器IP> [服务器端口]
```

**示例**：
```bash
python start_client.py MR646C80105795 mypassword 172.21.77.34 8888
```

#### 方式2: GUI版本（适用于桌面环境）

**使用启动脚本（推荐）**：
```bash
python start_client_gui.py
```

**或直接运行**：
```bash
python -m client_gui.vpn_client_gui
```

在GUI界面中填写：
- Dr.COM 用户名
- Dr.COM 密码
- 服务器内网IP（从服务端获取）
- 服务器端口（默认 8888）

然后点击"连接"按钮。

#### 方式3: OpenWrt 等嵌入式设备

1. 安装 Python 3 和 pip：
```bash
opkg update
opkg install python3 python3-pip
```

2. 安装依赖：
```bash
pip3 install requests
```

3. 上传必要文件到设备：
   - `config.py`
   - `logger.py`
   - `drcom_login.py`
   - `vpn_client.py`

4. 运行客户端：
```bash
python3 vpn_client.py <用户名> <密码> <服务器IP> <端口>
```

## ⚙️ 配置说明

编辑 `config.py` 文件可以自定义配置：

### Dr.COM 服务器配置
```python
DRCOM_CONFIG = {
    'base_url': 'http://10.252.252.5',  # 认证服务器地址
    'eportal_port': 801,                 # ePortal端口
    # ... 其他配置
}
```

### 重试配置
```python
RETRY_CONFIG = {
    'max_retries': 5,          # 最大重试次数
    'retry_delay': 30,         # 重试间隔（秒）
    'ping_timeout': 5,         # ping超时时间
    'test_url': 'www.bing.com' # 测试地址
}
```

### VPN 配置
```python
VPN_CONFIG = {
    'server_port': 8888,           # 服务端口
    'heartbeat_interval': 30,      # 心跳间隔
    'buffer_size': 8192            # 缓冲区大小
}
```

## 📝 日志文件

所有日志文件保存在 `logs/` 目录下：

- `vpn_server_YYYYMMDD.log` - 服务端日志
- `vpn_client_YYYYMMDD.log` - 客户端日志
- `drcom_login_YYYYMMDD.log` - 登录模块日志
- `vpn_client_gui_YYYYMMDD.log` - GUI客户端日志

日志文件会自动轮转，单个文件最大 10MB，保留最近 5 个文件。

## 🔍 故障排查

### 1. 登录失败

**现象**：`登录失败: 密码错误` 或 `登录失败: AC验证失败`

**解决方案**：
- 检查用户名和密码是否正确
- 确认账号未欠费或被停用
- 查看 `drcom_login_YYYYMMDD.log` 获取详细错误信息

### 2. 无法连接服务器

**现象**：`无法连接到服务器，已尝试10次`

**解决方案**：
- 确认服务器已启动且正常运行
- 检查服务器IP地址是否正确
- 确认客户端和服务端在同一内网
- 检查防火墙设置，确保端口未被阻止
- 尝试 ping 服务器IP：`ping 172.21.77.34`

### 3. 连接后无法上网

**现象**：VPN连接成功但无法访问互联网

**解决方案**：
- 检查服务端是否在线（查看服务端日志）
- 确认服务端重新登录是否成功
- 检查网络路由配置

### 4. 频繁断线

**现象**：连接不稳定，频繁断开重连

**解决方案**：
- 检查网络质量
- 增加心跳间隔：修改 `config.py` 中的 `heartbeat_interval`
- 查看日志文件中的错误信息

## 🛠️ 高级用法

### 1. 开机自启动（Linux）

创建 systemd 服务文件 `/etc/systemd/system/drcom-vpn-server.service`：

```ini
[Unit]
Description=Dr.COM VPN Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/drcom
ExecStart=/usr/bin/python3 /path/to/drcom/vpn_server.py username password 8888
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable drcom-vpn-server
sudo systemctl start drcom-vpn-server
```

### 2. 后台运行（Linux/macOS）

使用 `nohup` 命令：
```bash
nohup python3 vpn_server.py username password 8888 > /dev/null 2>&1 &
```

或使用 `screen`：
```bash
screen -S drcom-vpn
python3 vpn_server.py username password 8888
# 按 Ctrl+A 然后按 D 分离会话
```

### 3. Docker 部署（推荐）

创建 `Dockerfile`：
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "vpn_server.py"]
```

构建和运行：
```bash
docker build -t drcom-vpn-server .
docker run -d --name vpn-server --network host \
  drcom-vpn-server \
  python vpn_server.py username password 8888
```

## ⚠️ 注意事项

1. **账号安全**：请妥善保管账号密码，不要在公共场合明文输入
2. **合规使用**：请遵守学校网络使用规定，本工具仅供学习交流
3. **稳定性**：服务器建议使用稳定的设备（如树莓派、开发板等）
4. **网络质量**：内网质量会影响VPN性能，建议使用有线连接
5. **多设备限制**：本系统基于网络特性设计，不同网络环境可能有差异

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📮 联系方式

如有问题，请提交 Issue 或联系项目维护者。

---

**免责声明**：本项目仅供技术学习和研究使用，使用者应遵守相关法律法规和学校规章制度。因使用本项目造成的任何后果由使用者自行承担。

