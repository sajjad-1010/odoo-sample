# Odoo 19 — Sales Field Project

## Project Overview
Odoo 19 Community with a custom field sales module (`sales_field`) for mobile salespeople in Tajikistan.
Stack: Python 3.12, PostgreSQL 15, OWL 2 frontend, Leaflet.js maps.

## Directory Structure
```
first-odoo/
├── odoo-src/              ← Odoo 19 source (NOT in git, clone separately)
├── custom-addons/
│   ├── sales_field/       ← PRIMARY custom module (in git)
│   ├── my_inventory/      ← Secondary custom module (in git)
│   ├── account-financial-tools/  ← OCA repo (git submodule or clone)
│   ├── account-payment/          ← OCA repo (git submodule or clone)
│   └── account-invoicing/        ← OCA repo (git submodule or clone)
├── nginx/
│   └── odoo.conf          ← nginx reverse proxy config (in git)
├── docker-compose.yml     ← PostgreSQL + nginx via Docker (in git)
├── odoo.conf.example      ← config template (in git, copy to odoo.conf)
├── odoo.conf              ← actual config (NOT in git, has passwords)
├── venv/                  ← Python virtualenv (NOT in git)
├── logs/                  ← log files (NOT in git)
└── certs/                 ← SSL certificates (NOT in git)
```

## Files NOT in Git (must create on new server)

### 1. `odoo.conf` — copy from `odoo.conf.example` and fill in:
```ini
[options]
db_host = localhost
db_port = 5432
db_user = odoo
db_password = YOUR_POSTGRES_PASSWORD
http_port = 8069
workers = 0
addons_path = /path/to/odoo-src/addons,/path/to/custom-addons
logfile = /path/to/logs/odoo.log
log_level = info
admin_passwd = YOUR_MASTER_PASSWORD
```

### 2. `odoo-src/` — clone Odoo 19:
```bash
git clone https://github.com/odoo/odoo.git --depth=1 --branch=19.0 odoo-src
```

### 3. `venv/` — create Python virtualenv:
```bash
python3.12 -m venv venv
venv/bin/pip install -r odoo-src/requirements.txt
venv/bin/pip install "setuptools<74"
```

### 4. `logs/` — create directory:
```bash
mkdir logs
```

### 5. `certs/` — for HTTPS (optional, dev only):
```bash
mkdir certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/key.pem -out certs/cert.pem -subj "/CN=localhost"
```

### 6. OCA repos — clone into custom-addons:
```bash
cd custom-addons
git clone https://github.com/OCA/account-financial-tools.git --branch=19.0 --depth=1
git clone https://github.com/OCA/account-payment.git --branch=19.0 --depth=1
git clone https://github.com/OCA/account-invoicing.git --branch=19.0 --depth=1
```

## Running the Project

### Start infrastructure (PostgreSQL + nginx):
```bash
docker compose up -d
```

### Start Odoo:
```bash
# Windows
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf

# Linux
venv/bin/python odoo-src/odoo-bin -c odoo.conf
```

### Update sales_field module after code changes:
```bash
# Windows
venv\Scripts\python.exe odoo-src\odoo-bin -c odoo.conf -u sales_field -d sj-odoo

# Linux
venv/bin/python odoo-src/odoo-bin -c odoo.conf -u sales_field -d sj-odoo
```

## Custom Module: `sales_field`

### Location: `custom-addons/sales_field/`

### Models:
| Model | File | Purpose |
|---|---|---|
| `field.visit` | `models/field_visit.py` | Visit records with GPS, customer, invoice link |
| `sales.commission.config` | `models/sales_commission_config.py` | Commission rate per salesperson (fixed/tiered) |
| `sales.commission.tier` | `models/sales_commission_config.py` | Tiered commission table |
| `sales.target` | `models/sales_target.py` | Monthly sales target per salesperson |
| `sales.commission.payment` | `models/sales_commission_payment.py` | Commission payment records |
| `res.users` (extend) | `models/res_users_extend.py` | Adds computed commission/target stats to users |

### Frontend (OWL 2 components):
| Component | JS | XML | Purpose |
|---|---|---|---|
| `Dashboard` | `static/src/js/dashboard.js` | `static/src/xml/dashboard.xml` | Main salesperson dashboard |
| `MapView` | `static/src/js/map_widget.js` | `static/src/xml/map_widget.xml` | Leaflet.js visits map (manager) |
| `GpsCapture` | `static/src/js/gps_widget.js` | `static/src/xml/gps_widget.xml` | GPS capture widget in visit form |
| `CustomerBalanceDialog` | `static/src/js/customer_balance.js` | `static/src/xml/customer_balance.xml` | Customer debt popup |
| `CommissionDashboard` | `static/src/js/commission_dashboard.js` | `static/src/xml/commission_dashboard.xml` | Manager commission overview |

### Controllers (JSON-RPC endpoints):
| Route | Auth | Purpose |
|---|---|---|
| `POST /sales_field/visits` | user | Get visits for map |
| `POST /sales_field/customer_balance` | user | Get customer debt + invoices |
| `POST /sales_field/debtors_summary` | user | Get count/total of customers with balance |

### Security Groups:
- `sales_field.group_sales_field_salesperson` — field salespeople
- `sales_field.group_sales_field_manager` — managers (full access)

### Odoo 19 Specific Notes:
- `_sql_constraints` is removed — use `models.Constraint('UNIQUE(...)', 'msg')` as class attribute with `_` prefix
- `name_get()` is deprecated — use `_compute_display_name()` with `@api.depends`
- RPC service removed from JS — use `fetch()` with JSON-RPC format
- `ir.actions.client` target `new` opens dialog
- GPS uses browser `navigator.geolocation` API
- Map uses Leaflet.js loaded from CDN (no API key needed)

## Database
- Name: `sj-odoo`
- Host: localhost:5432
- User: odoo
- Managed by PostgreSQL 15 in Docker

## Common Issues

### Module not updating:
Always specify `-d sj-odoo` — without it Odoo may not find the database.
```bash
venv/bin/python odoo-src/odoo-bin -c odoo.conf -u sales_field -d sj-odoo
```

### 500 error on startup:
Check `logs/odoo.log` — usually a Python syntax error or missing model field.

### Groups not showing in user settings:
Assign groups via URL: `http://localhost:8069/odoo/users/{user_id}/res.groups`
Or: Settings → Technical → Groups (requires developer mode).

### OCA modules not found:
Make sure `addons_path` in `odoo.conf` includes the OCA repo directories.
