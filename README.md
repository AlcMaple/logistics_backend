# logistics_backend

## 环境搭建

### 1. 安装Python

```
conda create -n pylog python=3.9.19
conda activate pylog
```

### 2. 安装依赖包

```
pip install -r requirements.txt
```

### 3. 创建数据库

```sql
create database logistics_db;

-- 使用数据库
USE logistics_db;

-- 创建企业表
CREATE TABLE IF NOT EXISTS companies (
    company_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '企业ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    company_name VARCHAR(100) NOT NULL COMMENT '企业名称',
    invite_code VARCHAR(8) NOT NULL UNIQUE COMMENT '企业邀请码（8位大写字母）',
    operator_type ENUM('CLIENT', 'PLATFORM') NOT NULL DEFAULT 'CLIENT' COMMENT '操作员类型',
    wallet DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '企业钱包余额',
    administrator_name VARCHAR(50) NOT NULL COMMENT '管理员姓名',
    administrator_phone VARCHAR(20) NOT NULL COMMENT '管理员手机号',
    administrator_password VARCHAR(255) NOT NULL COMMENT '管理员密码（哈希加密）',
    INDEX idx_invite_code (invite_code),
    INDEX idx_operator_type (operator_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='企业表';

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '用户ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    nick_name VARCHAR(50) NOT NULL COMMENT '用户名称',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号',
    company_id VARCHAR(36) NOT NULL COMMENT '所属企业ID',
    job_number VARCHAR(20) NOT NULL UNIQUE COMMENT '工号',
    position ENUM('1', '2', '3', '4', '5') NOT NULL COMMENT '岗位：1.客服 2.物流专员 3.财务 4.人事 5.管理员',
    permissions JSON COMMENT '权限列表（JSON格式）',
    registered BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已注册（激活状态）',
    operator_type ENUM('CLIENT', 'PLATFORM') NOT NULL DEFAULT 'CLIENT' COMMENT '操作员类型',
    password VARCHAR(255) NULL COMMENT '密码（哈希加密）',
    salt VARCHAR(32) NULL COMMENT '盐值',
    INDEX idx_phone (phone),
    INDEX idx_job_number (job_number),
    INDEX idx_company_id (company_id),
    INDEX idx_position (position),
    INDEX idx_registered (registered),
    INDEX idx_operator_type (operator_type),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 查看创建的表
SHOW TABLES;

-- 查看表结构
DESCRIBE companies;
DESCRIBE users;

ALTER TABLE users ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;

INSERT INTO companies (
    company_id,
    company_name,
    invite_code,
    operator_type,
    wallet,
    administrator_name,
    administrator_phone,
    administrator_password,
    created_at,
    updated_at
) VALUES (
    '998a5805-ff3d-477d-a598-8348db542ccf',
    '测试企业',
    'ABCDEFGH',
    'CLIENT',
    1000.00,
    '管理员张三',
    '18800001234',
    '123456',
    NOW(),
    NOW()
);
```

### 4. 启动服务

```bash
python main.py
```