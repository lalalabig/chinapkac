#!/usr/bin/env python3
"""
修复用户密码问题
将所有用户的密码重置为 123456 并正确加密
"""
import sqlite3
import hashlib
import os
import base64

def make_password(password, salt=None, iterations=600000):
    """
    生成Django兼容的pbkdf2_sha256密码哈希
    模拟Django的make_password函数
    """
    if salt is None:
        # 生成22字符的随机salt (16字节base64编码)
        salt = base64.b64encode(os.urandom(16))[:22].decode('utf-8')
    
    # 使用PBKDF2算法
    hash_value = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations,
        dklen=32
    )
    
    # 编码为base64
    hash_b64 = base64.b64encode(hash_value).decode('utf-8').strip()
    
    # 返回Django格式的密码
    return f'pbkdf2_sha256${iterations}${salt}${hash_b64}'

def fix_passwords():
    """修复所有用户的密码"""
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        print("="*80)
        print("修复用户密码")
        print("="*80)
        
        # 查询所有用户
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("数据库中没有用户！")
            return
        
        print(f"\n找到 {len(users)} 个用户，正在重置密码为 '123456'...\n")
        
        # 为所有用户设置密码
        new_password = '123456'
        
        for user_id, username in users:
            # 生成加密后的密码
            encrypted_password = make_password(new_password)
            
            # 更新数据库
            cursor.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (encrypted_password, user_id)
            )
            
            print(f"✓ {username} - 密码已重置")
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print("\n" + "="*80)
        print("密码修复完成！")
        print("所有用户现在可以使用密码 '123456' 登录")
        print("="*80)
        
        # 验证修复
        print("\n验证修复结果...")
        verify_fix()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

def verify_fix():
    """验证密码修复"""
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, password FROM users")
        users = cursor.fetchall()
        
        print(f"\n验证 {len(users)} 个用户的密码格式:")
        
        all_ok = True
        for username, password in users:
            if password.startswith('pbkdf2_sha256$'):
                print(f"  ✓ {username} - 密码格式正确")
            else:
                print(f"  ✗ {username} - 密码格式错误: {password[:30]}...")
                all_ok = False
        
        if all_ok:
            print("\n✓ 所有用户密码格式正确！")
        else:
            print("\n✗ 部分用户密码格式仍有问题")
        
        conn.close()
        
    except Exception as e:
        print(f"验证错误: {e}")

if __name__ == '__main__':
    fix_passwords()
