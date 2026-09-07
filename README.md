---
title: AI Export Facilitation Agent
emoji: 🚢
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: "1.35.0"
app_file: app.py
pinned: false
license: mit
short_description: AI guide for exporting products from India. RAG + Voice.
---

# 🚀 AI Export Facilitation Agent (India Export AI)

> **Your intelligent, trustworthy AI guide for exporting products from India to the world.**

---

## 💡 What is this project? (Explained Simply)

Starting an export business from India can feel overwhelming. Exporters often get confused searching across dozens of scattered government websites (DGFT, RBI, ICEGATE, Customs, FIEO, etc.) or consulting expensive agents. A single wrong document or incorrect product code can delay a shipment by weeks!

The **AI Export Facilitation Agent** solves this problem! It is an AI-powered assistant designed specifically for Indian small business owners and first-time exporters.

### 🌟 Key Highlights:
* 🤖 **Smart & Accurate**: Uses **RAG (Retrieval-Augmented Generation)** to look up official rules from verified government documents before answering.
* 🛡️ **Zero Hallucination / No Guessing**: The AI **never invents rules or numbers**. If it isn't sure, it cites official government sources instead of guessing.
* 📜 **Source Citing**: Every answer shows exact official sources (e.g., *DGFT Foreign Trade Policy, RBI Master Directions, CBIC Customs Manual*).
* 🎙️ **Voice Enabled**: Speak your query aloud (Speech-to-Text) and listen to spoken voice responses (Text-to-Speech).
* 💰 **100% Free to Run**: Built entirely using free-tier tools (Groq / Google Gemini APIs, local ChromaDB vector search).

---

## 🎯 13 Topics Covered

1. **How to Start Exporting** (First steps, registering your business)
2. **Export Procedures & Documentation** (Invoices, Packing lists, Bills of Lading, Shipping Bills)
3. **Government Registrations** (IEC Code, GST registration, AD Code, RCMC certificate)
4. **HS Code Guidance** (Finding the right 6-digit/8-digit trade classification code)
5. **Incoterms Simplified** (FOB, CIF, EXW, DDP — who pays for shipping & insurance)
6. **Logistics & Customs Clearance** (Port procedures, ICEGATE filing, customs duty)
7. **Payment Methods & Safety** (Letters of Credit / LC, Advance Payment, Bank Guarantees)
8. **Govt Schemes & Incentives** (RoDTEP, Duty Drawback, Advance Authorisation)
9. **Certifications & Compliance** (FSSAI export permission, ISO, Phytosanitary certificates)
10. **Country Import Rules** (USA, EU, UAE import requirements for Indian goods)
11. **Trade Intelligence** (Top importing countries for Indian goods)
12. **Trade Fairs & Exhibitions** (Events organized by Export Promotion Councils)
13. **Instant FAQs** (Quick answers to common exporter questions)

---

## 🛠️ What You Need Before Starting (Prerequisites)

Make sure you have the following installed on your computer:

