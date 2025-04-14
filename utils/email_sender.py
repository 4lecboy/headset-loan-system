"""
Email utilities for sending notifications
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import os
from datetime import datetime
import csv
from models.image import get_image_from_db

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
        <head></head>
        <body>
            <img src="cid:logo" alt="Logo" style="width:100px;height:100px;position:absolute;top:0;left:0;"><br>
            <p>Good Day Team,</p>
            <p>I hope this message finds you well.</p>
            <p>As part of our ongoing efforts to maintain inventory accuracy, Our records indicate that there are several headsets that have not been returned.</p>
            <p>As for PDDs, your assistance in addressing this issue promptly is crucial. Could we kindly request your support in reminding your team members to return their headsets immediately after the[...]
            <p>Your guidance in reinforcing the importance of adhering to company policies will greatly assist in resolving this matter swiftly.</p>
            <p>Please find below the list of unreturned headsets along with the names of agents whom they were issued:</p>
            {body}
            <p>Thank you for your prompt attention to this matter.</p>
            <p>Note: This is an auto-generated email no need to reply.</p>
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
            part.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
            msg.attach(part)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(login, password)
            server.sendmail(sender_email, [receiver_email] + cc_emails, msg.as_string())

        # Remove the CSV file after sending the email
        os.remove(attachment_filename)
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def create_csv_from_data(data, filename):
    """
    Create a CSV file from data
    
    Args:
        data (list): List of data rows
        filename (str): Output filename
        
    Returns:
        str: Path to created CSV file
    """
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header row
        csv_writer.writerow(["Date Issued", "AshimaID", "Issued To", "Campaign", 
                          "Room Number", "Asset Tags", "Issued By", "Status"])
        # Write data rows
        csv_writer.writerows(data)
    return filename

def send_scheduled_email():
    """
    Send a scheduled email with unreturned headsets report
    This is called by the scheduler
    
    Returns:
        bool: True if successful, False otherwise
    """
    from models.loan import LoanModel
    
    loan_model = LoanModel()
    unreturned_headsets = loan_model.get_active_loans()
    
    if not unreturned_headsets:
        print("No unreturned headsets to report")
        return False
    
    # Format the data for HTML display
    html_body = format_tree_data_for_html(unreturned_headsets)
    
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
        sender_email='noreply@eastwestcallcenter.com',
        receiver_email='ewsupport@eastwestbpo.com',
        cc_emails=['pdd@eastwestbpo.com', 'operationsmanagers@eastwestbpo.com'],
        subject='Urgent: List of Unreturned Headsets',
        body=html_body,
        attachment_filename=csv_filename,
        logo_data=logo_data,
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        login='jcarlos@eastwestbpo.com',
        password='ehls jqsp yruk wvsr'  # Consider using environment variables for sensitive data
    )

def format_tree_data_for_html(data):
    """
    Format tree data for HTML email display
    
    Args:
        data: List of record data
        
    Returns:
        str: HTML table string
    """
    # Define header WITHOUT "Campaign"
    header = ["Date Issued", "AshimaID", "Issued To", "Room Number", 
             "Asset Tags", "Issued By", "Status"]

    # Create HTML table
    html_table = '<table border="1" cellspacing="0" cellpadding="5">'
    
    # Add header row
    html_table += '<tr>' + ''.join(f'<th>{col}</th>' for col in header) + '</tr>'
    
    # Add data rows, SKIPPING index 3 (Campaign)
    for row in data:
        html_table += '<tr>'
        for i, item in enumerate(row):
            if i == 3:  # Skip Campaign column
                continue
            html_table += f'<td>{item}</td>'
        html_table += '</tr>'
    
    html_table += '</table>'
    return html_table