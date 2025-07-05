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

USE logistics_db;

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
    '数字化智能',
    'RYJJJBQM',
    'CLIENT',
    1000.00,
    '张三',
    '18800001234',
    '734567',
    NOW(),
    NOW()
);

CREATE TABLE IF NOT EXISTS fees (
    fee_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '费用ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    path_id VARCHAR(50) NOT NULL COMMENT '运单号',
    order_id VARCHAR(50) NOT NULL COMMENT '订单号',
    status ENUM('APPEALING', 'PENDING_PAYMENT', 'DELIVERING') NOT NULL DEFAULT 'APPEALING' COMMENT '订单状态',
    total_price INT NOT NULL DEFAULT 0 COMMENT '基本路费（分）',
    driver_fee INT NOT NULL DEFAULT 0 COMMENT '司机费用（分）',
    highway_fee INT NOT NULL DEFAULT 0 COMMENT '高速费（分）',
    parking_fee INT NOT NULL DEFAULT 0 COMMENT '停车费（分）',
    carry_fee INT NOT NULL DEFAULT 0 COMMENT '搬运费（分）',
    wait_fee INT NOT NULL DEFAULT 0 COMMENT '等候费（分）',
    order_time DATETIME NOT NULL COMMENT '下单时间',
    receipt_imgs TEXT COMMENT '回单照片路径',
    parking_bill_imgs TEXT COMMENT '停车费发票照片路径',
    highway_bill_imgs TEXT COMMENT '高速费发票照片路径',
    receipt_reject_reason VARCHAR(255) COMMENT '回单驳回原因',
    bill_reject_reason VARCHAR(255) COMMENT '账单驳回原因',
    except_highway_fee INT DEFAULT 0 COMMENT '期望高速费（分）',
    except_parking_fee INT DEFAULT 0 COMMENT '期望停车费（分）',
    except_carry_fee INT DEFAULT 0 COMMENT '期望搬运费（分）',
    except_wait_fee INT DEFAULT 0 COMMENT '期望等候费（分）',
    logistics_platform VARCHAR(100) COMMENT '派单渠道（物流平台）',
    settlement_enable BOOLEAN DEFAULT FALSE COMMENT '是否发起结算操作',
    company_id VARCHAR(36) NOT NULL COMMENT '客户公司ID',
    INDEX idx_order_id (order_id),
    INDEX idx_path_id (path_id),
    INDEX idx_status (status),
    INDEX idx_company_id (company_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='费用表';

CREATE TABLE IF NOT EXISTS company_accounts (
    company_account_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '客户账户ID',
    company_id VARCHAR(36) NOT NULL COMMENT '客户公司ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    company_account_updatetime DATETIME NOT NULL COMMENT '账户更新时间',
    company_account_balance INT NOT NULL DEFAULT 0 COMMENT '账户余额（分）',
    company_account_balance_warning_val INT NOT NULL DEFAULT 0 COMMENT '余额预警值（分）',
    company_account_balance_warning_phone VARCHAR(20) COMMENT '预警手机号',
    company_account_balance_warning_enable BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否启用余额预警',
    recharge_status ENUM('审核中', '已通过') DEFAULT '审核中' COMMENT '充值状态',
    recharge_time DATETIME COMMENT '充值时间',
    recharge_name VARCHAR(50) COMMENT '充值人姓名',
    recharge_phone VARCHAR(20) COMMENT '充值人手机号',
    recharge_amount INT DEFAULT 0 COMMENT '充值金额（分）',
    received_amount INT DEFAULT 0 COMMENT '到账金额（分）',
    INDEX idx_company_id (company_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户账户表';

CREATE TABLE IF NOT EXISTS driver_accounts (
    driver_account_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '司机账户ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    driver_phone VARCHAR(20) NOT NULL COMMENT '司机手机号',
    driver_account_balance INT NOT NULL DEFAULT 0 COMMENT '司机账户余额（分）',
    INDEX idx_driver_phone (driver_phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='司机账户表';

ALTER TABLE fees
MODIFY COLUMN company_id VARCHAR(36) NULL COMMENT '客户公司ID';

INSERT INTO fees (
    fee_id,
    path_id,
    order_id,
    status,
    total_price,
    driver_fee,
    highway_fee,
    parking_fee,
    carry_fee,
    wait_fee,
    order_time,
    receipt_imgs,
    parking_bill_imgs,
    highway_bill_imgs,
    receipt_reject_reason,
    bill_reject_reason,
    except_highway_fee,
    except_parking_fee,
    except_carry_fee,
    except_wait_fee,
    logistics_platform,
    settlement_enable,
    company_id,
    created_at,
    updated_at
) VALUES
('fee001', 'path001', 'order001', 'PENDING_PAYMENT', 10000, 3000, 2000, 1000, 1500, 2500, NOW(),
 '/imgs/receipt1.jpg', '/imgs/parking1.jpg', '/imgs/highway1.jpg', NULL, NULL,
 2000, 1000, 1500, 2500, '平台A', FALSE, '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),

('fee002', 'path002', 'order002', 'DELIVERING', 15000, 4000, 3000, 2000, 2000, 4000, NOW(),
 '/imgs/receipt2.jpg', '/imgs/parking2.jpg', '/imgs/highway2.jpg', NULL, NULL,
 3000, 2000, 2000, 4000, '平台B', TRUE, NULL, NOW(), NOW()),

('fee003', 'path003', 'order003', 'APPEALING', 8000, 2000, 1000, 500, 1000, 1500, NOW(),
 NULL, NULL, NULL, '照片模糊', '票据缺失',
 1000, 500, 1000, 1500, '平台C', FALSE, NULL, NOW(), NOW()),

('fee004', 'path004', 'order004', 'DELIVERING', 12000, 3500, 2500, 1500, 1000, 3500, NOW(),
 '/imgs/receipt4.jpg', NULL, '/imgs/highway4.jpg', NULL, NULL,
 2500, 1500, 1000, 3500, '平台D', TRUE, '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW());
```

### 4. 启动服务

```bash
python main.py
```