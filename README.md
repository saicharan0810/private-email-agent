# 🔒 Private AI Email Agent

A Local-First, Multi-Modal Email Assistant powered by Llama 3.2.

This application connects securely to your Gmail inbox to analyze, summarize, and manage emails without sending your private data to the cloud. It runs entirely on your local machine using Ollama for inference, Tesseract for OCR, and gTTS for audio briefings.

---

## 🚀 Key Features

* **🛡️ Privacy First**: Uses local LLMs (Llama 3.2) so email content never leaves your device
* **🧠 Auto-Triage Agent**: Automatically classifies emails (Job Apps, Security, Spam) using a Hybrid Rule+AI engine
* **🎙️ Morning Podcast Mode**: Converts your top priority emails into a spoken audio briefing to listen to while commuting
* **👁️ Visual Intelligence (OCR)**: Detects text inside images (screenshots, receipts) using Tesseract OCR
* **✍️ Smart Drafts**: Generates context-aware replies and saves them directly to your Gmail Drafts folder
* **📊 Analytics Dashboard**: Visualizes sender activity and inbox composition
* **⚡️ Fast & Efficient**: Optimized for local execution, providing quick responses without cloud latency

---

## 🛠️ Tech Stack

* **Frontend**: Streamlit (Python)
* **AI Inference**: Ollama (Llama 3.2)
* **Computer Vision**: Tesseract OCR / PyTesseract
* **Audio**: gTTS (Google Text-to-Speech)
* **Email Protocol**: IMAP/SMTP for secure email handling

---

## ⚙️ Installation & Setup

### 1. Prerequisites

* **Python 3.8+**
* **Ollama**: [Download here](https://ollama.ai/) and run:
  ```bash
  ollama pull llama3.2
  ```
* **Tesseract OCR**:
  * **Mac**: 
    ```bash
    brew install tesseract
    ```
  * **Windows**: [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki)
  * **Linux**:
    ```bash
    sudo apt-get install tesseract-ocr
    ```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Get a Google App Password

To connect securely, you must generate a specific App Password (do not use your main Gmail password):

1. Go to [Google Account > Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Search for **"App Passwords"**
4. Create a new one named **"Email Agent"**
5. Copy the **16-character code**

> ⚠️ **Important**: Keep this password secure and never commit it to version control.

---

## 🏃‍♂️ Running the App

1. Navigate to the project directory in your terminal
2. Run the Streamlit server:
   ```bash
   streamlit run app.py
   ```
3. The app will open in your browser at `http://localhost:8501`
4. Enter your **Name**, **Email**, and the **App Password** to log in

---

## 📈 Usage Guide

### Dashboard
View your inbox with color-coded tags for "Job Applications," "Security Alerts," etc.

### Auto-Triage
Click the **"✨ Auto-Triage"** button to have the AI sort and categorize your emails automatically.

### Chat
Use the **"Chat with Inbox"** feature to ask questions like:
- "Did I get any interview updates today?"
- "Show me all emails from recruiters this week"
- "Summarize my unread security alerts"

### OCR
Enable **"Enable Image Scan"** in the sidebar settings to read text inside email attachments (screenshots, receipts, documents).

### Podcast Mode
Click **"▶️ Play Audio Summary"** in the sidebar for a voice briefing of your top priority emails - perfect for your morning commute!

---

## 🔒 Privacy & Security

* **Local-Only Processing**: All email analysis happens on your machine using local LLMs
* **No Cloud API Calls**: Your email content never gets sent to external servers
* **Secure Connection**: Uses IMAP/SMTP with App Passwords for Gmail authentication
* **No Data Storage**: Emails are processed in memory and not persistently stored

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

* Fork this repository
* Create a feature branch (`git checkout -b feature/amazing-feature`)
* Commit your changes (`git commit -m 'Add amazing feature'`)
* Push to the branch (`git push origin feature/amazing-feature`)
* Open a Pull Request

### Feature Ideas
- Calendar integration for meeting scheduling
- Support for other email providers (Outlook, ProtonMail)
- Different local LLM models (Mistral, Phi-3)
- Email templates and automation rules
- Multi-language support

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

* [Ollama](https://ollama.ai/) - For making local LLM inference accessible
* [Streamlit](https://streamlit.io/) - For the amazing UI framework
* [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - For open-source OCR
* [gTTS](https://github.com/pndurette/gTTS) - For text-to-speech conversion

---

## 📧 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

## ⚠️ Disclaimer

This tool is for personal use only. Always ensure you comply with your email provider's terms of service and applicable data privacy regulations when using automated email tools.

---

**Built with ❤️ for privacy-conscious email management**
