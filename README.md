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
    status ENUM('APPEALING', 'PENDING_PAYMENT', 'PENDING_SETTLEMENT','SETTLED') NOT NULL DEFAULT 'APPEALING' COMMENT '订单状态',
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
    highway_bill_imgs, 
    parking_bill_imgs, 
    company_id, 
    created_at, 
    updated_at
) VALUES
('test_001', 'Y2025070100001', 'D2025070100001', 'PENDING_PAYMENT', 5900, 3500, 1500, 1000, 1500, 800, '2025-07-01 09:30:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_002', 'Y2025070100001', 'D2025070100002', 'PENDING_PAYMENT', 3950, 2500, 1000, 500, 0, 650, '2025-07-01 10:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_003', 'Y2025070100001', 'D2025070100003', 'PENDING_PAYMENT', 2950, 1800, 800, 300, 0, 450, '2025-07-01 11:20:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_004', 'Y2025070200004A', 'D2025070200004', 'SETTLED', 8950, 5200, 2500, 1500, 0, 1250, '2025-07-02 08:20:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_005', 'Y2025070200004B', 'D2025070200004', 'SETTLED', 12800, 7800, 3500, 2000, 0, 1830, '2025-07-02 14:45:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_006', 'Y2025070300006', 'D2025070300006', 'PENDING_PAYMENT', 4500, 2800, 1200, 800, 0, 600, '2025-07-03 11:10:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_007', 'Y2025070300007', 'D2025070300007', 'APPEALING', 15600, 9500, 4200, 2500, 0, 2230, '2025-07-03 16:25:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_008', 'Y2025070400008', 'D2025070400008', 'SETTLED', 6750, 4100, 1800, 1200, 0, 1020, '2025-07-04 09:45:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_009', 'Y2025070400008', 'D2025070400009', 'SETTLED', 14200, 8800, 3800, 2200, 0, 1980, '2025-07-04 13:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_010', 'Y2025070500010A', 'D2025070500010', 'APPEALING', 3250, 2000, 800, 400, 0, 350, '2025-07-05 15:40:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_011', 'Y2025070500010B', 'D2025070500010', 'APPEALING', 9800, 6200, 2800, 1800, 0, 1590, '2025-07-05 10:25:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_012', 'Y2025070500010C', 'D2025070500010', 'APPEALING', 5800, 3600, 1600, 1000, 0, 890, '2025-07-05 18:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_013', 'Y2025070600013A', 'D2025070600013', 'PENDING_PAYMENT', 7650, 4800, 2000, 1400, 0, 1160, '2025-07-06 08:50:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_014', 'Y2025070600013B', 'D2025070600013', 'PENDING_PAYMENT', 5450, 3400, 1500, 900, 0, 780, '2025-07-06 12:30:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_015', 'Y2025070700015', 'D2025070700015', 'APPEALING', 11800, 7200, 3200, 2000, 0, 1720, '2025-07-07 14:20:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_016', 'Y2025070700015', 'D2025070700016', 'APPEALING', 8750, 5500, 2400, 1600, 0, 1380, '2025-07-07 11:40:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_017', 'Y2025070800017', 'D2025070800017', 'SETTLED', 17800, 10800, 4800, 3000, 0, 2620, '2025-07-08 09:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_018', 'Y2025070900018', 'D2025070900018', 'PENDING_PAYMENT', 2800, 1800, 600, 300, 0, 240, '2025-07-09 16:35:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_019', 'Y2025071000019', 'D2025071000019', 'SETTLED', 14550, 8900, 3900, 2400, 0, 2070, '2025-07-10 10:25:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_020', 'Y2025071100020', 'D2025071100020', 'APPEALING', 13250, 8200, 3600, 2200, 0, 1900, '2025-07-11 13:50:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_021', 'Y2025071200021', 'D2025071200021', 'PENDING_PAYMENT', 19800, 12200, 5500, 3500, 0, 3090, '2025-07-12 08:30:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_022', 'Y2025071200021', 'D2025071200022', 'PENDING_PAYMENT', 16750, 10200, 4500, 2800, 0, 2460, '2025-07-12 15:45:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_023', 'Y2025071300023', 'D2025071300023', 'SETTLED', 6850, 4200, 1850, 1250, 0, 1040, '2025-07-13 09:20:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_024', 'Y2025071300023', 'D2025071300024', 'SETTLED', 10300, 6400, 2900, 1850, 0, 1630, '2025-07-13 14:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_025', 'Y2025071300023', 'D2025071300025', 'SETTLED', 4350, 2700, 1150, 700, 0, 600, '2025-07-13 17:30:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_026', 'Y2025071400026A', 'D2025071400026', 'SETTLED', 11250, 6900, 3100, 1900, 0, 1650, '2025-07-14 11:10:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_027', 'Y2025071400026B', 'D2025071400026', 'SETTLED', 18550, 11500, 5100, 3200, 0, 2780, '2025-07-14 16:25:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_028', 'Y2025071500028A', 'D2025071500028', 'APPEALING', 8900, 5500, 2450, 1550, 0, 1350, '2025-07-15 09:40:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_029', 'Y2025071500028B', 'D2025071500028', 'APPEALING', 6150, 3850, 1700, 1050, 0, 920, '2025-07-15 13:55:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW()),
('test_030', 'Y2025071500028C', 'D2025071500028', 'APPEALING', 13800, 8600, 3850, 2350, 0, 2070, '2025-07-15 18:10:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf', NOW(), NOW());

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


```

### 4. 启动服务

```bash
python main.py
```