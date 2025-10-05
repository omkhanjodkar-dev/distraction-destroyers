# Team Name:
**Coffee Overflow**

---

# Team Members:
- Om Khanjodkar  
- Pranav Dabeer  
- Siddhant Verma  
- Swara Kulkarni  

---

# Project Name:
**AI-Driven Distraction Detection App for Students**

---

# Project Abstract:
A desktop application that uses Artificial Intelligence to help students stay focused by detecting and blocking distracting websites and applications.  
The app features **AI-based distraction detection**, **Pomodoro mode**, **gamification**, **personalized analytics**, and **background music** to create a focused and customizable study environment.  
It leverages zero-shot learning with the **facebook/bart-large-mnli** model to classify distractions intelligently and uses automation tools to manage apps and system activities seamlessly.

---

# Tech Stack:

### Backend:
- **AI/ML:** `transformers`, `torch`  
- **Automation:** `pyautogui`, `pywinauto`, `keyboard`  
- **Web Scraping:** `requests`, `BeautifulSoup`, `re`, `urllib`  
- **System Utilities:** `os`, `datetime`, `json`  
- **Model Used:** `facebook/bart-large-mnli` *(Zero-shot classification)*  

### Frontend:
- **GUI Building:** `tkinter`  
- **Background Music:** `pygame.mixer`  
- **File Paths/Access:** `os`  

---

# Dataset Used:
No external dataset was used.  
The project utilizes **real-time user activity and text classification** through the pre-trained **facebook/bart-large-mnli** model for distraction detection.

---
