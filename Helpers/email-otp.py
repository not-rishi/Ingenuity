import base64
import requests
import time
import random
import threading
import database

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_access_token(refresh_token):
    data = {
        'client_id': database.CLIENT_ID,
        'client_secret': database.CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(database.TOKEN_URI, data=data)
    response_data = response.json()

    if 'access_token' in response_data:
        access_token = response_data['access_token']
        return access_token
    else:
        print("Access token fail")
        raise Exception("Failed to obtain access token")

def send_email(access_token,toemail,otp):
    creds = Credentials(token=access_token)
    service = build('gmail', 'v1', credentials=creds)


    message = MIMEMultipart()
    message['to'] = toemail
    message['subject'] = 'OTP for BMSCE Discord Server'
    html_content = f"""
    <html>
    <body>
        <h2>OTP Verification</h2>
        <p>Your One Time Password (OTP) is <strong>{otp}</strong></p>
        <p>Thank you verifying in our server!</p>
    </body>
    </html>
    """

    message.attach(MIMEText(html_content, 'html'))
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()


    try:
        send_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f"Email sent successfully! Message ID: {send_message['id']}")
    except Exception as error:
        print(f"An error occurred: {error}")



def initiate_mail(toemail,otp):
    try:
        if database.COMMAND_ACCEPTED_REFRESH_TOKEN == None:
            access_token = get_access_token(database.REFRESH_TOKEN)
        else:
            access_token = get_access_token(database.COMMAND_ACCEPTED_REFRESH_TOKEN)
        send_email(access_token,toemail,otp)
        return True
    except:
        return False
    


"""Mail Module ends OTP Module starts"""

otp_store = {}


def generate_otp():
    otp = random.randint(1000, 9999)  
    return otp



def add_otp(user_id):
    otp = generate_otp()
    expiration_time = time.time() + 600 

    otp_store[user_id] = {'otp': otp, 'expiration': expiration_time}
    threading.Thread(target=delete_otp, args=(user_id, expiration_time)).start()
    return otp



def delete_otp(user_id, expiration_time):
    time.sleep(600)
    
    if time.time() >= expiration_time:
        if user_id in otp_store:
            del otp_store[user_id]
            print(f"OTP for user {user_id} has expired and was deleted.")



def validate_otp(user_id, entered_otp):
    entered_otp = int(entered_otp)
    if user_id not in otp_store:
        return "OTP has expired or does not exist."
    
    otp_data = otp_store[user_id]
    if time.time() > otp_data['expiration']:
        del otp_store[user_id]  
        return "OTP has expired."
    
    if entered_otp == otp_data['otp']:
        return "OTP has been validated and the role has been assigned."
    else:
        return "Invalid OTP."
    
def check_access_token():
    if initiate_mail("test@gmail.com","1234") == True:
        return True
    else:
        return False        
