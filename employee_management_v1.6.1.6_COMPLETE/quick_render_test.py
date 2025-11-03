#!/usr/bin/env python3
"""
快速Render数据库连接测试
基于您的截图配置更新
"""

import psycopg2
import time

print("🚀 快速Render数据库连接测试")
print("=" * 50)

# 从截图确认的配置
DATABASE_CONFIG = {
    'HOST': 'dpg-d447hde3jp1c739bdo90-a.singapore-1.renderd.com',
    'NAME': 'chinpkac_database_tps4',
    'USER': 'chinpkac_database_tps4_user',
    'PASSWORD': 'rDAEqQUTcL28yd1m0jVe4TstpAyfVaVG',
    'PORT': '5432'
}

print("📊 数据库配置:")
for key, value in DATABASE_CONFIG.items():
    if key == 'PASSWORD':
        print(f"  {key}: {value[:8]}...")  # 隐藏密码
    else:
        print(f"  {key}: {value}")

print(f"\n🔍 正在测试连接...")
print("💡 如果连接失败，请检查Render数据库的IP白名单设置")

try:
    start_time = time.time()
    
    conn = psycopg2.connect(
        dbname=DATABASE_CONFIG['NAME'],
        user=DATABASE_CONFIG['USER'],
        password=DATABASE_CONFIG['PASSWORD'],
        host=DATABASE_CONFIG['HOST'],
        port=DATABASE_CONFIG['PORT'],
        connect_timeout=10
    )
    
    elapsed = time.time() - start_time
    print(f"✅ 连接成功! (耗时: {elapsed:.1f}秒)")
    
    # 快速测试
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchone()
    
    print("✅ 数据库响应正常")
    
    # 检查表
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print(f"\n📋 数据库表数量: {len(tables)}")
    
    # 检查Django表
    django_tables = [t[0] for t in tables if t[0] in ['accounts_user', 'django_migrations']]
    print(f"👤 Django表: {django_tables}")
    
    if 'accounts_user' in [t[0] for t in tables]:
        cursor.execute("SELECT COUNT(*) FROM accounts_user;")
        count = cursor.fetchone()[0]
        print(f"👥 用户数量: {count}")
    
    conn.close()
    
    print("\n🎉 连接测试成功！可以开始创建用户了！")
    print("运行: python final_render_solution.py")
    
except psycopg2.OperationalError as e:
    print(f"❌ 连接失败: {e}")
    print("\n🔧 请检查:")
    print("1. Render数据库的IP白名单设置")
    print("2. 数据库服务是否正常运行")
    print("3. 网络连接是否正常")
    
except Exception as e:
    print(f"❌ 其他错误: {e}")

print("\n" + "=" * 50)