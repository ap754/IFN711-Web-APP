# 设备信息查询与预测系统

一个基于Flask的设备信息管理系统，允许用户登录、注册、查看和添加设备信息。

## 功能特点

- 用户登录与注册
- 设备信息展示与搜索
- 添加新设备
- 支持精确购买日期或估计日期范围

## 技术栈

- Flask (Python Web框架)
- MySQL (数据库)
- HTML/CSS
- Tailwind CSS (样式类)
- Font Awesome (图标)

## 安装与运行

1. 确保已安装Python和MySQL

2. 创建MySQL数据库

```sql
CREATE DATABASE device_management;
```

3. 安装所需Python包

```bash
pip install flask pymysql
```

4. 运行应用

```bash
python app.py
```

5. 在浏览器中访问 http://127.0.0.1:5000

## 数据库配置

- 数据库名称: device_management
- 用户名: root
- 密码: 987654321

## 页面说明

1. 登录页 - 用户登录系统
2. 注册页 - 新用户注册
3. 设备信息页 - 展示设备列表，支持搜索
4. 新增设备页 - 添加新设备信息