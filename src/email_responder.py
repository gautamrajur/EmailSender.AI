import os
import json
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from groq import Groq
import re

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
    f"Craft a natural, professional, and respectful reply to the following email, based on its content and tone. Ensure the response is specific to the email, and avoid using any generic or templated phrases. Focus on providing a personalized reply that shows attention to detail and an understanding of the sender's message:\n\n"
    f"{email_content}\n\n"
    f"### Guidelines for the Reply:\n"
    f"1. **Acknowledge** the sender's message with sincerity, addressing any key points they have made or questions they have raised.\n"
    f"2. Provide a **clear, direct, and relevant response** to the sender’s inquiry or topic. Do not use placeholders or filler language. The reply should be specific and tailored to the details of the email.\n"
    f"3. Maintain a **professional, courteous, and empathetic tone** that is appropriate for the context of the conversation. Adapt the tone based on the nature of the email—whether formal or informal, urgent or casual.\n"
    f"4. **Avoid template language**. Instead of using pre-written phrases or insertions (like ‘Dear [Name]’ or ‘Best regards [Your Name]’), respond as if you are directly speaking to the sender, with natural, fluid language.\n"
    f"5. Ensure your response is well-structured, but do not resort to clichés or formulaic endings. The response should be easy to read and follow logically, with the focus entirely on the sender’s needs and context.\n"
    f"6. If the email requests a follow-up or action, make sure to **acknowledge next steps** clearly, without using vague terms like ‘We’ll follow up soon.’ Be specific about what actions you’ll take or when you’ll get back to them.\n"
    f"7. **Close the reply politely** without relying on standard phrases. The closing should match the overall tone and context, not following a preset template. Acknowledge any final details or summarize the response appropriately."
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


def is_auto_reply_or_no_reply(email_address):
    no_reply_patterns = [r"no-reply", r"donotreply", r"noreply"]
    return any(re.search(pattern, email_address, re.IGNORECASE) for pattern in no_reply_patterns)

def main():
    unread_emails = fetch_unread_emails()
    for msg in unread_emails:
        msg_id = msg['id']
        email_data = service.users().messages().get(userId='me', id=msg_id).execute()
        email_content = email_data['snippet']

        ai_response = generate_ai_response(email_content)

        sender_email = next(header['value'] for header in email_data['payload']['headers'] if header['name'] == 'From')
        subject = "Re: " + next(header['value'] for header in email_data['payload']['headers'] if header['name'] == 'Subject')

        # Check if the sender's email is an auto-reply or no-reply address
        if is_auto_reply_or_no_reply(sender_email):
            print(f"Skipping reply to no-reply or auto-reply email: {sender_email}")
        else:
            send_email(sender_email, subject, ai_response)

            # Mark email as read after replying
            service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

if __name__ == "__main__":
    main()
