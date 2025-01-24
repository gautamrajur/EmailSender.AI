import os
import json
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from groq import Groq

# Load Gmail API credentials
gmail_creds_json = os.getenv("GMAIL_API_CREDENTIALS")
gmail_creds = json.loads(gmail_creds_json)
creds = Credentials.from_authorized_user_info(gmail_creds)

# Initialize Gmail API
service = build('gmail', 'v1', credentials=creds)

def fetch_unread_emails():
    """Fetch unread emails from Gmail inbox."""
    query = "is:unread category:primary" 
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query, maxResults=10).execute()
    messages = results.get('messages', [])
    return messages

def generate_ai_response(email_content):
    """Generate AI response using Groq LLaMA API."""
    groq_api_key = os.getenv("GROQ_LLAMMA_API_KEY")

    # Initialize the Groq client
    client = Groq(api_key=groq_api_key)

    prompt = (
    f"Craft a professional and respectful reply to the following email based on its context, ensuring clarity and conciseness:\n\n"
    f"{email_content}\n\n"
    f"### Guidelines for the Reply:\n"
    f"1. **Acknowledge** the sender politely.\n"
    f"2. Provide a **clear, concise, and relevant** response.\n"
    f"3. Maintain a **professional and courteous** tone.\n"
    f"4. Use a logical structure for better readability.\n"
    f"5. Ensure the reply is **precise and error-free.**\n"
    f"6. Conclude with a **polite closing**, signing off as 'Best regards, Gautam Raju'."
    f"5. If you don't understand the context. Just reply to them that I will get back to them soon.**\n"
    )


    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_completion_tokens=300,
            top_p=1,
            stop=None,
            stream=False
        )
        
        ai_response = chat_completion.choices[0].message.content.strip()
        return ai_response

    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I could not generate a response at the moment."

def send_email(reply_to, subject, body):
    """Send an email reply using Gmail API."""
    message = f"From: me\nTo: {reply_to}\nSubject: {subject}\n\n{body}"
    encoded_message = base64.urlsafe_b64encode(message.encode('utf-8')).decode('utf-8')

    send_message = {'raw': encoded_message}
    service.users().messages().send(userId="me", body=send_message).execute()

def main():
    unread_emails = fetch_unread_emails()
    for msg in unread_emails:
        msg_id = msg['id']
        email_data = service.users().messages().get(userId='me', id=msg_id).execute()
        email_content = email_data['snippet']

        ai_response = generate_ai_response(email_content)

        sender_email = next(header['value'] for header in email_data['payload']['headers'] if header['name'] == 'From')
        subject = "Re: " + next(header['value'] for header in email_data['payload']['headers'] if header['name'] == 'Subject')

        send_email(sender_email, subject, ai_response)

        # Mark email as read
        service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

if __name__ == "__main__":
    main()
