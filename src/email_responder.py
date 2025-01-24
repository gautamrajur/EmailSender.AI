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
    f"Please craft a professional and respectful reply to the following email, ensuring that the response is tailored to the context and tone of the message. The reply should be clear, concise, and appropriate for the given situation:\n\n"
    f"{email_content}\n\n"
    f"### Guidelines for Crafting the Reply:\n"
    f"1. Begin by **addressing the sender by their name or title**, and acknowledge their message in a polite and sincere manner. Acknowledge any important details or requests made in the email.\n"
    f"2. Respond to the main content of the email, providing a **relevant and actionable answer** that directly addresses the questions or concerns raised.\n"
    f"3. Maintain a **professional, courteous, and empathetic tone** that is suited to the specific context, ensuring the response aligns with the tone of the original email.\n"
    f"4. Use a **logical and clear structure** for the reply, with short paragraphs, bullet points, or numbered lists if necessary to improve readability and comprehension.\n"
    f"5. Ensure the reply is **precise, helpful, and without unnecessary information**, focusing on providing the most relevant details that will be useful to the sender.\n"
    f"6. If the email mentions a request for further information or actions, make sure to **address those next steps**, including any timelines or follow-up actions required.\n"
    f"7. End the message with a **polite closing**, ensuring the message is warm and inviting for further conversation if necessary. Sign off with ‘Best regards, Gautam Raju.’\n"
    f"8. If the context or request in the email is unclear or ambiguous, **respond politely** by acknowledging that you need a little more time or clarification and assure them that you'll get back to them as soon as possible.\n"
    f"9. **Avoid template language**. Instead of using pre-written phrases or insertions (like ‘Dear [Name]’ or ‘Best regards [Your Name]’), respond as if you are directly speaking to the sender, with natural, fluid language.\n"
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
