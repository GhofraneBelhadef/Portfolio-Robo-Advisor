# 🤖 RoboAdvisor-Portfolio-Personalizer

Welcome to **RoboAdvisor-Portfolio-Personalizer** — an intelligent, in-progress system for personalized investment portfolio management.  
This backend application leverages **AI**, **financial optimization**, and **RAG (Retrieval-Augmented Generation)** to recommend optimal investment allocations based on individual risk profiles, ESG preferences, and financial goals.

It also features a built-in **AI chatbot** (powered by Mistral + RAG) that explains the logic behind portfolio and risk score decisions using data from the SQL database.

---

## 🎯 Project Objective

Build a **Robo-Advisor** capable of:

- Analyzing user financial and psychological profiles
- Recommending investment portfolios (ETF, bonds, stocks, crypto)
- Performing risk-return optimization using the **Markowitz Efficient Frontier**
- Offering periodic rebalancing and performance simulations
- Explaining portfolio decisions using a **retrieval-based LLM chatbot**

---

## 🔥 Key Features

- 🧠 **Client Profiling** via interactive questionnaire (age, income, goals, risk aversion)
- 📊 **Portfolio Optimization** using `cvxpy`, `pypfopt`, `scipy.optimize`
- 💬 **LLM Chatbot with RAG** (Mistral + LangChain + SQL) to explain decisions  
  _Ex: “You got a high risk score because you are 18 with unstable income...”_
- 📈 **Historical Performance Simulation** on portfolios
- 🛠️ **Auto-rebalancing** based on threshold triggers or scheduled intervals
- 📥 **PDF Report Generation** for recommendations

---

## 🧠 AI & Machine Learning

- **Clustering** (e.g., KMeans) for segmenting users
- **Reinforcement Learning** (optional) for adaptive portfolio tuning
- **LLM-based RAG** for interactive question-answering

---

## 📦 Dataset

We use the [Plant Village Dataset](https://www.kaggle.com/datasets/arjuntejaswi/plant-village) 🍃 as a placeholder for initial training and testing.  
In the final product, we integrate live financial APIs like **Yahoo Finance**, **Alpha Vantage**, and **Finnhub** for real-time data.

---

## 🛠️ Tech Stack

| Layer         | Tech / Tools                                                                 |
|---------------|------------------------------------------------------------------------------|
| **Backend**   | Python • FastAPI • Flask                                                     |
| **Optimization** | `cvxpy` • `pypfopt` • `scipy.optimize`                                    |
| **Data Source** | Yahoo Finance • Alpha Vantage • Finnhub                                    |
| **Database**  | PostgreSQL • MongoDB                                                         |
| **AI/NLP**    | Mistral LLM • LangChain • FAISS • SQLite                                     |
| **Deployment**| Docker • Heroku / Render / AWS                                               |

---

## 🧪 Sample Flow

1. 📝 User fills a questionnaire (age, income, goals...)
2. 🧮 System calculates the profile & risk score
3. 💹 Suggests optimized portfolio allocation
4. 📊 Simulates performance & generates graphs
5. 🧠 User asks chatbot "Why this risk score?"
6. 🤖 RAG LLM answers using SQL data (e.g., "You are 18, with low income...")

## 🌐 Frontend Repository

The frontend for this project is developed using **React** and is available here:

🔗 [Portfolio-Advisor Frontend Repository](https://github.com/GhofraneBelhadef/Portfolio-Advisor-front.git)

---

## 🧠 Required Knowledge

- Market Finance: volatility, Sharpe ratio, diversification
- Portfolio Optimization: Efficient Frontier, VaR
- Data Science: Time series, clustering, ML basics
- Backend Development: FastAPI, REST APIs
- Database: PostgreSQL, MongoDB, SQLite
- (Optional) LangChain / LLMs / Prompt engineering

---

## 💼 Project Status

🚧 **Work in progress** — current focus:

- [x] Set up risk scoring and client profiling
- [x] Backend API structure with FastAPI
- [x] Basic LLM RAG chatbot with Mistral
- [ ] Complete portfolio optimization pipeline
- [ ] Add automated PDF report generation
- [ ] Frontend integration and UI polish

---

## 👨‍💻 Author

**Ghofrane Belhadef**  
📧 [ghofrane.belhadef.it@gmail.com](mailto:ghofrane.belhadef.it@gmail.com)  
🔗 [LinkedIn](https://linkedin.com/in/ghofrane-belhadef)  
💻 [GitHub](https://github.com/GhofraneBelhadef)

---

## 📎 Recruiter Note

This backend is part of a larger academic and portfolio project that aims to **democratize financial advisory services** using AI.  
We're combining **machine learning**, **financial optimization**, and **LLMs** to build a tool that’s educational, impactful, and scalable.

Thank you for reviewing this project! 🙏
