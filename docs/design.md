# Smart Financial Coach — Design Document

## 📌 Problem Statement
Personal finance is overwhelming for most users:
- Manual expense tracking is tedious.
- Generic budgeting apps rarely lead to **behavior change**.
- Subscriptions and “gray charges” slip through unnoticed.
- Users lack long-term visibility into **net worth** and future savings trajectory.

**Hackathon Case Alignment:**  
Our project addresses the **Smart Financial Coach** case study, focusing on:
- **Behavioral Change**: actionable, non-judgmental suggestions.  
- **Financial Visibility**: dashboards that clearly explain spending, goals, and net worth.  
- **Trust & Security**: privacy-first, in-memory demo-only design.  
- **AI Application**: lightweight ML + heuristics for categorization, anomaly detection, and forecasting.  

---

## 🎯 Target Audience
- **Young adults and students** looking to form healthy financial habits.  
- **Freelancers/gig workers** with variable income who need clarity.  
- **Everyday users** wanting control over spending, goals, and subscriptions.  

---

## ✨ Features

### 1. Transaction Upload & Analysis
- Upload CSV of transactions.
- Parsing with **Pandas** → clean DataFrame.
- Categorization with **k-NN classifier + heuristics**.
- Charts: **bar, pie, stacked by month**.

### 2. Intelligent Spending Insights
- Top spending categories.
- Detect anomalies (spikes in certain categories).
- Generate **friendly, actionable insights**.

### 3. Savings Goal Calculator & Forecasting
- Input: target savings + timeframe.
- Forecast if user is on/off track.
- Suggest top **3 biggest cut levers** (15–35% reduction scenarios).
- Visualize projected savings over time.

### 4. Subscription & Gray Charge Detector
- Detects recurring payments (merchant + cadence).
- Surfaces forgotten trials, duplicate services, small unnoticed charges.
- Displays as filterable list with monthly totals.
- Provides **links to websites** for subscription management.

### 5. Net Worth Calculator & Projections
- Computes **baseline net worth** from assets, debts, income.
- Projects future net worth under different strategies.
- Visualizes trajectory with **interactive charts**.
- Provides **recommendations to increase net worth**.

---

## 🏗 System Architecture

```text
 ┌─────────────────────┐       ┌──────────────────────────┐
 │      Frontend       │       │         Backend          │
 │ React + Vite        │<----->│ FastAPI (Python)         │
 │ Recharts, Tailwind  │  REST │ Pandas, NumPy, scikit-learn│
 │ Developer Mode      │       │ k-NN categorization       │
 └─────────▲───────────┘       └──────────▲───────────────┘
           │                               │
           │ JSON (analysis, forecasts)    │
           ▼                               ▼
 ┌─────────────────────┐       ┌──────────────────────────┐
 │   User CSV Upload   │─────▶ │   Analysis Engine        │
 │ (transactions)      │       │  - Categorization        │
 │                     │       │  - Insights & Goals      │
 │                     │       │  - Subscription Finder   │
 └─────────────────────┘       └──────────────────────────┘


---

## 🛠 Tech Stack  

### Frontend (User Interface)  
- **React + Vite**: modern, fast development experience.  
- **Recharts**: charts for spending, savings, projections.  
- **TailwindCSS + shadcn/ui**: clean styling and layout.  
- **Developer Mode toggle** to seed demo data quickly.  

### Backend (Business Logic & APIs)  
- **FastAPI (Python)**: lightweight, async-friendly REST API.  
- **Pandas / NumPy**: transaction parsing, aggregation, statistics.  
- **scikit-learn**: k-NN classifier for transaction categorization.  
- **Endpoints implemented (~20)**:  
  - `POST /upload-transactions`  
  - `GET /files/{file_id}/analysis`  
  - `GET /files/{file_id}/subscriptions`  
  - `POST /savings/analyze`  
  - `POST /wealth/optimized-projections`  
  - `GET /files/{file_id}/networth`  
  - …and more.  

### Tools & Infrastructure  
- **Node.js / npm** for frontend.  
- **Python v3.11** + `requirements.txt` for backend.  
- **Uvicorn** for local dev server.  
- **GitHub** for version control & submission.  

---

## 🚀 Getting Started  

### Backend Setup  
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_server.py
Also needs an API key for OpenAI

### Frontend Setup
cd frontend
npm install
npm run devs

Open at http://localhost:5173
```
---

## 🔒 Responsible AI & Privacy

No sensitive data stored: all uploads processed in-memory only.

User override: categories can be re-labeled if AI confidence is low.

Transparency: projections show assumptions and ranges.

Ethics: avoids hard guarantees on outcomes, framed as guidance only.

## 📊 Success Metrics (per case study brief)

Behavioral Change: concrete, non-judgmental suggestions to reduce spend.

Financial Visibility: clean dashboards (insights, subscriptions, goals, projections).

Trust & Security: private, demo-only, with disclaimers.

AI Application: ML for categorization + anomaly detection, forecasting heuristics.

## 📈 Future Enhancements

Direct bank integrations (Plaid, Chase API).

Multi-account merging.

Monte Carlo net worth simulation.

Mobile app interface (React Native).

Advanced explainable AI models for categorization & forecasting.

Wealth maximization strategies on how to tackle credit card debt, and where to spend extra money following these pillars:
1.Credit Card Debt → pay off as fast as possible.

2.Emergency Fund → save until 6 months of expenses.

3.Retirement Match → always invest enough to capture free match.

4.Investing Allocation → 80% into retirement/SPY, 20% into HYSA or high-risk securities.

5. (Optional extension: Major purchase goals or side investments)