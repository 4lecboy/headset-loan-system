"""
Email utilities for sending notifications
"""
import os
import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from datetime import datetime
from utils.env_loader import get_env

from config.database import execute_query
from models.image import get_image_from_db

def create_csv_from_data(data, filename):
    """
    Create a CSV file from data
    
    Args:
        data (list): List of data rows
        filename (str): Output filename
        
    Returns:
        str: Path to created CSV file
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['DateIssued', 'AshimaID', 'Name', 'RoomNumber', 'AssetTag', 'IssuedBy', 'Status'])
        for row in data:
            writer.writerow(row)
    return filename

def generate_html_body(records):
    """
    Generate HTML table from records
    
    Args:
        records (list): List of record data
        
    Returns:
        str: HTML table string
    """
    rows = ""
    for record in records:
        rows += "<tr>" + "".join(f"<td>{field}</td>" for field in record) + "</tr>"
    return f"""
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>DateIssued</th><th>AshimaID</th><th>Name</th>
            <th>RoomNumber</th><th>AssetTag</th><th>IssuedBy</th><th>Status</th>
        </tr>
        {rows}
    </table>
    """

def send_email_with_attachment(sender_email, receiver_email, cc_emails, subject, body, 
                              attachment_filename, logo_data, smtp_server, smtp_port, 
                              login, password):
    """
    Send an email with an attachment and embedded logo
    
    Args:
        sender_email (str): Sender's email address
        receiver_email (str): Recipient's email address
        cc_emails (list): List of CC recipients
        subject (str): Email subject
        body (str): Email body (HTML)
        attachment_filename (str): Path to attachment file
        logo_data (bytes): Logo image data
        smtp_server (str): SMTP server address
        smtp_port (int): SMTP server port
        login (str): SMTP login username
        password (str): SMTP login password
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Cc'] = ', '.join(cc_emails)
        msg['Subject'] = subject

        # Read the logo image file and attach it to the email
        logo = MIMEImage(logo_data)
        logo.add_header('Content-ID', '<logo>')
        msg.attach(logo)

        # Generate HTML content with logo
        html_content = f"""
        <html>
        <body>
            <img src="cid:logo" alt="Logo" style="width:100px;height:100px;"><br>
            <p>Good Day Team,</p>
            <p>I hope this message finds you well.</p>
            <p>As part of our ongoing efforts to maintain inventory accuracy, our records indicate that there are several headsets that have not been returned.</p>
            <p>We request your support in reminding your team members to return their headsets immediately after their shifts.</p>
            <p>Please find below the list of unreturned headsets along with the names of agents whom they were issued:</p>
            {body}
            <p>Thank you for your prompt attention to this matter.</p>
            <p><i>Note: This is an auto-generated email, no need to reply.</i></p>
        </body>
        </html>
        """

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        # Attach CSV file
        with open(attachment_filename, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_filename)}')
            msg.attach(part)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(login, password)
            server.sendmail(sender_email, [receiver_email] + cc_emails, msg.as_string())

        # Remove the CSV file after sending the email
        try:
            os.remove(attachment_filename)
        except FileNotFoundError:
            pass
            
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def fetch_loan_records():
    """
    Fetch active loan records from database
    
    Returns:
        list: List of records
    """
    query = """
        SELECT DateIssued, AshimaID, Name, RoomNumber, AssetTag, IssuedBy, Status 
        FROM sentrecords 
        WHERE Status = 'Issued' 
        ORDER BY ID DESC
    """
    return execute_query(query)

def send_scheduled_email():
    """
    Send a scheduled email with unreturned headsets report
    This is called by the scheduler
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("Generating report and sending email...")
    
    # Get unreturned headsets data
    unreturned_headsets = fetch_loan_records()
    
    if not unreturned_headsets:
        print("No unreturned headsets to report")
        return False
    
    # Format the data for HTML display
    html_body = generate_html_body(unreturned_headsets)
    
    # Create CSV file
    csv_filename = create_csv_from_data(unreturned_headsets, 'unreturned_headsets.csv')
    
    # Get logo image
    image_id = 1  # Logo image ID
    logo_data, _ = get_image_from_db(image_id)
    
    if not logo_data:
        print("Logo image not found")
        return False
    
    # Send email
    return send_email_with_attachment(
        sender_email=get_env('EMAIL_SENDER', 'noreply@eastwestcallcenter.com'),
        receiver_email=get_env('EMAIL_RECIPIENT', 'ewsupport@eastwestbpo.com'),
        cc_emails=get_env('EMAIL_CC', 'pdd@eastwestbpo.com').split(','),
        subject='Urgent: List of Unreturned Headsets',
        body=html_body,
        attachment_filename=csv_filename,
        logo_data=logo_data,
        smtp_server=get_env('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
        smtp_port=int(get_env('EMAIL_SMTP_PORT', '587')),
        login=get_env('EMAIL_LOGIN', ''),
        password=get_env('EMAIL_PASSWORD', '')
    )