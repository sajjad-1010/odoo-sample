# Odoo 19 Community - دستورات اجرا

## ساختار پروژه
```
first-odoo/
├── docker-compose.yml          ← PostgreSQL
├── odoo.conf                   ← تنظیمات Odoo
├── odoo-src/                   ← سورس کد Odoo 19
├── custom-addons/
│   ├── account-financial-tools/  ← OCA 19.0: ابزارهای حسابداری پیشرفته
│   ├── account-payment/          ← OCA 19.0: مدیریت پرداخت
│   └── my_inventory/             ← ماژول سفارشی انبار با minimap
├── logs/                       ← فایل‌های لاگ
└── venv/                       ← Python 3.12 محیط مجازی
```

---

## راه‌اندازی (اولین بار و هر بار بعد از ریستارت سیستم)

### مرحله ۱ - دیتابیس را بالا بیاور

```bat
cd D:\odoo\first-odoo
docker compose up -d
```

برای بررسی وضعیت:
```bat
docker compose ps
```

### مرحله ۲ - Odoo را اجرا کن

```bat
cd D:\odoo\first-odoo
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf
```

بعد از اجرا، مرورگر را باز کن:
**http://localhost:8069**

---

## دستورات متداول

### متوقف کردن Odoo
```
Ctrl + C
```

### متوقف کردن دیتابیس
```bat
docker compose down
```

### نصب یک ماژول خاص (اولین بار)
```bat
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf -d YOUR_DB_NAME -i module_name --stop-after-init
```

### آپدیت یک ماژول
```bat
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf -d sajjad.newnew -u my_inventory --stop-after-init
```

### اجرا در حالت debug
```bat
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf --dev=all
```

---

## ماژول سفارشی

ماژول‌های خودت را در پوشه `custom-addons/` بساز.
Odoo به صورت خودکار آن‌ها را پیدا می‌کند (در `odoo.conf` تنظیم شده).

ساختار یک ماژول:
```
custom-addons/
└── my_module/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    ├── views/
    └── security/
```

---

## OCA Modules موجود (نسخه 19.0)

> توجه: OCA هنوز همه ماژول‌ها رو به 19 پورت نکرده. فقط موارد زیر در 19.0 موجودن.

### account-financial-tools
| ماژول | توضیح |
|-------|-------|
| `account_account_tag_code` | کد برای تگ‌های حسابداری |
| `account_journal_restrict_mode` | محدود کردن ویرایش ژورنال |
| `account_move_name_sequence` | شماره‌گذاری سفارشی اسناد |
| `account_move_post_date_user` | نمایش تاریخ و کاربر ثبت سند |
| `account_move_print` | چاپ اسناد حسابداری |
| `account_usability` | بهبودهای کاربری حسابداری |

### account-payment
| ماژول | توضیح |
|-------|-------|
| `account_check_printing_report_base` | پایه گزارش چاپ چک |
| `account_due_list` | لیست سررسید پرداخت‌ها |
| `account_payment_method_base` | پایه روش‌های پرداخت |

برای نصب هر ماژول در Odoo:
```
Apps → Update Apps List → جستجو → نصب
```

---

## Staging Environment

### ساخت staging از روی backup production

```bat
# ۱. backup از prod
docker exec odoo_postgres pg_dump -U odoo YOUR_DB_NAME > backup.sql

# ۲. ساخت staging_db
docker exec odoo_postgres createdb -U odoo staging_db

# ۳. ریختن دیتا توی staging_db
docker exec -i odoo_postgres psql -U odoo staging_db < backup.sql
```

### اجرای staging (همزمان با production)

```bat
cd D:\odoo\first-odoo
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo_staging.conf
```

آدرس staging: **http://localhost:8070**
آدرس production: **http://localhost:8069**

### آپدیت و تست روی staging قبل از production

```bat
# migrate روی staging
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo_staging.conf -d staging_db -u all --stop-after-init

# اگه OK بود، همین کار رو روی prod انجام بده
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf -d sajjad.newnew -u all --stop-after-init
```

---

## رفع مشکل رایج

### اگر خطای pkg_resources گرفتی:
```bat
venv\Scripts\pip.exe install "setuptools<74"
```

### اگر دیتابیس وصل نشد:
```bat
docker compose ps   # بررسی کن که postgres در حال اجراست
```