1. **Python** (version `3.10` or higher) — [Download Python](https://www.python.org/downloads/)
2. **Node.js** (version `18` or higher) — [Download Node.js](https://nodejs.org/)
3. **Git** — [Download Git](https://git-scm.com/)
4. **A Free API Key** from Groq (Recommended) or Google Gemini:
   * **Groq API Key (Free & Super Fast)**: Get it in 1 minute at [https://console.groq.com](https://console.groq.com)
   * *(Optional)* **Gemini API Key**: Get it at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

## 🚀 Quick Start Guide (How to Clone & Run)

Follow these easy step-by-step instructions to get the application running on your computer.

### Step 1: Clone the Repository

Open your terminal or Command Prompt (CMD) and run:

```bash
git clone https://github.com/arpitcodelab/Ai-export-Agent.git
cd Ai-export-Agent
```

---

### Step 2: Set Up the Python Backend & API Key

1. **Create and activate a virtual environment**:

   * **On Windows (Command Prompt / PowerShell)**:
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```
   * **On Mac / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

2. **Install Python dependencies**:
   ```bash
   pip install -r export-agent/requirements.txt
   pip install -r frontend/backend/requirements.txt
   ```

3. **Configure your API Key**:
   * Navigate to the `export-agent` folder.
   * Make a copy of `.env.example` and name it `.env`:
     * On Windows: `copy export-agent\.env.example export-agent\.env`
     * On Mac/Linux: `cp export-agent/.env.example export-agent/.env`
   * Open `export-agent/.env` in any text editor (VS Code, Notepad).
   * Replace `your_groq_api_key_here` with your actual free Groq API key:
     ```env
     GROQ_API_KEY=gsk_YourActualGroqApiKeyHere...
     LLM_PROVIDER=groq
     ```

---

### Step 3: Launch the Application!

You can run the app in two ways:

#### 🌟 Option A: Modern React Web App + FastAPI Backend (Recommended)

1. **Start the FastAPI Backend Server**:
   Open Terminal #1:
   ```bash
   cd frontend/backend
   python main.py
   ```
   *(Backend will start running at `http://localhost:8000`)*

2. **Start the React Frontend UI**:
   Open Terminal #2:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *(Frontend will start running at `http://localhost:5173`)*

3. **Open your browser** and go to: **`http://localhost:5173`** 🎉

---

#### 🎈 Option B: Run the Streamlit Prototype App

If you prefer a single-screen Streamlit chat window:

Open Terminal:
```bash
cd export-agent
streamlit run app.py
```
*(Streamlit app will open automatically at `http://localhost:8501`)*

---

## 📁 Project Folder Structure

Here is how the project is organized:

```text
Ai-export-Agent/
├── export-agent/                  # Core RAG AI Pipeline & Streamlit App
│   ├── app.py                     # Streamlit frontend application
│   ├── .env.example               # Environment configuration template
│   ├── data/
│   │   ├── processed/             # Processed Knowledge Base JSON & Excel files
│   │   └── vector_store/          # ChromaDB local vector database embeddings
│   ├── src/
│   │   ├── agent.py               # Main RAG AI pipeline (Groq / Gemini)
│   │   ├── retriever.py           # ChromaDB search & vector retriever
│   │   ├── nlp.py                 # Query intent classifier (13 export domains)
│   │   ├── prompts.py             # Anti-hallucination prompt instructions
│   │   ├── voice.py               # Speech-to-Text & Text-to-Speech module
│   │   ├── ingest.py              # Raw document parser & JSON builder
│   │   └── build_index.py         # ChromaDB index builder
│   └── tests/                     # Automated testing suite & benchmark questions
│
├── frontend/                      # Modern Web Interface (React + Vite)
│   ├── backend/
│   │   └── main.py                # FastAPI REST server bridging RAG logic
│   ├── src/                       # React components (Chat, Hero, Coverage, Voice)
│   └── package.json               # Node.js dependencies
│
├── files/                         # Project Documentation & Specifications
│   ├── PRD.md                     # Product Requirements Document
│   ├── TECH_STACK.md              # Technical stack breakdown & cost analysis
│   ├── ROADMAP.md                 # Future expansion roadmap (WhatsApp bot, etc.)
│   └── AGENT_RULES.md             # System prompt rules & safety guardrails
│
└── README.md                      # Project user guide (You are here!)
```

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>1. Is this app free to use?</b></summary>
Yes! The app runs completely on free-tier tools: free Groq or Gemini API keys, local ChromaDB embeddings (`sentence-transformers`), and open-source packages.
</details>

<details>
<summary><b>2. What if I get an "API Key Not Configured" error?</b></summary>
Make sure you created a file named <code>.env</code> inside the <code>export-agent/</code> directory (not <code>.env.txt</code>) and added your valid <code>GROQ_API_KEY</code>.
</details>

<details>
<summary><b>3. How do I rebuild or refresh the knowledge base index?</b></summary>
If you update the knowledge base JSON or Excel files in <code>export-agent/data/processed/</code>, you can rebuild the vector search index by running:
<pre>python export-agent/src/build_index.py</pre>
</details>

---

## 🤝 Contributing & Feedback

Contributions, feedback, and feature suggestions are welcome! Feel free to open an Issue or Submit a Pull Request.

---

<p center>Made with ❤️ to empower Indian Exporters worldwide 🇮🇳✨</p>
