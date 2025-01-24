
![logo](logo.png)

# 📧 EmailSender.AI

An AI-powered email responder that automatically replies to unread emails in your Gmail inbox using **Groq's LLaMA API**. The system runs periodically via **GitHub Actions**, ensuring prompt and intelligent responses to incoming emails.

## 🚀 Features

- **Automated Email Replies**: Reads unread emails and responds intelligently.
- **Groq LLaMA API Integration**: Uses LLaMA models to generate professional responses.
- **Manual Trigger Support**: Run the responder manually when needed.
- **Secure API Key Management**: Uses GitHub Secrets to store credentials securely.

---

## 🏰️ Project Structure

```
📂 EmailSender.AI
│-- 📄 requirements.txt       # Required dependencies
│-- 📄 .github/workflows/      # GitHub Actions workflow configuration
│-- 📄 README.md               # Project documentation
│-- 📂 src/
    │-- 📄 email_responder.py   # Main script to fetch, generate response, and send emails
```

---

## ⚙️ Installation and Setup

Follow these steps to set up and run the project locally or using GitHub Actions.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/EmailSender.AI.git
cd EmailSender.AI
```

### 2. Install Dependencies

Make sure you have Python installed, then install required packages:

```bash
pip install -r requirements.txt
```

### 3. Set Up Gmail API Credentials

- Generate Gmail API credentials from the [Google Cloud Console](https://console.cloud.google.com/)
- Save the credentials JSON and set it as an environment variable:

```bash
export GMAIL_API_CREDENTIALS='{"client_id":"YOUR_CLIENT_ID","client_secret":"YOUR_CLIENT_SECRET",...}'
```

### 4. Get Your Groq LLaMA API Key

- Sign up at [Groq](https://groq.com) and obtain an API key.
- Store it securely in your environment:

```bash
export GROQ_LLAMMA_API_KEY="your_groq_api_key_here"
```

---

## 🔍 How It Works

Below is an overview of how the email responder operates:

1. The script fetches unread emails from Gmail.
2. The email content is sent to Groq's LLaMA API to generate a reply.
3. The AI-generated response is sent back to the sender.
4. The email is marked as read to avoid duplicate responses.

---

## 🛡️ Security Considerations

- Always store sensitive credentials in **GitHub Secrets** and avoid hardcoding them.
- Set appropriate permissions for your Gmail API to limit access.
- Monitor the GitHub Actions logs for any failures or unauthorized activity.

---

## 🐛 Troubleshooting

If you encounter any issues, try the following:

- Ensure your Gmail API credentials are correct and have proper permissions.
- Verify your Groq API key is valid and active.
- Check GitHub Actions logs for errors in execution.
- Run the script locally to confirm everything works fine.

---

## 🛠️ Future Improvements

- Add support for multiple email accounts.
- Enhance AI-generated responses with custom prompts.
- Integrate with other email services (Outlook, Yahoo, etc.).
- Build a web interface to monitor email responses.

---

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests to improve the project.

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Submit a pull request.

