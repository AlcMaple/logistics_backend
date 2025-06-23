import pytest
from utils.pwd import hash_password, verify_password, generate_salt


class TestPwdUtils:
    """密码工具测试类"""

    def test_generate_salt(self):
        """测试盐值生成"""
        salt1 = generate_salt()
        salt2 = generate_salt()

        assert isinstance(salt1, str), "盐值应该是字符串类型"
        assert len(salt1) == 32, "盐值长度应该是32位"
        assert salt1 != salt2, "两个盐值应该不相同"
        print(f"盐值生成测试通过")

    def test_hash_password_with_salt(self):
        """测试带盐值的密码加密"""
        password = "12345"
        salt = "test_salt_12345"

        hashed, returned_salt = hash_password(password, salt)

        assert isinstance(hashed, str), "加密密码应该是字符串"
        assert len(hashed) == 64, "SHA256哈希长度应该是64位"
        assert returned_salt == salt, "返回的盐值应该与传入的一致"
        print(f"带盐值密码加密测试通过")
        print(f"  原始密码: {password}")
        print(f"  盐值: {salt}")
        print(f"  加密后: {hashed}")

    def test_hash_password_auto_salt(self):
        """测试自动生成盐值的密码加密"""
        password = "12345"

        hashed1, salt1 = hash_password(password)
        hashed2, salt2 = hash_password(password)

        # 不同盐值应该产生不同的哈希
        assert salt1 != salt2, "自动生成的盐值应该不同"
        assert hashed1 != hashed2, "不同盐值应该产生不同哈希"
        print(f"自动盐值密码加密测试通过")

    def test_verify_password_correct(self):
        """测试正确密码验证"""
        password = "12345"
        hashed, salt = hash_password(password)

        # 验证正确密码
        is_valid = verify_password(password, hashed, salt)
        assert is_valid == True, "正确密码验证应该通过"
        print(f"正确密码验证测试通过")

    def test_verify_password_incorrect(self):
        """测试错误密码验证"""
        password = "12345"
        wrong_password = "123456"
        hashed, salt = hash_password(password)

        # 验证错误密码
        is_valid = verify_password(wrong_password, hashed, salt)
        assert is_valid == False, "错误密码验证应该失败"
        print(f"错误密码验证测试通过")

    def test_same_password_different_salt(self):
        """测试相同密码不同盐值产生不同哈希"""
        password = "12345"

        hashed1, salt1 = hash_password(password)
        hashed2, salt2 = hash_password(password)

        assert salt1 != salt2, "盐值应该不同"
        assert hashed1 != hashed2, "相同密码不同盐值应该产生不同哈希"

        # 但验证应该都能通过
        assert verify_password(password, hashed1, salt1) == True
        assert verify_password(password, hashed2, salt2) == True

        print(f"相同密码不同盐值测试通过")
