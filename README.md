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
    recharge_status ENUM('UNDER_REVIEW', 'APPROVED') DEFAULT 'UNDER_REVIEW' COMMENT '充值状态',
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
    driver_name VARCHAR(50) NOT NULL COMMENT '司机姓名',
    driver_phone VARCHAR(20) NOT NULL COMMENT '司机手机号',
    driver_account_balance INT NOT NULL DEFAULT 0 COMMENT '司机账户余额（分）',
    INDEX idx_driver_phone (driver_phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='司机账户表';

INSERT INTO company_accounts (
    company_account_id,
    company_id,
    company_account_updatetime,
    company_account_balance,
    company_account_balance_warning_val,
    company_account_balance_warning_phone,
    company_account_balance_warning_enable,
    recharge_status,
    recharge_time,
    recharge_name,
    recharge_phone,
    recharge_amount,
    received_amount,
    created_at,
    updated_at
) VALUES
-- 公司1 (余额充足)
('550e8400-e29b-41d4-a716-446655440000', '998a5805-ff3d-477d-a598-8348db542ccf', '2025-07-01 09:00:00', 500000, 100000, '13812345678', TRUE, 'APPROVED', '2025-06-28 14:30:00', '张财务', '13512345678', 200000, 200000, '2024-01-15 10:00:00', '2025-07-01 09:00:00');


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
    driver_account_id VARCHAR(50) COMMENT '司机账户ID',
    INDEX idx_order_id (order_id),
    INDEX idx_path_id (path_id),
    INDEX idx_status (status),
    INDEX idx_company_id (company_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    FOREIGN KEY (driver_account_id) REFERENCES driver_accounts(driver_account_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='费用表';



ALTER TABLE fees
MODIFY COLUMN company_id VARCHAR(36) NULL COMMENT '客户公司ID';

INSERT INTO driver_accounts (
    driver_account_id, 
    driver_phone, 
    driver_name, 
    driver_account_balance
) VALUES (
    'a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8',
    '13812345678',
    '小王',
    125800
);

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
    driver_account_id, 
    created_at, 
    updated_at
) VALUES
('998a5805-ff3d-477d-a598-8348db542cc1', 'Y2025070100001', 'D2025070100001', 'PENDING_PAYMENT', 100, 22, 23, 41, 23, 412, '2025-07-01 09:30:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cc2', 'Y2025070100001', 'D2025070100002', 'PENDING_PAYMENT', 21, 22, 12, 32, 0, 12, '2025-07-01 10:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cc3', 'Y2025070100001', 'D2025070100003', 'PENDING_PAYMENT', 12, 32, 12, 32, 123, 32, '2025-07-01 11:20:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cc4', 'Y2025070200004A', 'D2025070200004', 'SETTLED', 3, 3, 12, 12, 0, 12, '2025-07-02 08:20:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cc5', 'Y2025070200004B', 'D2025070200004', 'SETTLED', 13, 2, 30, 20, 0, 1830, '2025-07-02 14:45:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cc6', 'Y2025070300006', 'D2025070300006', 'PENDING_PAYMENT', 40, 20, 12, 8, 0, 600, '2025-07-03 11:10:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cc7', 'Y2025070300007', 'D2025070300007', 'PENDING_PAYMENT', 100, 95, 40, 25, 0, 2230, '2025-07-03 16:25:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cc8', 'Y2025070400008', 'D2025070400008', 'PENDING_PAYMENT', 60, 40, 10, 12, 0, 10, '2025-07-04 09:45:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cc9', 'Y2025070400008', 'D2025070400009', 'SETTLED', 142, 88, 30, 20, 0, 1980, '2025-07-04 13:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca0', 'Y2025070500010A', 'D2025070500010', 'PENDING_PAYMENT', 30, 20, 800, 400, 0, 350, '2025-07-05 15:40:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca1', 'Y2025070500010B', 'D2025070500010', 'PENDING_PAYMENT', 98, 62, 20, 10, 0, 1590, '2025-07-05 10:25:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca2', 'Y2025070500010C', 'D2025070500010', 'PENDING_PAYMENT', 321, 12, 12, 32, 12, 22, '2025-07-05 18:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca3', 'Y2025070600013A', 'D2025070600013', 'PENDING_PAYMENT', 7, 4, 20, 100, 0, 1160, '2025-07-06 08:50:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca4', 'Y2025070600013B', 'D2025070600013', 'PENDING_PAYMENT', 1111500, 11134, 15200, 1900, 111110, 71180, '2025-07-06 12:30:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca5', 'Y2025070700015', 'D2025070700015', 'PENDING_PAYMENT', 10, 70, 3, 0, 0, 17, '2025-07-07 14:20:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca6', 'Y2025070700015', 'D2025070700016', 'PENDING_PAYMENT', 80, 50, 20, 0, 0, 10, '2025-07-07 11:40:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca7', 'Y2025070800017', 'D2025070800017', 'SETTLED', 12, 32, 12, 23, 0, 26, '2025-07-08 09:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca8', 'Y2025070900018', 'D2025070900018', 'PENDING_PAYMENT', 28, 10, 0, 30, 0, 240, '2025-07-09 16:35:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542ca9', 'Y2025071000019', 'D2025071000019', 'PENDING_PAYMENT', 145, 89, 39, 20, 0, 2070, '2025-07-10 10:25:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cb0', 'Y2025071100020', 'D2025071100020', 'PENDING_PAYMENT', 130, 200, 0, 22, 0, 1900, '2025-07-11 13:50:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cb1', 'Y2025071200021', 'D2025071200021', 'PENDING_PAYMENT', 190, 100, 50, 30, 0, 3090, '2025-07-12 08:30:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cb2', 'Y2025071200021', 'D2025071200022', 'PENDING_PAYMENT', 10, 10, 40, 2800, 0, 24, '2025-07-12 15:45:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cb3', 'Y2025071300023', 'D2025071300023', 'PENDING_PAYMENT', 6850, 4200, 1850, 1250, 0, 10, '2025-07-13 09:20:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cb4', 'Y2025071300023', 'D2025071300024', 'PENDING_PAYMENT', 10300, 6400, 2900, 1850, 0, 30, '2025-07-13 14:15:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cb5', 'Y2025071300023', 'D2025071300025', 'PENDING_PAYMENT', 43, 70, 10, 00, 0, 600, '2025-07-13 17:30:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cb6', 'Y2025071400026A', 'D2025071400026', 'PENDING_PAYMENT', 150, 69, 310, 0, 0, 16, '2025-07-14 11:10:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cb7', 'Y2025071400026B', 'D2025071400026', 'PENDING_PAYMENT', 180, 100, 510, 300, 0, 27, '2025-07-14 16:25:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cb9', 'Y2025071500028B', 'D2025071500028', 'PENDING_PAYMENT', 50, 50, 10, 1050, 0, 92, '2025-07-15 13:55:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW()),
('998a5805-ff3d-477d-a598-8348db542cc0', 'Y2025071500028C', 'D2025071500028', 'APPEALING', 130, 86, 30, 20, 0, 70, '2025-07-15 18:10:00', 'static/test_image.jpg', 'static/test_image.jpg', '998a5805-ff3d-477d-a598-8348db542ccf','a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8', NOW(), NOW());

-- 创建订单详情表
CREATE TABLE IF NOT EXISTS order_details (
    detail_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '详情ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 关联字段
    order_id VARCHAR(50) NOT NULL COMMENT '订单号',
    
    -- 车辆信息
    car_plate VARCHAR(20) COMMENT '车牌号',
    
    -- 地址信息
    loading_addr TEXT COMMENT '装货地址',
    unloading_addr TEXT COMMENT '卸货地址',
    
    -- 联系人信息
    sender_name VARCHAR(50) COMMENT '装货联系人',
    sender_phone VARCHAR(20) COMMENT '装货联系手机号',
    receiver_name VARCHAR(50) COMMENT '卸货联系人',
    receiver_phone VARCHAR(20) COMMENT '卸货联系手机号',
    
    -- 订单时间
    finish_time DATETIME COMMENT '订单完成时间',
    
    -- 货物信息
    goods_volume DECIMAL(10,2) COMMENT '货物方数',
    goods_num INT COMMENT '货物数量',
    goods_weight DECIMAL(10,2) COMMENT '货物重量',
    
    -- 车型和服务配置
    demand_car_type VARCHAR(50) COMMENT '车型选择',
    is_carpool BOOLEAN COMMENT '是否拼车，1-拼车，0-整车',
    need_carry BOOLEAN COMMENT '是否需要搬运服务',
    
    -- 订单备注和总里程
    other_loading_demand TEXT COMMENT '订单备注',
    total_distance DECIMAL(15,2) COMMENT '总里程(米)',
    
    -- 照片信息
    loading_goods_imgs TEXT COMMENT '装货-货物照片',
    loading_car_imgs TEXT COMMENT '装货-车辆照片',
    unloading_goods_imgs TEXT COMMENT '卸货-货物照片',
    unloading_car_imgs TEXT COMMENT '卸货-车辆照片',
    
    -- 索引
    INDEX idx_order_id (order_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单详情表';

INSERT INTO order_details (
    detail_id,
    order_id,
    car_plate,
    loading_addr,
    unloading_addr,
    sender_name,
    sender_phone,
    receiver_name,
    receiver_phone,
    finish_time,
    goods_volume,
    goods_num,
    goods_weight,
    demand_car_type,
    is_carpool,
    need_carry,
    other_loading_demand,
    total_distance,
    loading_goods_imgs,
    loading_car_imgs,
    unloading_goods_imgs,
    unloading_car_imgs,
    created_at,
    updated_at
) VALUES
-- 订单 D2025070100001
('998a5805-ff3d-477d-a598-8348db542dd1', 'D2025070100001', '京A12345', '北京市朝阳区建国路88号', '上海市浦东新区张江高科技园区', '李经理', '13811112222', '王主任', '13922223333', '2025-07-01 16:30:00', 12.5, 50, 3.2, '4.2米厢式货车', FALSE, TRUE, '易碎物品，小心搬运', 125000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070100002
('998a5805-ff3d-477d-a598-8348db542dd2', 'D2025070100002', '京B23456', '北京市海淀区中关村大街1号', '天津市河西区友谊路32号', '张主管', '13544445555', '赵经理', '13655556666', '2025-07-01 14:45:00', 8.2, 30, 2.1, '3.8米平板车', FALSE, FALSE, '准时送达', 98000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070100003
('998a5805-ff3d-477d-a598-8348db542dd3', 'D2025070100003', '京C34567', '北京市丰台区科技园2号', '河北省石家庄市长安区建设大街', '王主任', '13766667777', '李主管', '13877778888', '2025-07-01 13:20:00', 6.8, 25, 1.8, '3.5米厢式货车', TRUE, FALSE, '拼车货物', 85000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070200004
('998a5805-ff3d-477d-a598-8348db542dd4', 'D2025070200004', '京D45678', '北京市通州区物流基地', '江苏省南京市鼓楼区中山路', '刘经理', '13988889999', '陈总监', '15099990000', '2025-07-02 18:30:00', 15.2, 60, 4.5, '6.8米高栏车', FALSE, TRUE, '贵重仪器，防震处理', 320000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070300006
('998a5805-ff3d-477d-a598-8348db542dd6', 'D2025070300006', '京F67890', '北京市昌平区科技园区', '山东省济南市历下区解放路', '周主管', '15122223333', '吴经理', '15233334444', '2025-07-03 15:10:00', 9.5, 35, 2.8, '4.2米冷藏车', FALSE, FALSE, '冷链运输，保持温度', 185000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070300007
('998a5805-ff3d-477d-a598-8348db542dd7', 'D2025070300007', '京G78901', '北京市大兴区生物医药基地', '河南省郑州市金水区花园路', '郑总监', '15344445555', '孙主管', '15455556666', '2025-07-03 20:25:00', 18.6, 70, 5.2, '7.6米厢式货车', FALSE, TRUE, '医疗器械，小心搬运', 280000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070400008
('998a5805-ff3d-477d-a598-8348db542dd8', 'D2025070400008', '京H89012', '北京市顺义区空港物流园', '山西省太原市小店区平阳路', '钱经理', '15566667777', '冯主任', '15677778888', '2025-07-04 13:45:00', 11.3, 45, 3.5, '5.2米平板车', TRUE, FALSE, '拼车货物', 150000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070400009
('998a5805-ff3d-477d-a598-8348db542dd9', 'D2025070400009', '京J90123', '北京市房山区良乡工业区', '内蒙古呼和浩特市新城区新华大街', '陈主管', '15788889999', '褚经理', '15899990000', '2025-07-04 17:15:00', 14.8, 55, 4.1, '6.2米高栏车', FALSE, TRUE, '重型设备，需要叉车', 210000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070500010
('998a5805-ff3d-477d-a598-8348db542da0', 'D2025070500010', '京K01234', '北京市石景山区首钢园', '辽宁省沈阳市和平区中山路', '卫总监', '15922223333', '蒋主管', '16033334444', '2025-07-05 19:40:00', 7.5, 28, 2.3, '4.2米厢式货车', TRUE, FALSE, '拼车货物', 135000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070600013
('998a5805-ff3d-477d-a598-8348db542da3', 'D2025070600013', '京N34567', '北京市门头沟区石龙工业区', '吉林省长春市朝阳区人民大街', '沈经理', '16366667777', '韩主任', '16477778888', '2025-07-06 12:50:00', 10.2, 38, 3.0, '5.2米厢式货车', FALSE, TRUE, '易碎品，小心轻放', 175000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070700015
('998a5805-ff3d-477d-a598-8348db542da5', 'D2025070700015', '京P56789', '北京市怀柔区科学城', '黑龙江省哈尔滨市南岗区西大直街', '杨主管', '16588889999', '朱经理', '16699990000', '2025-07-07 18:20:00', 16.5, 65, 4.8, '7.2米高栏车', FALSE, TRUE, '重型机械，需要吊车', 265000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070700016
('998a5805-ff3d-477d-a598-8348db542da6', 'D2025070700016', '京Q67890', '北京市平谷区物流基地', '安徽省合肥市蜀山区长江西路', '秦总监', '16722223333', '尤主管', '16833334444', '2025-07-07 15:40:00', 12.8, 48, 3.8, '6.2米平板车', TRUE, FALSE, '拼车货物', 195000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070800017
('998a5805-ff3d-477d-a598-8348db542da7', 'D2025070800017', '京R78901', '北京市密云区经济开发区', '福建省福州市鼓楼区五四路', '许经理', '16944445555', '何主任', '17055556666', '2025-07-08 13:15:00', 20.3, 75, 6.2, '9.6米厢式货车', FALSE, TRUE, '大型设备，专业装卸', 350000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025070900018
('998a5805-ff3d-477d-a598-8348db542da8', 'D2025070900018', '京S89012', '北京市延庆区工业园', '江西省南昌市东湖区阳明路', '吕主管', '17166667777', '施经理', '17277778888', '2025-07-09 20:35:00', 5.5, 20, 1.5, '3.8米厢式货车', TRUE, FALSE, '小件拼车', 95000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025071000019
('998a5805-ff3d-477d-a598-8348db542da9', 'D2025071000019', '京T90123', '北京市朝阳区CBD核心区', '山东省青岛市市南区香港中路', '孔总监', '17388889999', '曹主管', '17499990000', '2025-07-10 14:25:00', 13.6, 52, 4.0, '6.8米高栏车', FALSE, TRUE, '精密仪器，防震包装', 225000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025071100020
('998a5805-ff3d-477d-a598-8348db542db0', 'D2025071100020', '京U01234', '北京市海淀区上地信息产业基地', '河南省洛阳市涧西区南昌路', '严经理', '17522223333', '华主任', '17633334444', '2025-07-11 17:50:00', 17.2, 68, 5.0, '7.6米厢式货车', FALSE, TRUE, '重型设备，专业装卸', 275000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025071200021
('998a5805-ff3d-477d-a598-8348db542db1', 'D2025071200021', '京V12345', '北京市丰台区总部基地', '湖北省武汉市武昌区中南路', '金主管', '17744445555', '魏经理', '17855556666', '2025-07-12 12:30:00', 19.5, 72, 6.0, '8.6米平板车', FALSE, TRUE, '大型机械，需要吊装', 310000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025071200022
('998a5805-ff3d-477d-a598-8348db542db2', 'D2025071200022', '京W23456', '北京市通州区张家湾开发区', '湖南省长沙市芙蓉区五一大道', '陶总监', '17966667777', '姜主管', '18077778888', '2025-07-12 19:45:00', 15.8, 62, 4.7, '7.2米高栏车', TRUE, FALSE, '拼车货物', 255000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025071300023
('998a5805-ff3d-477d-a598-8348db542db3', 'D2025071300023', '京X34567', '北京市昌平区沙河工业园', '广东省广州市天河区体育西路', '戚经理', '18188889999', '谢主任', '18299990000', '2025-07-13 13:20:00', 11.5, 42, 3.3, '5.8米厢式货车', FALSE, TRUE, '易碎品，小心搬运', 185000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025071300024
('998a5805-ff3d-477d-a598-8348db542db4', 'D2025071300024', '京Y45678', '北京市大兴区亦庄开发区', '广西南宁市青秀区民族大道', '邹主管', '18322223333', '喻经理', '18433334444', '2025-07-13 18:15:00', 14.2, 53, 4.2, '6.5米平板车', TRUE, FALSE, '拼车货物', 205000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025071300025
('998a5805-ff3d-477d-a598-8348db542db5', 'D2025071300025', '京Z56789', '北京市顺义区空港开发区', '海南省海口市龙华区滨海大道', '柏总监', '18544445555', '水主管', '18655556666', '2025-07-13 21:30:00', 8.8, 32, 2.6, '4.5米厢式货车', FALSE, FALSE, '普通货物', 145000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025071400026
('998a5805-ff3d-477d-a598-8348db542db6', 'D2025071400026', '京A67890', '北京市房山区燕山工业区', '四川省成都市锦江区红星路', '章经理', '18766667777', '云主任', '18877778888', '2025-07-14 15:10:00', 12.3, 46, 3.6, '5.5米高栏车', FALSE, TRUE, '精密仪器，防震包装', 195000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW()),

-- 订单 D2025071500028
('998a5805-ff3d-477d-a598-8348db542db8', 'D2025071500028', '京C89012', '北京市石景山区八大处科技园', '贵州省贵阳市云岩区中华北路', '鲁主管', '19122223333', '危经理', '19233334444', '2025-07-15 13:40:00', 9.2, 34, 2.8, '4.8米厢式货车', TRUE, FALSE, '拼车货物', 165000.00, 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', 'static/test_image.jpg', NOW(), NOW());
```

### 4. 启动服务

```bash
python main.py
```