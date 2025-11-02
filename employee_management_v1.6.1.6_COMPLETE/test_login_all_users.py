#!/usr/bin/env python3
"""
测试用户登录功能
验证所有用户都可以使用密码 123456 登录
"""
import sqlite3
import hashlib
import base64

def verify_password(stored_password, test_password):
    """
    验证密码是否正确
    """
    if not stored_password.startswith('pbkdf2_sha256$'):
        return False
    
    try:
        # 解析存储的密码
        parts = stored_password.split('$')
        if len(parts) != 4:
            return False
        
        algorithm = parts[0]
        iterations = int(parts[1])
        salt = parts[2]
        stored_hash = parts[3]
        
        # 使用相同参数计算测试密码的哈希
        test_hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            test_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations,
            dklen=32
        )
        test_hash = base64.b64encode(test_hash_bytes).decode('utf-8').strip()
        
        # 比较哈希值
        return test_hash == stored_hash
        
    except Exception as e:
        print(f"验证错误: {e}")
        return False

def test_login():
    """测试所有用户登录"""
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        print("="*80)
        print("测试用户登录功能")
        print("="*80)
        
        # 查询所有用户
        cursor.execute("""
            SELECT username, password, role, is_active 
            FROM users
        """)
        users = cursor.fetchall()
        
        if not users:
            print("数据库中没有用户！")
            return
        
        print(f"\n测试 {len(users)} 个用户使用密码 '123456' 登录:\n")
        
        test_password = '123456'
        success_count = 0
        fail_count = 0
        
        for username, password, role, is_active in users:
            # 检查is_active
            if not is_active:
                print(f"✗ {username} - 账户未激活")
                fail_count += 1
                continue
            
            # 验证密码
            if verify_password(password, test_password):
                print(f"✓ {username} ({role}) - 登录成功")
                success_count += 1
            else:
                print(f"✗ {username} ({role}) - 密码验证失败")
                fail_count += 1
        
        conn.close()
        
        print("\n" + "="*80)
        print(f"测试结果: 成功 {success_count}/{len(users)}, 失败 {fail_count}/{len(users)}")
        print("="*80)
        
        if fail_count == 0:
            print("\n✓✓✓ 所有用户都可以正常登录！")
            return True
        else:
            print(f"\n✗✗✗ 有 {fail_count} 个用户无法登录")
            return False
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_login()
    exit(0 if success else 1)
