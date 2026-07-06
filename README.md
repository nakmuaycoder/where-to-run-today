# 🌲 where-to-run-today

![CI](https://github.com/nakmuaycoder/where-to-run-today/actions/workflows/ci.yml/badge.svg)

🔥 **Forest Fire Risk Monitor – Southern France**

This project monitors the accessibility of forest massifs in several departments of Southern France based on wildfire risk levels published by local prefectures. It helps runners and hikers know exactly where they can safely go during the high-risk summer season.

## 🛡️ Context & Safety

In Southern France, access to forest massifs is strictly regulated from **June 1st to September 30th** due to extreme wildfire risks. These regulations are updated **daily at 5:00 PM (17h)** for the following day.

**Why use this tool?**
Checking the prefecture's website every day before a run can be tedious. This project automates the check and notifies you directly, so you never miss a safe window or risk a heavy fine.

**Why are these restrictions necessary?**
- 🔥 **High Vulnerability**: Heat, wind, and drought make vegetation a "tinderbox".
- 🚶 **Human Origin**: **90% of forest fires are caused by human activity** (negligence, cigarettes, tools).
- 🚑 **Public Safety**: Restrictions protect people from being trapped by smoke or flames.
- 🚒 **Emergency Services**: Less people in the forest means firefighters can focus entirely on fighting the fire front safely.

*This tool helps you respect these vital safety regulations by checking access status daily.*

## ✨ Features

- 🕵️ **Daily Scraping**: Automatically fetches risk levels from [risque-prevention-incendie.fr](https://www.risque-prevention-incendie.fr/).
- 📱 **SMS Notifications**: Sends an alert via Free Mobile SMS API if your favorite forests are open.
- 🔭 **Flexible Watchlist**: Monitor specific massifs or track the entire department using the `"ALL"` keyword.
- 🌍 **Multi-Department Support**: Easily switch between departments (13, 83, 84, 06, etc.).
- 🛠️ **Code Quality**: Pre-commit hooks with **Ruff** for linting/formatting and **detect-secrets** for security.
- 🏠 **NAS Friendly**: Designed to run on a Synology NAS via a simple cron job.

## 🚀 Quick Start

### 📦 Installation

You can use the provided **Makefile** for a quick setup (requires [uv](https://github.com/astral-sh/uv)):

```bash
make install
```

### 🧪 Testing & Quality

Run the unit tests:
```bash
make test
```

Other useful commands:
- `make mock`: Run the scraper with mock data.
- `make lint`: Check code quality with Ruff.
- `make format`: Auto-format code with Ruff.
- `make clean`: Remove temporary files and the virtual environment.

### ⚙️ Configuration

Create/edit `src/config.json` with your credentials and preferences:

```json
{
  "department": "13",
  "free_mobile_user": "YOUR_USER_ID",
  "free_mobile_pass": "YOUR_API_KEY",
  "watchlist": ["ALL"]
}
```

#### 📍 Supported Departments

| Code | Department |
| :--- | :--- |
| **04** | Alpes-de-Haute-Provence |
| **06** | Alpes-Maritimes |
| **11** | Aude |
| **13** | Bouches-du-Rhône (Default) |
| **2A / 2B** | Corsica |
| **26** | Drôme |
| **30** | Gard |
| **34** | Hérault |
| **66** | Pyrénées-Orientales |
| **81** | Tarn |
| **83** | Var |
| **84** | Vaucluse |

### 🧪 Testing

Test the notification system and scraping logic even during off-season using the mock mode:

```bash
uv run src/__main__.py --mock
```

## 📊 Risk Levels

The script interprets the official risk levels as follows:
- 🟢 **Level 1 & 2**: **OPEN** (Access authorized)
- 🔴 **Level 3 & 4**: **CLOSED** (Access prohibited)
- ⚪ **Level 0**: No data (usually off-season)

---
*Created by นักมวยโคเดอร์. Keep running, stay safe!* 🏃💨
