#!/usr/bin/env python3
"""
快速测试登录修复
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.drcom_login import DrcomLogin

# 测试配置（请根据实际情况修改）
TEST_CONFIG = {
    'username': '23410338',  # 你的用户名
    'password': 'Bw093019',   # 你的密码
    'isp': '中国电信',
    'connection_type': 'auto'
}

def test_login():
    """测试登录功能"""
    print("=" * 60)
    print("🧪 测试 Dr.COM 登录修复")
    print("=" * 60)
    print()
    
    print("配置信息:")
    print(f"  用户名: {TEST_CONFIG['username']}")
    print(f"  运营商: {TEST_CONFIG['isp']}")
    print(f"  连接方式: {TEST_CONFIG['connection_type']}")
    print()
    
    # 创建登录实例
    login = DrcomLogin(
        username=TEST_CONFIG['username'],
        password=TEST_CONFIG['password'],
        isp=TEST_CONFIG['isp'],
        connection_type=TEST_CONFIG['connection_type']
    )
    
    # 执行登录
    print("开始登录测试...")
    print("-" * 60)
    result = login.login()
    print("-" * 60)
    print()
    
    # 显示结果
    if result['success']:
        print("✅ 登录测试成功！")
        print(f"   内网IP: {result['ip']}")
        print(f"   消息: {result['message']}")
    else:
        print("❌ 登录测试失败")
        print(f"   原因: {result['message']}")
        print()
        print("💡 调试建议:")
        print("   1. 检查用户名和密码是否正确")
        print("   2. 查看上面的日志输出，特别注意:")
        print("      - 在线状态检查方式 (内核接口 或 Radius接口)")
        print("      - MAC地址格式 (应该是大写)")
        print("      - IP地址转换 (Radius方式会显示十进制)")
        print("   3. 如果看到 '页面配置响应' 或 '状态查询响应'，")
        print("      请将完整的响应内容提供给开发者")
    
    return result['success']

if __name__ == '__main__':
    try:
        success = test_login()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f)
        print(f"测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

