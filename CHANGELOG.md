# 更新日志

## [v1.3.1] - 2025-11-08

### 🔧 重大修复 - Dr.COM登录逻辑

#### 核心问题修复
- ✅ **登录路径修复**：将错误的 `/eportal/?c=ACSetting&a=Login` 修正为 `/eportal/portal/login`
- ✅ **用户名格式修正**：修复用户名格式为 `,0,{username}@{运营商代码}`
- ✅ **请求方法修正**：修改为使用GET方法，参数通过URL query string传递
- ✅ **JS版本更新**：更新jsVersion为实际使用的 `4.2.1`

#### 运营商支持
- ✅ **运营商选择**：新增运营商类型选择（中国电信/中国移动/中国联通/中国广电/职工账号）
- ✅ **运营商映射**：添加运营商代码映射配置
  - 中国电信 → telecom
  - 中国移动 → cmcc
  - 中国联通 → unicom
  - 中国广电 → cbn
  - 职工账号 → （无后缀）

#### 配置改进
- ✅ **交互式选择**：在配置输入时可选择运营商类型
- ✅ **默认设置**：默认使用中国电信
- ✅ **配置保存**：运营商类型会被加密保存

### 🔍 问题诊断方法
- 使用浏览器开发者工具分析实际登录请求
- 对比实际请求与代码中的实现
- 通过抓包确认正确的API格式

### 📝 文件变更
- `common/config.py` - 更新Dr.COM配置
- `common/drcom_login.py` - 修复登录逻辑
- `common/config_manager.py` - 添加运营商选择
- `server/vpn_server.py` - 添加ISP参数支持
- `start_server.py` - 传递运营商参数

## [v1.3.0] - 2025-11-07

### 🔧 重大修复

#### VPN代理功能真实实现
- ✅ **修复核心问题**：之前的代理功能为模拟实现，现已完全重写
- ✅ **SOCKS5协议**：实现完整的SOCKS5代理协议（RFC 1928）
- ✅ **真实流量转发**：双向数据转发，支持所有网络协议
- ✅ **本地代理服务**：客户端提供本地SOCKS5代理（127.0.0.1:1080）

#### 代码质量提升
- ✅ 移除所有TODO和模拟代码
- ✅ 实现完整的网络代理功能
- ✅ 添加详细的代码注释和文档
- ✅ 无Lint错误

### ✨ 新增功能

#### SOCKS5代理模块
- 新增 `common/socks5_proxy.py` - SOCKS5协议处理器
  - `Socks5ProxyHandler` - 单连接处理
  - `Socks5ProxyServer` - 独立代理服务器
- 支持IPv4、IPv6和域名地址类型
- 完整的握手、认证、连接处理
- 高效的select-based双向数据转发

#### VPN服务器改进
- 使用真实的SOCKS5代理处理器
- 完整的流量转发功能
- 详细的连接和转发日志
- 多客户端并发支持

#### VPN客户端改进
- 本地SOCKS5代理服务（监听127.0.0.1:1080）
- 自动接受并转发本地应用请求
- 多连接并发处理
- 使用说明和配置提示

#### 测试工具
- 新增 `test_socks5_proxy.py` - SOCKS5代理测试脚本
- 自动测试连接、握手、数据传输
- HTTP通信验证
- 详细的测试报告



### 🔄 变更内容

#### VPN服务器 (`server/vpn_server.py`)
```python
# 旧实现（已删除）
# TODO: 实现完整的代理逻辑
# 目前只是简单的回显
client_socket.send(b'OK')

# 新实现
handler = Socks5ProxyHandler(client_socket, client_id, self.logger)
handler.handle()
```

#### VPN客户端 (`client/vpn_client.py`)
- 添加本地代理服务器功能
- 支持配置本地代理端口
- 自动将流量转发到VPN服务器

#### 配置文件 (`common/config.py`)
```python
VPN_CONFIG = {
    'server_port': 8888,
    'local_proxy_port': 1080,      # 新增
    'heartbeat_interval': 30,
    'buffer_size': 8192,
    'connection_timeout': 10,       # 新增
    'socks5_enabled': True,         # 新增
}
```

### 📚 使用方法更新

#### 服务器端
```bash
python start_server.py
# 交互式输入配置，启动VPN服务器
```

