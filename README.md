# Smart Financial Coach 💰  

An AI-powered financial coach that transforms raw transaction data into **actionable insights** — helping users understand their spending, set and achieve goals, and eliminate hidden recurring costs.  

Built for the Palo Alto Networks IT Hackathon 2025, Case Study.  

> 🎥 **Demo Video (5–7 minutes):** [ADD YOUTUBE OR VIMEO LINK HERE]  
> 📄 **Design Doc:** See `/docs/design.md`  

---

## 📌 Problem Statement  

Managing personal finances is overwhelming. Manual tracking is tedious, and generic budgeting apps fail to drive behavior change. Users often:  

- Lack **visibility** into where their money is going.  
- Miss opportunities to save or cut expenses.  
- Overlook recurring subscriptions or “gray charges.”  
- Feel anxious about long-term financial stability.  

The **Smart Financial Coach** addresses these pain points by leveraging AI + heuristics to **analyze spending, forecast goals, and suggest concrete, non-judgmental actions**.  

---

## ✨ Features  

### 1. **Transaction Upload & Analysis**  
- Upload a CSV of transactions.  
- Automatic parsing with Pandas → clean DataFrame.  
- Categorization via lightweight ML (k-NN, text vectorization) + heuristics.  
- Charts: bar, pie, stacked by month.  

### 2. **Intelligent Spending Insights**  
- Detect top spending categories.  
- Identify anomalies (“spike in rideshare this month”).  
- Friendly insights (“$120 spent on coffee; brewing at home could save $1,000/year”).  

### 3. **Savings Goal Calculator & Forecasting**  
- Input: target amount + timeframe.  
- Forecast progress based on current income/expenses.  
- If off-track, system suggests **3 biggest cut levers** (randomized 15–35% reductions to simulate behavior change).  
- Output: projected savings curve with/without cuts.  

### 4. **Subscription & Gray Charge Detector**  
- Scans for recurring transactions by merchant + cadence.  
- Flags forgotten free trials, duplicate services, small unnoticed charges.  
- Displays as a clean, filterable list with monthly totals.  
- Automatically finds websites for some subscriptions to easily manage them.

### 5. **Net Worth Calculator & Projections**  
- Computes baseline net worth from assets, debts, and income.  
- Projects future net worth based on spending cuts and investment strategy.  
- Visualized as a time-series chart.  
- Suggests changes on how to increase net worth and visually allows you to see how those changes will affect your net worth.


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
uvicorn app:app --reload --port 8000
Also needs an API key for OpenAI

### Frontend Setup
cd frontend
npm install
npm run dev

Open at http://localhost:5173

###🔒 Responsible AI & Privacy

No sensitive data stored: all uploads processed in-memory only.

User override: categories can be re-labeled if AI confidence is low.

Transparency: projections show assumptions and ranges.

Ethics: avoids hard guarantees on outcomes, framed as guidance only.

###📊 Success Metrics (per case study brief)

Behavioral Change: concrete, non-judgmental suggestions to reduce spend.

Financial Visibility: clean dashboards (insights, subscriptions, goals, projections).

Trust & Security: private, demo-only, with disclaimers.

AI Application: ML for categorization + anomaly detection, forecasting heuristics.

📈 Future Enhancements

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