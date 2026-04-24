# Odoo 19 Community — دستورات اجرا

## ساختار پروژه
```
first-odoo/
├── docker-compose.yml          ← PostgreSQL + nginx
├── odoo.conf                   ← تنظیمات Odoo (در گیت نیست)
├── odoo.conf.example           ← نمونه تنظیمات (در گیت هست)
├── odoo-src/                   ← سورس کد Odoo 19 (در گیت نیست)
├── custom-addons/
│   ├── sales_field/            ← ماژول اصلی فروش میدانی
│   ├── my_inventory/           ← ماژول انبار
│   ├── account-financial-tools/
│   ├── account-payment/
│   └── account-invoicing/
├── nginx/odoo.conf             ← تنظیمات nginx
├── logs/                       ← فایل‌های لاگ (در گیت نیست)
└── venv/                       ← محیط مجازی Python (در گیت نیست)
```

---

## راه‌اندازی (هر بار بعد از ریستارت سیستم)

### مرحله ۱ — دیتابیس و nginx را بالا بیاور
```bat
docker compose up -d
```

### مرحله ۲ — Odoo را اجرا کن
```bat
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf
```

آدرس: **http://localhost:8069**

---

## دستورات متداول

### آپدیت ماژول sales_field
```bat
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf -u sales_field -d sj-odoo
```

### آپدیت و بعد خاموش شدن (برای CI/اسکریپت)
```bat
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf -u sales_field -d sj-odoo --stop-after-init
```

### اجرا در حالت debug
```bat
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf --dev=all
```

### متوقف کردن دیتابیس
```bat
docker compose down
```

### نصب ماژول جدید (اولین بار)
```bat
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf -d sj-odoo -i MODULE_NAME --stop-after-init
```

---

## لاگ‌ها
```bat
# آخرین ۵۰ خط لاگ
tail -50 logs/odoo.log

# لاگ زنده
Get-Content logs\odoo.log -Wait -Tail 30
```

---

## Staging (تست موازی با production)

```bat
# backup از prod
docker exec odoo_postgres pg_dump -U odoo sj-odoo > backup.sql

# ساخت و پر کردن staging
docker exec odoo_postgres createdb -U odoo staging_db
docker exec -i odoo_postgres psql -U odoo staging_db < backup.sql

# اجرا staging روی پورت 8070
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo_staging.conf
```

---

## رفع مشکل رایج

### خطای pkg_resources
```bat
venv\Scripts\pip.exe install "setuptools<74"
```

### دیتابیس وصل نشد
```bat
docker compose ps
```

### ماژول آپدیت نشد (0 queries)
حتماً `-d sj-odoo` را اضافه کن — بدون آن Odoo دیتابیس را پیدا نمی‌کند.

### 500 Internal Server Error
```bat
tail -20 logs/odoo.log
```
