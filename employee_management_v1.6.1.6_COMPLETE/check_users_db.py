#!/usr/bin/env python3
"""
直接查询数据库检查用户信息
"""
import sqlite3
import sys

def check_users():
    """检查数据库中的用户"""
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        print("="*80)
        print("用户信息检查")
        print("="*80)
        
        # 查询所有用户
        cursor.execute("""
            SELECT id, username, email, role, is_active, is_staff, is_superuser, 
                   password
            FROM users
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("数据库中没有用户！")
            return
        
        print(f"\n找到 {len(users)} 个用户:\n")
        
        for user in users:
            user_id, username, email, role, is_active, is_staff, is_superuser, password = user
            print(f"用户: {username}")
            print(f"  ID: {user_id}")
            print(f"  Email: {email}")
            print(f"  角色: {role}")
            print(f"  is_active: {is_active}")
            print(f"  is_staff: {is_staff}")
            print(f"  is_superuser: {is_superuser}")
            print(f"  密码哈希: {password[:60]}...")
            print(f"  密码算法: {password.split('$')[0] if '$' in password else '未知'}")
            print()
        
        conn.close()
        
        print("="*80)
        print("检查完成")
        print("="*80)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_users()
