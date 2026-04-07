# Smart Municipal Tax Record Management System

A polished local web dashboard for managing municipal tax holding data from Excel. This project is designed for academic defense presentations and as a professional portfolio showcase.

## Project Overview

The **Smart Municipal Tax Record Management System** helps municipal offices analyze and manage holding tax records using a clean admin-style dashboard.

It provides:
- advanced search across key identity fields
- combined multi-criteria filters
- summary analytics cards
- interactive charts (Chart.js)
- data validation insights (missing/incomplete records)
- one-click export of currently filtered rows to Excel

## Tech Stack

### Backend
- Python
- Flask
- Pandas
- OpenPyXL

### Frontend
- HTML
- CSS
- Vanilla JavaScript
- Chart.js

## Folder Structure

```bash
tax_project/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── ccc_holding_data_collection.xlsx
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Data Source Requirements

Place your Excel file at:

```bash
data/ccc_holding_data_collection.xlsx
```

Sheet name must be:

```bash
Holding
```

Expected columns (minor case/space formatting differences are handled automatically):
- holding
- circle_office
- ward
- moholla
- rate
- owner_name
- holding_name
- swo_relation
- swo_name
- address
- mobile
- type
- beneficiary_type
- note

## Features

### 1) Dashboard Analytics
- Total Records
- Total Wards
- Total Mohollas
- Incomplete Records

### 2) Interactive Charts
- Records per Ward
- Top Mohollas by Record Count
- Rate Distribution

### 3) Search
Case-insensitive global search on:
- owner_name
- holding
- swo_name

### 4) Combined Filters
Filter by:
- ward
- moholla
- rate
- type

All filters work together.

### 5) Data Table
Includes:
- sticky table header
- responsive horizontal scrolling
- clean striped rows + hover effects

### 6) Data Validation Insights
Shows counts for:
- missing owner_name
- missing mobile
- missing moholla
- total incomplete rows

### 7) Export
Use **Download Filtered Data** to export currently filtered rows to Excel.

## Setup and Run

### 1. Clone or Download Repository
```bash
git clone <your-repository-url>
cd tax_project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```

### 4. Open in Browser
```bash
http://127.0.0.1:5000
```

## Notes for Users

- If the Excel file is missing, the dashboard will still load with empty data safely.
- Optional blank cells do not crash the application.
- Column names are normalized automatically to avoid breakage from spacing/case variations.

## License

This project is suitable for academic and portfolio use. You can add your preferred license (e.g., MIT) before publishing.