#### 客户端
```bash
python start_client.py
# 交互式输入配置，启动客户端
# 本地SOCKS5代理将在 127.0.0.1:1080 上监听
```

#### 使用代理
```bash
# 方法1：curl测试
curl --socks5 127.0.0.1:1080 http://www.bing.com

# 方法2：配置浏览器
# Firefox: 设置 → 网络设置 → SOCKS5代理: 127.0.0.1:1080

# 方法3：测试脚本
python test_socks5_proxy.py
```

### 🔍 验证工具

#### 自动化测试
```bash
python test_socks5_proxy.py
```

测试内容：
- ✓ SOCKS5握手
- ✓ 连接建立
- ✓ HTTP通信
- ✓ 数据转发

### 🛡️ 技术改进

| 指标 | 旧版本 | 新版本 |
|------|--------|--------|
| 代理功能 | ❌ 模拟 | ✅ 真实 |
| 流量转发 | ❌ 无 | ✅ 完整 |
| SOCKS5支持 | ❌ 无 | ✅ 完整 |
| 协议兼容 | ❌ 无 | ✅ HTTP/HTTPS等所有 |
| 本地代理 | ❌ 无 | ✅ 127.0.0.1:1080 |
| 并发支持 | ⚠️ 有限 | ✅ 完整 |
| **功能完整度** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

### 📦 新增文件

- `common/socks5_proxy.py` - SOCKS5代理实现
- `test_socks5_proxy.py` - 代理测试工具
- `docs/修复说明.md` - 详细修复文档

### ⚠️ 破坏性变更

**无破坏性变更**

所有修改都是向下兼容的内部实现改进，API和使用方法保持不变。

### 🐛 修复的Bug

1. **严重**: VPN服务器代理功能为模拟实现
   - 影响：无法真正转发流量
   - 修复：实现完整SOCKS5代理

2. **中等**: 客户端缺少本地代理服务
   - 影响：用户无法方便地使用代理
   - 修复：添加本地SOCKS5代理服务

---

## [v1.2.0] - 2025-11-06

### 🔐 重大安全改进

#### 交互式配置输入
- ✅ 移除命令行参数传递敏感信息
- ✅ 改为交互式问答输入
- ✅ 密码输入时隐藏显示（使用getpass）
- ✅ 避免shell历史记录泄露

#### 配置文件加密
- ✅ 使用AES-256加密存储配置
- ✅ PBKDF2-HMAC-SHA256密钥派生
- ✅ 100,000次迭代增强安全性
- ✅ 每个配置文件独立的16字节随机盐值
- ✅ 主密码保护配置文件

#### 文件安全
- ✅ 配置文件自动设置为600权限（仅所有者可读写）
- ✅ `.drcom/` 目录加入.gitignore
- ✅ 防止配置文件被意外提交

### ✨ 新增功能

- 新增 `common/config_manager.py` - 加密配置管理模块
- 更新 `start_server.py` - 交互式服务端启动
- 更新 `start_client.py` - 交互式客户端启动
- 新增 `docs/配置加密说明.md` - 详细的加密说明文档
- 新增 `安全更新说明.md` - 安全更新完整说明

### 🔄 使用方式变更

#### 旧方式（已弃用）❌
```bash
python start_server.py username password 8888
```

#### 新方式（安全）✅
```bash
python start_server.py
# 然后按提示交互式输入
```

### 📦 依赖更新

- 新增：`cryptography>=41.0.0` - 用于配置文件加密

### ⚠️ 破坏性变更

- 命令行参数方式已完全移除
- 需要重新配置（首次运行时）
- 需要安装新的依赖（cryptography）

### 🛡️ 安全性提升

| 指标 | 旧版本 | 新版本 |
|------|--------|--------|
| 密码传递 | ❌ 命令行 | ✅ 交互式 |
| 密码显示 | ❌ 明文 | ✅ 隐藏 |
| 配置存储 | ❌ 明文 | ✅ AES-256加密 |
| Shell历史 | ❌ 泄露 | ✅ 不记录 |
| **安全级别** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## [v1.1.0] - 2025-11-06

### 🎯 重大变更

#### 项目结构重组
- 将代码按功能分类到不同文件夹
- `common/` - 公共模块（配置、日志、登录）
- `server/` - 服务端程序
- `client/` - 命令行客户端
- `client_gui/` - GUI客户端
- `docs/` - 文档集中管理

