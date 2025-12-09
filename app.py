import imaplib
import email
import ollama
import pandas as pd
import plotly.express as px
import streamlit as st
import pytesseract
import io
import math
from PIL import Image
from email.header import decode_header
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
from email.mime.text import MIMEText
from gtts import gTTS
import time

# --- HELPER FUNCTIONS ---

def _is_lxml_available():
    try:
        import lxml
        return True
    except ImportError:
        return False

def clean_email_body(raw_html):
    parser = 'lxml' if _is_lxml_available() else 'html.parser'
    soup = BeautifulSoup(raw_html, parser)
    return soup.get_text(separator=' ', strip=True)

def safe_decode(byte_data, encoding="utf-8"):
    try:
        if not encoding: encoding = "utf-8"
        return byte_data.decode(encoding)
    except Exception:
        return byte_data.decode("utf-8", errors="replace")

def extract_text_from_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception:
        return ""

def text_to_audio(text):
    try:
        tts = gTTS(text=text, lang='en')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception:
        return None

def save_draft_to_gmail(username, password, to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = f"Re: {subject}"
        msg['From'] = username
        msg['To'] = to_email
        
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        
        date_now = imaplib.Time2Internaldate(time.localtime())
        
        try:
            mail.append('[Gmail]/Drafts', None, date_now, msg.as_bytes())
            mail.logout()
            return True, "Saved to [Gmail]/Drafts"
        except:
            try:
                mail.append('Drafts', None, date_now, msg.as_bytes())
                mail.logout()
                return True, "Saved to Drafts"
            except Exception as e:
                return False, str(e)

    except Exception as e:
        return False, str(e)

# --- CORE LOGIC ---

def fetch_emails(username, password, limit=10, folder="ALL", enable_ocr=False, page=1):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")
        
        status, search_data = mail.search(None, folder)
        
        if not search_data[0]:
            return [], 0 

        mail_ids = search_data[0].split()
        total_emails = len(mail_ids)
        
        end_idx = total_emails - ((page - 1) * limit)
        start_idx = max(0, end_idx - limit)
        
        if end_idx <= 0:
            return [], total_emails 
            
        batch_ids = mail_ids[start_idx:end_idx]
        batch_ids = list(reversed(batch_ids)) 
        
        messages = []
        
        for num in batch_ids:
            try:
                _, msg_data = mail.fetch(num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject_header = decode_header(msg["Subject"])[0]
                        subject, encoding = subject_header
                        if isinstance(subject, bytes):
                            subject = safe_decode(subject, encoding)
                        
                        sender = msg.get("From")
                        sender_email = sender
                        if "<" in sender:
                            sender_email = sender.split("<")[1].replace(">", "")
                        
                        raw_date = msg.get("Date")
                        try:
                            dt_obj = parsedate_to_datetime(raw_date)
                            local_dt = dt_obj.astimezone()
                            date = local_dt.strftime("%b %d, %I:%M %p")
                        except Exception:
                            date = raw_date 

                        body = "No text content found."
                        has_image = False
                        
                        if msg.is_multipart():
                            full_text = ""
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                
                                if "attachment" not in content_disposition:
                                    if content_type == "text/plain":
                                        payload = part.get_payload(decode=True)
                                        full_text += safe_decode(payload) + "\n"
                                    elif content_type == "text/html":
                                        payload = part.get_payload(decode=True)
                                        html_body = safe_decode(payload)
                                        full_text += clean_email_body(html_body) + "\n"
                                
                                if enable_ocr and "image" in content_type:
                                    img_data = part.get_payload(decode=True)
                                    if len(img_data) > 5000:
                                        ocr_text = extract_text_from_image(img_data)
                                        if ocr_text:
                                            full_text += f"\n\n[🔍 IMAGE TEXT DETECTED]:\n{ocr_text}\n"
                                            has_image = True
                            
                            body = full_text
                        else:
                            content_type = msg.get_content_type()
                            payload = msg.get_payload(decode=True)
                            if content_type == "text/html":
                                html_body = safe_decode(payload)
                                body = clean_email_body(html_body)
                            else:
                                body = safe_decode(payload)
                        
                        messages.append({
                            "id": num.decode(),
                            "subject": subject,
                            "sender": sender,
                            "sender_email": sender_email,
                            "date": date,
                            "body": body,
                            "category": None,
                            "has_image": has_image
                        })
            except Exception:
                continue 
        
        mail.close()
        mail.logout()
        return messages, total_emails 
        
    except Exception as e:
        return str(e)

def rule_based_classify(sender, subject, body):
    sender = sender.lower()
    subject = subject.lower()
    body = body.lower()[:500]
    
    sec_keywords = ["security alert", "verification code", "2fa", "unauthorized access", "password reset"]
    if any(k in sender or k in subject or k in body for k in sec_keywords):
        return "Security Alert"
    
    job_keywords = ["application", "interview", "offer", "reject", "candidate", "linkedin", "workday", "greenhouse", "lever", "recruiter", "admission", "grad school", "university", "phd", "master"]
    if any(k in sender or k in subject for k in job_keywords):
        return "Job Application"
        
    news_keywords = ["newsletter", "digest", "weekly", "edition", "unsubscribe", "medium", "substack"]
    if any(k in sender for k in news_keywords):
        return "Newsletter"
    
    promo_keywords = ["sale", "discount", "% off", "deal", "limited time"]
    if any(k in subject for k in promo_keywords):
        return "Promotion/Spam"

    return None 

def classify_email(sender, subject, body):
    category = rule_based_classify(sender, subject, body)
    if category:
        return category
    
    try:
        categories = "['Job Application', 'Security Alert', 'Personal', 'Newsletter', 'Promotion/Spam']"
        prompt = f"Classify this email into exactly one of these categories: {categories}.\nSender: {sender}\nSubject: {subject}\nBody: {body[:1000]}\nReply ONLY with the category name."
        response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
        content = response['message']['content'].strip()
        for cat in ['Job Application', 'Security Alert', 'Personal', 'Newsletter', 'Promotion/Spam']:
            if cat in content:
                return cat
        return "Personal"
    except Exception:
        return "Personal"

def summarize_with_ollama(text):
    try:
        response = ollama.chat(model='llama3.2', messages=[
            {'role': 'user', 'content': f"Summarize this email in 2 sentences. Capture the main action item:\n\n{text[:4000]}"},
        ])
        return response['message']['content']
    except Exception as e:
        return f"Ollama Error: {e}"

def generate_reply(email_text, user_notes):
    try:
        # Retrieve real name from Session State
        user_name = st.session_state.get("user_full_name", "Sai")
        
        prompt = f"""
        You are an email assistant for {user_name}.
        
        Incoming Email:
        {email_text[:1000]}
        
        My Draft Notes:
        {user_notes}
        
        Task: Write a professional reply based on my notes.
        
        STRICT RULES:
        1. Output ONLY the email body.
        2. Do NOT write "Here is a draft" or "Subject:".
        3. Do NOT include placeholders like "[Your Name]".
        4. Sign off specifically as "{user_name}".
        """
        
        response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"

def ask_inbox(emails, query):
    try:
        context_blob = ""
        for mail in emails:
            context_blob += f"--- START EMAIL ---\nFrom: {mail['sender']}\nSubject: {mail['subject']}\nContent: {mail['body'][:500]}...\n--- END EMAIL ---\n\n"
        
        prompt = f"Context:\n{context_blob}\n\nUser Question: {query}\n\nAnswer based on the emails."
        response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"

def get_category_color(category):
    if not category: return "#808080"
    if "Security" in category: return "#ff4b4b" 
    if "Job" in category: return "#00c853"      
    if "Personal" in category: return "#29b6f6" 
    if "Newsletter" in category: return "#ffa726" 
    return "#808080"

# --- UI SETUP ---
st.set_page_config(page_title="Local Email AI", layout="wide")

st.markdown("""
    <style>
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .stButton>button { width: 100%; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🔒 Private Email Summarizer + OCR")

# Session State Init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "creds" not in st.session_state:
    st.session_state.creds = {"user": "", "pass": ""}
if "user_full_name" not in st.session_state:
    st.session_state.user_full_name = "Sai" # Default fallback
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "total_emails" not in st.session_state:
    st.session_state.total_emails = 0

# --- SIDEBAR ---
with st.sidebar:
    if not st.session_state.logged_in:
        st.header("🔐 Login")
        
        # --- NEW: NAME INPUT FIELD ---
        user_full_name = st.text_input("Your Name (for signatures)", placeholder="e.g. Sai Charan")
        
        email_user = st.text_input("Email Address")
        email_pass = st.text_input("App Password", type="password", help="Use your 16-character Google App Password")
        
        st.write("") 
        if st.button("Connect Account", type="primary", use_container_width=True):
            if email_user and email_pass:
                with st.spinner("Verifying credentials..."):
                    st.session_state.current_page = 1
                    result = fetch_emails(email_user, email_pass, limit=10, folder="ALL", page=1)
                    if isinstance(result, str):
                        st.error(f"Login Failed: {result}")
                    else:
                        emails, total = result
                        st.session_state.creds = {"user": email_user, "pass": email_pass}
                        # SAVE NAME
                        st.session_state.user_full_name = user_full_name if user_full_name else email_user.split('@')[0]
                        
                        st.session_state.logged_in = True
                        st.session_state.emails = emails
                        st.session_state.total_emails = total
                        st.rerun()
    else:
        st.subheader("👋 Welcome Back")
        # Display Real Name
        st.markdown(f"**{st.session_state.user_full_name}**")
        st.caption(f"{st.session_state.creds['user']}")
        
        st.divider()
        
        # 1. PODCAST
        st.markdown("##### 🎙️ Daily Briefing")
        if st.button("▶️ Play Audio Summary", type="primary", use_container_width=True):
             if "emails" in st.session_state and st.session_state.emails:
                 with st.spinner("Generating Audio Briefing..."):
                     top_emails = st.session_state.emails[:5]
                     # Personalized Greeting
                     podcast_script = f"Good morning, {st.session_state.user_full_name}. Here is your daily briefing. "
                     for mail in top_emails:
                         sender_clean = mail['sender'].split('<')[0].strip().replace('"', '')
                         podcast_script += f"From {sender_clean}: {mail['subject']}. "
                         short_sum = summarize_with_ollama(mail['body'])
                         podcast_script += f"{short_sum}. Next email. "
                     podcast_script += "That concludes your briefing."
                     audio_file = text_to_audio(podcast_script)
                     if audio_file:
                         st.audio(audio_file, format='audio/mp3', start_time=0)
                         st.toast("Podcast Ready!", icon="🎙️")
        
        st.divider()
        
        # 2. SETTINGS
        with st.expander("⚙️ View Settings", expanded=False):
            filter_type = st.radio("Inbox Filter", ["All Emails", "Unread Only"])
            limit_per_page = st.select_slider("Emails per Page", options=[5, 10, 15, 20], value=10)
            enable_ocr = st.toggle("Enable Image Scan (OCR)")
        
        # 3. NAVIGATION LOGIC
        st.markdown("##### 🧭 Navigation")
        
        total_pages = math.ceil(st.session_state.total_emails / limit_per_page)
        if total_pages < 1: total_pages = 1
        
        col_prev, col_pg, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if st.session_state.current_page > 1:
                if st.button("⬅️", help="Newer Emails"):
                    st.session_state.current_page -= 1
                    st.rerun()
            else:
                st.write("") 
        
        with col_pg:
            st.button(f"Page {st.session_state.current_page}/{total_pages}", disabled=True, use_container_width=True)
        
        with col_next:
            if st.session_state.current_page < total_pages:
                if st.button("➡️", help="Older Emails"):
                    st.session_state.current_page += 1
                    st.rerun()
            else:
                st.write("") 

        search_criteria = 'UNSEEN' if filter_type == "Unread Only" else 'ALL'
        if st.button("🔄 Refresh Inbox", use_container_width=True):
            with st.spinner("Fetching latest emails..."):
                result = fetch_emails(
                    st.session_state.creds['user'], 
                    st.session_state.creds['pass'], 
                    limit=limit_per_page, 
                    folder=search_criteria, 
                    enable_ocr=enable_ocr, 
                    page=st.session_state.current_page
                )
                if isinstance(result, str):
                    st.error(result)
                else:
                    emails, total = result
                    st.session_state.emails = emails
                    st.session_state.total_emails = total

        st.divider()
        col_logout, col_reset = st.columns(2)
        with col_logout:
            if st.button("Logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        with col_reset:
            if st.button("Reset App", use_container_width=True):
                st.session_state.clear()
                st.rerun()

# --- MAIN APP ---
if st.session_state.logged_in:
    
    col_a, col_b = st.columns([3, 1])
    with col_a:
        with st.expander("🤖 Chat with your Inbox", expanded=False):
            user_query = st.text_input("Ask a question:", placeholder="e.g., 'What does the screenshot in the last email say?'")
            if user_query and "emails" in st.session_state:
                with st.spinner("Analyzing..."):
                    answer = ask_inbox(st.session_state.emails, user_query)
                    st.info(answer)
    with col_b:
        if "emails" in st.session_state and st.session_state.emails:
            if st.button("✨ Auto-Triage"):
                progress_text = "Classifying emails..."
                my_bar = st.progress(0, text=progress_text)
                total = len(st.session_state.emails)
                for i, mail in enumerate(st.session_state.emails):
                    category = classify_email(mail['sender'], mail['subject'], mail['body'])
                    st.session_state.emails[i]['category'] = category
                    my_bar.progress((i + 1) / total, text=f"Classifying {i+1}/{total}")
                my_bar.empty()
                st.rerun()
    st.divider()
    
    tab1, tab2 = st.tabs(["📧 Inbox List", "📊 Dashboard Analytics"])
    
    with tab1:
        if "emails" in st.session_state and st.session_state.emails:
            for mail in st.session_state.emails:
                if 'category' not in mail: mail['category'] = None
                if 'has_image' not in mail: mail['has_image'] = False
            
            priority_map = {"Security Alert": 0, "Job Application": 1, "Personal": 2, "Newsletter": 3, "Promotion/Spam": 4}
            sorted_emails = sorted(st.session_state.emails, key=lambda x: priority_map.get(x.get('category'), 5))

            st.caption(f"Page {st.session_state.current_page} | Showing {len(sorted_emails)} emails")
            
            for mail in sorted_emails:
                with st.container():
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        badges = []
                        cat = mail.get('category')
                        if cat:
                            color = get_category_color(cat)
                            badges.append(f"<span style='background-color:{color}; color:white; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600; margin-right: 5px;'>{cat}</span>")
                        if mail.get('has_image'):
                            badges.append(f"<span style='background-color:#673ab7; color:white; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: 600;'>📷 Image Scan</span>")
                        if badges:
                            st.markdown("".join(badges), unsafe_allow_html=True)
                        
                        st.markdown(f"##### {mail['subject']}")
                        st.caption(f"From: {mail['sender']} | {mail['date']}")
                        
                        with st.expander("View Content"):
                            st.text(mail['body'])
                    
                    with col2:
                        if st.button(f"Summarize", key=f"sum_{mail['id']}"):
                            with st.spinner("Thinking..."):
                                summary = summarize_with_ollama(mail['body'])
                                st.info(summary)
                                audio = text_to_audio(summary)
                                if audio:
                                    st.audio(audio, format='audio/mp3')
                        
                        with st.expander("Draft Reply"):
                            user_notes = st.text_area("Notes", key=f"note_{mail['id']}")
                            if st.button("Generate Reply", key=f"rep_{mail['id']}"):
                                st.session_state[f"generated_reply_{mail['id']}"] = generate_reply(mail['body'], user_notes)
                            
                            if f"generated_reply_{mail['id']}" in st.session_state:
                                reply_text = st.session_state[f"generated_reply_{mail['id']}"]
                                st.success(reply_text)
                                
                                if st.button("💾 Save to Gmail Drafts", key=f"save_{mail['id']}"):
                                    with st.spinner("Uploading to Gmail..."):
                                        success, msg_result = save_draft_to_gmail(
                                            st.session_state.creds['user'],
                                            st.session_state.creds['pass'],
                                            mail.get('sender_email', ''),
                                            mail['subject'],
                                            reply_text
                                        )
                                        if success:
                                            st.toast(f"Success: {msg_result}", icon="✅")
                                        else:
                                            st.error(f"Failed: {msg_result}")

                st.divider()
        elif "emails" in st.session_state:
            st.info("No emails found.")

    with tab2:
        if "emails" in st.session_state and st.session_state.emails:
            df = pd.DataFrame(st.session_state.emails)
            if "category" in df.columns:
                st.subheader("Inbox Composition")
                df['category'] = df['category'].fillna("Uncategorized")
                counts = df['category'].value_counts().reset_index()
                counts.columns = ['Category', 'Count']
                fig_pie = px.pie(counts, values='Count', names='Category', title='Email Categories', color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_pie, use_container_width=True)
                
                st.subheader("Top Senders")
                sender_counts = df['sender'].value_counts().head(5).reset_index()
                sender_counts.columns = ['Sender', 'Count']
                fig_bar = px.bar(sender_counts, x='Count', y='Sender', orientation='h', title="Most Active Senders", color='Count', color_continuous_scale='Bluered')
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Run 'Auto-Triage' first to see Category Analytics!")
        else:
            st.info("Fetch emails to see analytics.")