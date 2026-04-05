# 🌱 GreenOps: AI-Driven ESG & Carbon Accounting Engine

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Native_Multi--Page-FF4B4B.svg)
![AI](https://img.shields.io/badge/AI_Engine-Llama--3_(Groq)-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

GreenOps is an enterprise-grade Environmental, Social, and Governance (ESG) compliance and predictive analytics engine. Engineered specifically for SMEs (Small and Medium-sized Enterprises), it digitizes the GHG Protocol to track Scope 1, 2, and 3 emissions while utilizing autonomous AI agents to ensure international regulatory compliance (e.g., EU CBAM).

## 🚀 Core Capabilities

### 📊 GHG Protocol Physics Engine
* **Strict Regional Math:** Calculates carbon footprints using geofenced, IPCC/DEFRA-compliant emission factors.
* **Scope Isolation:** Automatically categorizes entries into Scope 1 (Direct), Scope 2 (Purchased Electricity), and Scope 3 (Value Chain).
* **Custom PPAs:** Supports enterprise Power Purchase Agreements (PPAs) with self-verified custom grid overrides.

### 🧠 Autonomous AI Advisory (Llama-3)
* **Context Compression:** Dynamically compresses massive Pandas DataFrames to bypass LLM token limits without losing mathematical accuracy.
* **Regulation Radar:** Cross-references facility locations and export markets against emerging carbon border taxes (e.g., EU CBAM, US frameworks).
* **Optimization Strategy:** Generates real-time CapEx/OpEx operational optimization and verified offset recommendations.

### 🛡️ Enterprise Data Integrity
* **Cryptographic Ingestion:** Uses MD5 row-hashing during bulk CSV uploads to detect and block duplicate data corruption.
* **Zero-Ghost Data:** Server-side validation actively blocks `0.0` quantity logging to prevent artificial deflation of annual run-rate projections.
* **Surgical Range Delete:** Destructive database actions are protected by explicit user verification protocols.

### 📑 Executive Reporting
* **Memory-Safe Architecture:** Bypasses raw-row rendering limits by synthesizing data via `FPDF` into high-level, 1-page executive PDF summaries.
* **Ternary Analytics:** Maps energy transition trajectories (Clean vs. Grid vs. Fossil) using complex Plotly ternary scatter charts.

---

## 🏗️ System Architecture

GreenOps utilizes Streamlit's native multi-page architecture to isolate memory and ensure zero-latency routing.

```text
GreenOps/
├── Home.py                     # UI Landing Page & SaaS Hero Section
├── data_store.py               # Session State Management & Data Persistence
├── ui_components.py            # Reusable UI Components & CSS Styling
├── emission_factors.py         # The Physics Engine: Centralized IPCC/DEFRA constants
├── ai_agents.py                # LLM Interface: CrewAI logic via Groq
├── report_generator.py         # PDF Report Generation Engine (FPDF2)
├── data_generator.py           # Synthetic Data Generation Utilities
├── pyproject.toml              # Project Dependencies & Configuration (uv)
├── .streamlit/
│   └── config.toml             # Theme Config: Hardcoded Light Mode to prevent OS clashing
├── fonts/                      # UTF-8 Font binaries for FPDF export (DejaVu)
├── data/                       # Local JSON storage (emissions.json, settings.json)
└── pages/                      # Isolated Application Modules
    ├── 1_Dashboard.py          # Visual Analytics & Report Generation
    ├── 2_Data_Entry.py         # Dynamic UI Ingestion Pipeline
    ├── 3_AI_Insights.py        # Autonomous Agent Interface
    └── 4_Settings.py           # Global Enterprise Context & Geofencing
```

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/greenops.git
cd greenops
```

### 2. Install dependencies

Using **uv** (recommended):

```bash
uv sync
```

Or using standard **pip**:

```bash
pip install -r requirements.txt
```

**Dependencies include:** `streamlit`, `pandas`, `plotly`, `python-dotenv`, `fpdf2`, `crewai[litellm]`, `uuid`

### 3. Configure Environment Variables

Create a `.env` file in the root directory and add your Groq API key for the AI engine:

```env
GROQ_API_KEY=your_api_key_here
```

### 4. Boot the Application

```bash
streamlit run Home.py
```

---

## 🗄️ Database Structure

Local persistence utilizes flat JSON files mapped to Pandas DataFrames for rapid SME deployment.

### Example `emissions.json` Schema

```json
[
  {
    "date": "2026-04-04",
    "business_unit": "Main Office",
    "scope": "Scope 2",
    "category": "Electricity",
    "activity": "India Grid",
    "country": "India",
    "facility": "Ahmedabad HQ",
    "responsible_person": "Data Officer",
    "quantity": 1500.0,
    "unit": "kWh",
    "emission_factor": 0.82,
    "emissions_kgCO2e": 1230.0
  }
]
```

---

### Acknowledgments

This project was developed starting from an initial architectural reference by AI Anytime. It has since been >95% rewritten, modularized, and enhanced with enterprise-grade ESG physics, cryptographic data guards, and FPDF reporting capabilities.
