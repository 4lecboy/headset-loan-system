import os
import pymysql
import smtplib
import schedule
import threading
import time
import csv
from PIL import Image, ImageDraw
from pystray import Icon, MenuItem as item, Menu
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

# ========== Database ==========

def connect_to_mysql():
    conn = pymysql.connect(
        host='10.42.10.38',
        user='root',
        password='',
        database='headsets',
        autocommit=True
    )
    return conn

def fetch_loan_records():
    conn = connect_to_mysql()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DateIssued, AshimaID, Name, RoomNumber, AssetTag, IssuedBy, Status 
        FROM sentrecords 
        WHERE Status = 'Issued' 
        ORDER BY ID DESC
    """)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records

def get_image_from_db(image_id):
    conn = None
    cursor = None
    try:
        conn = connect_to_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT image_data FROM images WHERE id = %s", (image_id,))
        result = cursor.fetchone()
        return (result[0], None) if result else (None, None)
    except pymysql.MySQLError as e:
        print(f"[MySQL Error] Failed to retrieve image: {e}")
        return (None, str(e))
    except Exception as e:
        print(f"[Error] Unexpected error occurred: {e}")
        return (None, str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()



# ========== Email ==========

def create_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['DateIssued', 'AshimaID', 'Name', 'RoomNumber', 'AssetTag', 'IssuedBy', 'Status'])
        for row in data:
            writer.writerow(row)

def generate_html_body(records):
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

def send_email_with_attachment(sender_email, receiver_email, cc_emails, subject, body, attachment_filename, logo_data, smtp_server, smtp_port, login, password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Cc'] = ', '.join(cc_emails)
    msg['Subject'] = subject

    logo = MIMEImage(logo_data)
    logo.add_header('Content-ID', '<logo>')
    msg.attach(logo)

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
    msg.attach(MIMEText(html_content, 'html'))

    with open(attachment_filename, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
        msg.attach(part)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(login, password)
        server.sendmail(sender_email, [receiver_email] + cc_emails, msg.as_string())

    try:
        os.remove(attachment_filename)
    except FileNotFoundError:
        pass


# ========== Job ==========

def job():
    image_id = 1
    logo_data, _ = get_image_from_db(image_id)
    if not logo_data:
        print("Logo not found. Email not sent.")
        return

    print("Generating report and sending email...")
    all_items = fetch_loan_records()
    html_body = generate_html_body(all_items)
    create_csv(all_items, 'table_data.csv')

    send_email_with_attachment(
        sender_email='[eastwestcallcenter.com]',
        receiver_email='ewsupport@eastwestbpo.com',
        cc_emails=['pdd@eastwestbpo.com','operationsmanagers@eastwestbpo.com'],
        subject='Urgent: List of Unreturned Headsets',
        body=html_body,
        attachment_filename='table_data.csv',
        logo_data=logo_data,
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        login='jcarlos@eastwestbpo.com',
        password='ehls jqsp yruk wvsr'
    )

# ========== Scheduler ==========

exit_event = threading.Event()

def run_schedule():
    schedule.every().day.at("16:00").do(job)
    while not exit_event.is_set():
        schedule.run_pending()
        time.sleep(2)

# ========== Tray Icon ==========

def create_image():
    from PIL import Image
    return Image.open("hed.ico")


def on_send_now(icon, item):
    threading.Thread(target=job).start()

def on_exit(icon, item):
    exit_event.set()
    icon.stop()

def main():
    threading.Thread(target=run_schedule, daemon=True).start()

    menu = Menu(
        item("Send Now", on_send_now),
        item("Exit", on_exit)
    )

    icon = Icon("Headset Monitor", create_image(), "Headset Tracker", menu)
    icon.run()

if __name__ == '__main__':
    main()
