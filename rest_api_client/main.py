from api_client import APIClient
from dotenv import load_dotenv
import os
from pathlib import Path
import json
import argparse
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email(recipient_email, attachment_path, start_date, end_date):
    # Email configuration
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "total4ai@gmail.com"
    smtp_password = "ipezhuihfbqqzule"
    
    # Format dates for email subject (remove hyphens)
    formatted_start_date = start_date.replace('-', '')
    formatted_end_date = end_date.replace('-', '')
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient_email
    msg['Subject'] = f"TGRAM이용현황_{formatted_start_date}-{formatted_end_date}"
    
    # Add body
    body = "Please find attached the dashboard report."
    msg.attach(MIMEText(body, 'plain'))
    
    # Add attachment
    with open(attachment_path, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='xlsx')
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
        msg.attach(attachment)
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='REST API Client for Dashboard Report')
    parser.add_argument('--start-date', type=str, help='Start date for the report (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date for the report (YYYY-MM-DD)')
    parser.add_argument('--download-excel', action='store_true', help='Download report as Excel')
    parser.add_argument('--email', type=str, help='Email address to send the report to')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    base_url = os.getenv('API_BASE_URL', 'https://api.hugraph.com/')
    api_key = os.getenv('API_KEY')
    
    client = APIClient(base_url=base_url, api_key=api_key)
    
    try:
        # Login example (if not using API key)
        if not api_key:
            username = os.getenv('API_USERNAME', 'ibki')
            password = os.getenv('API_PASSWORD', 'ibki1234pw!')
            
            print("Attempting to login...")
            success, message = client.login(username, password)
            print(f"Login: {message}")
            
            if not success:
                print("Authentication failed. Exiting.")
                return
            
            # Display authentication information
            auth_info = client.get_auth_info()
            print("\nAuthentication Information:")
            print(f"Authenticated: {auth_info['is_authenticated']}")
            print(f"Token: {auth_info['auth_token'][:10]}..." if auth_info['auth_token'] else "Token: None")
            if auth_info['user_info']:
                print(f"User: {json.dumps(auth_info['user_info'], indent=2)}")
        
        # Get date parameters from user input if not provided as arguments
        start_date = args.start_date
        end_date = args.end_date
        
        if not start_date:
            start_date = input("Enter start date (YYYY-MM-DD): ")
        
        if not end_date:
            end_date = input("Enter end date (YYYY-MM-DD): ")
        
        # Get email address
        recipient_email = args.email
        if not recipient_email:
            recipient_email = input("Enter email address to send the report to (default: seungho.won@ibki.co.kr): ") or "seungho.won@ibki.co.kr"
        
        # Validate date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD format.")
            return
        
        # Service API call for dashboard report
        print("\n--- Requesting Dashboard Report ---")
        
        # Prepare query parameters
        query_params = {
            'start_date': start_date,
            'end_date': end_date,
            'download_excel': 'true' if args.download_excel else 'false'
        }
        
        print(f"Requesting report for period: {start_date} to {end_date}")
        print(f"Download Excel: {query_params['download_excel']}")
        
        try:
            # Set up headers for the API call
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {client.auth_token}'
            }
            
            # Make the API call with query parameters in the URL
            url = f"{client.base_url}/api/org/dashboard/report"
            print(f"\nSending POST request to: {url}")
            print(f"Query parameters: {query_params}")
            print(f"Headers: {headers}")
            
            response = client.session.post(
                url,
                params=query_params,
                headers=headers,
                data=''
            )
            
            # Remove API response details logging
            if response.status_code == 200:
                if args.download_excel:
                    # Handle Excel download
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/vnd.ms-excel' in content_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
                        # Save the Excel file
                        filename = f"dashboard_report_{start_date}_to_{end_date}.xlsx"
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        
                        # Send email with attachment
                        if send_email(recipient_email, filename, start_date, end_date):
                            print(f"Report has been sent to {recipient_email}")
                        else:
                            print("Failed to send email with the report")
                    else:
                        print("Response is not an Excel file. Content-Type:", content_type)
            else:
                print(f"Error: Request failed with status code {response.status_code}")
        except Exception as e:
            print(f"Error requesting dashboard report: {str(e)}")
        
        # Logout example (if logged in)
        # if not api_key and client.is_authenticated:
        #     print("\n--- Logging Out ---")
        #     print("Attempting to logout...")
        #     success, message = client.logout()
        #     print(f"Logout: {message}")
        #     print("--- Logout Complete ---")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 