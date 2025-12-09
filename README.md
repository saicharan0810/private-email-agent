# 🔒 Private AI Email Agent

**A Local-First, Multi-Modal Email Assistant powered by Llama 3.2.**

This application connects securely to your Gmail inbox to analyze, summarize, and manage emails without sending your private data to the cloud. It runs entirely on your local machine using **Ollama** for inference, **Tesseract** for OCR, and **gTTS** for audio briefings.

## 🚀 Key Features
* **🛡️ Privacy First:** Uses local LLMs (Llama 3.2) so email content never leaves your device.
* **🧠 Auto-Triage Agent:** Automatically classifies emails (Job Apps, Security, Spam) using a Hybrid Rule+AI engine.
* **🎙️ Morning Podcast Mode:** Converts your top priority emails into a spoken audio briefing to listen to while commuting.
* **👁️ Visual Intelligence (OCR):** Detects text inside images (screenshots, receipts) using Tesseract OCR.
* **✍️ Smart Drafts:** Generates context-aware replies and saves them directly to your **Gmail Drafts** folder.
* **📊 Analytics Dashboard:** Visualizes sender activity and inbox composition.
* **⚡️ Fast & Efficient:** Optimized for local execution, providing quick responses without cloud latency.

## 🛠️ Tech Stack

* **Frontend:** Streamlit (Python)
* **AI Inference:** Ollama (Llama 3.2)
* **Computer Vision:** Tesseract OCR / PyTesseract
* **Audio:** gTTS (Google Text-to-Speech)
* **Email Protocol:** IMAP/SMTP for secure email handling

## ⚙️ Installation & Setup

### 1. Prerequisites
* **Python 3.8+**
* **Ollama:** [Download here](https://ollama.com) and run `ollama pull llama3.2`
* **Tesseract OCR:** * *Mac:* `brew install tesseract`
    * *Windows:* [Download Installer](https://tesseract-ocr.github.io/tessdoc/Installation.html)

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt

### 3. Get a Google App Password

To connect securely, you must generate a specific App Password (do not use your main Gmail password):

Go to Google Account > Security.

Enable 2-Step Verification (if not already on).

Search for "App Passwords".

Create a new one named "Email Agent".

Copy the 16-character code.

🏃‍♂️ Running the App
Navigate to the project directory in your terminal.

Run the Streamlit server:
streamlit run app.py


The app will open in your browser at http://localhost:8501.

Enter your Name, Email, and the App Password to log in.

📈 Usage Guide
Dashboard: View your inbox with color-coded tags for "Job Applications," "Security Alerts," etc.

Auto-Triage: Click the "✨ Auto-Triage" button to have the AI sort and categorize your emails.

Chat: Use the "Chat with Inbox" feature to ask questions like "Did I get any interview updates today?"

OCR: Enable "Enable Image Scan" in the sidebar settings to read text inside attachments.

Podcast: Click "▶️ Play Audio Summary" in the sidebar for a voice briefing of your top emails.

🤝 Contributing
Feel free to fork this repository and submit pull requests. Suggestions for new features (e.g., calendar integration, different local models) are welcome!

📜 License
MIT License