#### 免责声明添加
- ⚠️ 在所有模块的 `__init__.py` 中添加免责声明
- ⚠️ 在所有主要文件顶部添加免责声明
- ⚠️ 在启动脚本中显示免责声明
- ⚠️ 在 README.md 顶部添加醒目的免责声明

**免责声明内容**：
> 此软件仅供学习用途使用，使用此软件则代表您愿意承担所造成的法律问题，
> 开发者不为此承担任何法律义务。

### ✨ 新增功能

#### 启动脚本
- 新增 `start_server.py` - 服务端启动脚本
- 新增 `start_client.py` - 客户端启动脚本
- 新增 `start_client_gui.py` - GUI启动脚本
- 所有启动脚本在运行时显示免责声明

#### 文档更新
- 新增 `项目说明.md` - 项目使用说明
- 新增 `docs/项目结构变更说明.md` - 详细的变更说明
- 更新 `README.md` - 包含免责声明和新的使用方法
- 所有文档移动到 `docs/` 目录

### 🔄 变更内容

#### 文件位置变更
- `config.py` → `common/config.py`
- `logger.py` → `common/logger.py`
- `drcom_login.py` → `common/drcom_login.py`
- `vpn_server.py` → `server/vpn_server.py`
- `vpn_client.py` → `client/vpn_client.py`
- `vpn_client_gui.py` → `client_gui/vpn_client_gui.py`
- 所有文档 → `docs/` 目录

#### 导入路径更新
```python
# 旧导入
from config import VPN_CONFIG
from logger import Logger
from drcom_login import DrcomLogin

# 新导入
from common.config import VPN_CONFIG
from common.logger import Logger
from common.drcom_login import DrcomLogin
```

#### 使用方法更新
```bash
# 旧方法
python vpn_server.py user pass 8888
python vpn_client.py user pass 172.21.77.34 8888

# 新方法（推荐）
python start_server.py user pass 8888
python start_client.py user pass 172.21.77.34 8888
python start_client_gui.py

# 或使用模块方式
python -m server.vpn_server user pass 8888
python -m client.vpn_client user pass 172.21.77.34 8888
python -m client_gui.vpn_client_gui
```

### 📚 文档改进

- ✅ README.md 添加免责声明章节
- ✅ 更新项目结构说明
- ✅ 更新安装和使用指南
- ✅ 创建详细的变更说明文档
- ✅ 所有文档集中到 docs/ 目录

### 🛡️ 法律合规

- ✅ 所有代码文件添加免责声明
- ✅ 启动时强制显示免责声明
- ✅ 文档中多处强调仅供学习使用
- ✅ 明确声明开发者不承担法律责任

### 🔧 技术改进

- ✅ 模块化设计，代码结构更清晰
- ✅ 统一的包管理（`__init__.py`）
- ✅ 便捷的启动脚本
- ✅ 更好的代码组织

### ⚠️ 破坏性变更

- 旧的直接运行方式已弃用（需使用新的启动脚本）
- 导入路径已变更（需更新自定义脚本）
- 配置文件位置已变更（自动兼容）

### 📦 依赖变更

无依赖变更，`requirements.txt` 保持不变。

---

## [v1.0.0] - 2025-11-06

### ✨ 初始发布

#### 核心功能
- ✅ Dr.COM自动登录
- ✅ VPN服务端实现
- ✅ VPN客户端（命令行版）
- ✅ VPN客户端（GUI版）
- ✅ 智能重试机制
- ✅ 详细日志系统
- ✅ 心跳保活机制

#### 文档
- ✅ README.md
- ✅ 快速开始.md
- ✅ 使用示例.md
- ✅ 开发说明.md
- ✅ 验证逻辑分析.md
- ✅ 项目总结.md

#### 特性
- ✅ 多平台支持（Windows/Linux/macOS）
- ✅ OpenWrt兼容
- ✅ GUI多平台支持（Flet）
- ✅ 完善的异常处理
- ✅ 自动重连机制

---

## 版本说明

### 版本号格式
遵循语义化版本规范：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 变更类型

- **新增** - 新功能添加
- **变更** - 现有功能修改
- **弃用** - 即将移除的功能
- **移除** - 已删除的功能
- **修复** - Bug修复
- **安全** - 安全相关修复

---

**项目**: Dr.COM VPN 网络共享系统  
**许可**: MIT License  
**语言**: Python 3.7+

