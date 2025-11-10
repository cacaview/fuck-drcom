# 更新日志

## [v2.0.0] - 2025-11-10

### 🔄 项目重大转型

#### 项目重新定位
- 🎯 **从**: VPN网络共享系统
- 🎯 **到**: Dr.COM校园网自动认证工具

#### 转型原因
经过全面的网络环境测试，发现：
- ❌ Dr.COM + 锐捷AC环境对未认证设备采取严格的流量控制
- ❌ VPN端口被完全拦截，无法建立连接
- ❌ 协议伪装无效，AC在网络层拦截
- ✅ **但认证模块完全可用且有价值**

#### 新的应用场景
保留并优化了自动认证功能，专注于：
- ✅ Linux服务器自动联网
- ✅ OpenWrt路由器自动认证
- ✅ 树莓派/NAS等嵌入式设备
- ✅ Docker容器网络认证
- ✅ 无图形界面设备的网络管理

### 新增功能

#### 1. 统一的命令行工具 `drcom_auth.py`
```bash
# 一键认证
python drcom_auth.py -u 学号 -p 密码

# 查询状态
python drcom_auth.py --status

# 主动下线
python drcom_auth.py --logout

# 自动重连
python drcom_auth.py -u 学号 -p 密码 --auto-reconnect
```

#### 2. 自动重连模式
- ✅ 定时检查在线状态
- ✅ 掉线自动重连
- ✅ 失败重试机制
- ✅ 适合后台运行

#### 3. 系统服务支持
- ✅ systemd服务配置示例
- ✅ OpenWrt定时任务集成
- ✅ 开机自启动支持

#### 4. 增强的命令行参数
- `--auto-reconnect`: 自动重连模式
- `--check-interval`: 检查间隔
- `--max-retries`: 最大重试次数
- `-v, --verbose`: 详细输出
- `-q, --quiet`: 静默模式

### 删除的功能

#### VPN相关代码（已删除）
- ❌ `server/vpn_server.py`
- ❌ `client/vpn_client.py`
- ❌ `start_server.py`
- ❌ `start_client.py`

#### 测试文件（已删除）
- ❌ 所有网络测试脚本
- ❌ 端口扫描工具
- ❌ AC策略分析脚本

#### 文档（已删除）
- ❌ VPN相关文档
- ❌ AC测试分析文档
- ❌ 项目不可行性评估

### 保留的核心模块

#### `common/drcom_login.py`
- ✅ Dr.COM认证核心逻辑
- ✅ 网络参数自动获取
- ✅ 在线状态查询
- ✅ 登录/下线功能

#### `common/wifi_params.py`
- ✅ WiFi参数获取
- ✅ 跨平台支持（Windows/Linux/macOS）

### 改进优化

1. **代码简化**
   - 移除了复杂的VPN网络栈
   - 专注于认证功能
   - 提高了可维护性

2. **文档重写**
   - 全新的README
   - 清晰的使用场景
   - 详细的部署指南

3. **用户体验**
   - 统一的命令行界面
   - 更友好的输出信息
   - 完善的错误处理

### 使用场景示例

#### Linux服务器
```bash
# 开机自动认证
sudo systemctl enable drcom-auth
sudo systemctl start drcom-auth
```

#### OpenWrt路由器
```bash
# 定时检查（crontab）
*/5 * * * * /usr/bin/python3 /root/drcom/drcom_auth.py --auto-reconnect
```

#### Docker容器
```dockerfile
CMD ["python3", "/app/drcom_auth.py", "--auto-reconnect"]
```

### 未来计划

1. **功能增强**
   - [ ] Web管理界面
   - [ ] 流量统计
   - [ ] 多账号管理
   - [ ] 通知推送（邮件/微信）

2. **平台支持**
   - [ ] 打包为二进制文件
   - [ ] Docker镜像
   - [ ] OpenWrt ipk包

3. **稳定性**
   - [ ] 更多错误处理
   - [ ] 网络异常恢复
   - [ ] 日志轮转

---

## [v1.6.1] - 2025-11-10 (已废弃)

### 🚨 项目终止 - 经全面测试验证不可行

此版本已废弃，项目已转型为自动认证工具。

详见v2.0.0更新日志。

---

## [v1.6.0] - 2025-11-10 (已废弃)

### 🔴 重大发现 - 设备被踢下线后无法访问内网

此版本已废弃，项目已转型。

---

## [v1.5.0] - 2025-11-09 (已废弃)

### 初始VPN版本

此版本已废弃。核心认证功能已迁移到v2.0.0。

---

**版本说明**:
- v2.0.0+ : 自动认证工具（当前版本）
- v1.x : VPN共享系统（已废弃）

**迁移指南**:
如果您之前使用v1.x版本，请查看README.md了解新的使用方式。
