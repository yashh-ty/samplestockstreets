IN ORDER TO SEND THE COPY OF REPORTS TO THE MAIL THEN FIRSTLY WE HAVE TO 

WHILE EMAIL ACTIVATION FOLLOW THE BELOW STEPS


In order to send the pdf to the mail cannot use your normal Gmail password.You must generate an App Password:
Step-1-Go to Google Account → Security
Step-2-Enable 2-Step Verification
Step-3-Then create App Password (Mail)


USING THE MAIL AND APP_PASSWORD SECURELY IN test.py file without exposing our mail_details
Go to my system and fetch the value stored under the name EMAIL and APP_PASSWORD

Step-1 Close all of the terminals and code editors
Step-1-Press Windows + S
Step-2-Search: Environment Variables
Step-3-Click: Edit the system environment variables
Step-4-Click New
  Name: EMAIL
  Value: your email
Step-4 -Again click New
  Name: APP_PASSWORD
  Value: your app password
Step-5 Now your enviornment variables are set

##Checking whether the email and password are correct or not by using system variables
import os
sender_email = os.getenv("EMAIL")
app_password = os.getenv("APP_PASSWORD")

if not sender_email or not app_password:
    raise ValueError("Environment variables not set properly")
else:
    print('DONE SUCESSFULLY')


