import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re
from utils.logger import logger
import os
from datetime import datetime, timedelta
from system_config import EMAIL_SENDER, EMAIL_PASSWORD, HR_EMAILS

class EmailReporter:
    def __init__(self):
        self.sender = EMAIL_SENDER
        self.password = EMAIL_PASSWORD
        self.recipients = HR_EMAILS
        if not self.sender:
            raise ValueError("EMAIL_SENDER not configured.")
        if not self.password:
            raise ValueError("EMAIL_PASSWORD not configured.")
        if all(not email.strip() for email in self.recipients):
            ValueError(
                "No email recipients configured."
            )
    
    def create_email_content(self, metrics: dict, predictions: list[dict]) -> str:
        """Create HTML email content"""
        report_time = datetime.now()

        html_content = f"""
        <html>
        <head>
            <style>
            body{{font-family: Arial, Helvetica, sans-serif; background:#f0dfdf; color:#222; margin:0; padding:40px;}}

            .container{{max-width:1200px; margin:auto;}}

            .header{{text-align:center; margin-bottom:40px;}}

            .title{{font-size:46px; font-weight:800; color:#1f2937; margin-bottom:7px;}}

            .date{{font-size:16px; color:#555; font-weight:500;}}

            h2{{color:#1f2937; margin-top:40px; margin-bottom:12px;}}

            .summary-title{{font-size:34px; font-weight:bold; margin-bottom:7px;}}

            .metrics-title{{font-size:28px; font-weight:bold;}}

            .summary-text{{font-size:14px; line-height:1.7; color:#444; margin-bottom:25px;}}

            /* Metric Cards */

            .metrics{{display:grid; grid-template-columns:repeat(3,260px); justify-content:center; gap:25px; margin-top:30px; margin-bottom:50px;}}

            .metric-card{{background:#e7fdd2; border-radius:35px; padding:25px; text-align:center; box-shadow:0px 3px 10px rgba(0,0,0,.15);}}

            .metric-title{{font-size:20px; font-weight:600; color:#444; margin-bottom:18px;}}

            .metric-value{{font-size:36px; font-weight:bold; color:#000;}}

            .positive{{color:#179b2b;}}

            .negative{{color:#d60000;}}

            .prediction-table{{width:100%; border-collapse:collapse; margin-top:20px; background:white;}}

            .prediction-table th{{background:#1f2937; color:white; padding:12px;}}

            .prediction-table td{{padding:10px; border-bottom:1px solid #ddd;}}

            .strong-buy{{color:#0cd70c; font-weight:bold;}}

            .buy{{color:#009900; font-weight:bold;}}

            .hold{{color:#ff9800; font-weight:bold;}}

            .sell{{color:#d60000; font-weight:bold;}}

            .strong-sell{{color:#ff0000; font-weight:bold;}}
            </style>
        </head>
        <body>

        <div class="container">

        <div class="header">

        <div class="title">
        📊 Weekly Financial Report
        </div>

        <div class="date">
        {report_time.strftime('%Y-%m-%d %H:%M')}
        </div>

        </div>

        <h2 class="summary-title">
        📈 Executive Summary
        </h2>

        <p class="summary-text">
        This report contains automated analysis of financial data for the week ending
        {report_time.strftime('%Y-%m-%d')}.
        </p>

        <h2 class="metrics-title">
        📊 Key Metrics
        </h2>

        <div class="metrics">
        """
        
        # Add metrics
        for key, value in metrics.items():

            value_class = "metric-value"

            # Make only Average Daily Return dynamic
            if key == "average_daily_return":

                value_str = str(value)

                if value_str.startswith("-"):
                    value_class += " negative"
                else:
                    value_class += " positive"

            html_content += f"""
            <div class="metric-card">

                <div class="metric-title">
                    {key.replace('_', ' ').title()}
                </div>

                <div class="{value_class}">
                    {value}
                </div>

            </div>
            """
        
        html_content += """
            </div>
            
            <h2>🔮 Predictions & Signals</h2>
            <table class="prediction-table">
                <tr>
                    <th>Ticker</th>
                    <th>Current Price</th>
                    <th>Predicted Price</th>
                    <th>Expected Return</th>
                    <th>Signal</th>
                    <th>Confidence</th>
                </tr>
        """
        
        # Add predictions
        for pred in predictions:
            signal_class = pred['signal'].lower().replace(' ', '-')
            html_content += f"""
                <tr>
                    <td>{pred['ticker']}</td>
                    <td>${pred['current_price']:.2f}</td>
                    <td>${pred['predicted_price']:.2f}</td>
                    <td>{pred['expected_return_pct']:.2f}%</td>
                    <td class="{signal_class}">{pred['signal']}</td>
                    <td>{pred['confidence']}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>📋 Attachments</h2>
            <p>This email includes the following attachments:</p>
            <ul>
                <li>Complete dataset (CSV)</li>
                <li>Analysis spreadsheet (Excel)</li>
                <li>Interactive dashboard (HTML)</li>
            </ul>
            
            <hr>
            <p><em>This is an automated report generated by the Financial Analytics System.</em></p>
            <p><em>For any questions, please contact the data analytics team.</em></p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def send_email(
        self,
        subject: str,
        html_content: str,
        attachments: list[str],
        recipient_email: str = None
    ):
        """Send email with attachments"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender
            # Use custom recipient if supplied; otherwise use configured recipients
            if recipient_email:

                email_pattern = r"^[^@]+@[^@]+\.[^@]+$"

                if not re.match(email_pattern, recipient_email):

                    logger.error(
                        "Invalid recipient email: %s",
                        recipient_email
                    )

                    return False

                recipients = [recipient_email]

            else:

                recipients = self.recipients

            msg["To"] = ", ".join(recipients)
            msg['Subject'] = subject
            
            # Add HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Add attachments
            for attachment in attachments:
                if not os.path.exists(attachment):
                    logger.warning(
                        "Attachment not found: %s",
                        attachment
                    )
                    continue

                logger.info(
                    "Attaching file: %s",
                    attachment
                )

                logger.info(
                    "File size: %s KB",
                    f"{os.path.getsize(attachment)/1024:.2f}"
                )

                with open(attachment, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())

                    encoders.encode_base64(part)

                    filename = os.path.basename(attachment)

                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )

                    msg.attach(part)

            
            # Send email
            logger.info(
                "Connecting to Gmail SMTP server..."
            )

            with smtplib.SMTP(
                'smtp.gmail.com',
                587,
                timeout=30
            ) as server:

                server.starttls()

                logger.info(
                    "TLS encryption established."
                )

                logger.info(
                    "Logging into Gmail..."
                )

                server.login(
                    self.sender,
                    self.password
                )

                logger.info(
                    "Sending email..."
                )

                server.sendmail(
                    self.sender,
                    recipients,
                    msg.as_string()
                )
            
            logger.info(
                "Email sent successfully to %s recipient(s).",
                len(recipients)
            )
            logger.info(
                "Weekly report completed successfully."
            )
            return True
            
        except Exception as e:

            logger.error(
                "Email sending failed: %s: %s",
                type(e).__name__,
                e
            )
            return False
    
    def generate_weekly_report(
        self,
        recipient_email=None
    ):
        """Generate reports and send email"""
        report_time = datetime.now()

        logger.info(
            "Starting weekly report generation..."
        )

        from database_manager import DatabaseHandler
        from prediction_engine import FinancialPredictor
        from report_generator import ReportGenerator

        db = DatabaseHandler()
        predictor = FinancialPredictor()
        rep_gen = ReportGenerator()

        # Get latest data
        latest_prices = db.get_latest_prices()

        if latest_prices.empty:
            logger.info("No data available for report")
            return False

        # Calculate metrics
        total_tickers = len(
            latest_prices['Ticker'].unique()
        )

        avg_return = (
            latest_prices['Daily_Return'].mean() * 100
        )

        total_volume = (
            latest_prices['Volume'].sum()
        )

        one_year_ago = report_time - timedelta(days=365)

        data_points = 0

        for ticker in rep_gen.get_available_tickers():
            df = rep_gen.db.get_stock_data(
                ticker,
                start_date=one_year_ago
            )
            data_points += len(df)

        metrics = {
            'total_tickers_analyzed':
                total_tickers,

            'average_daily_return':
                f"{avg_return:.2f}%",

            'total_volume_traded':
                f"{total_volume:,.0f}",

            'report_date':
                report_time.strftime('%Y-%m-%d'),

            'data_points_analyzed':
                data_points
        }

        # Generate predictions
        predictions = []

        tickers = latest_prices['Ticker'].unique()

        for ticker in tickers[:5]:

            signal = predictor.generate_trading_signals(
                ticker
            )

            if signal:
                predictions.append(signal)

        logger.info(
            "Generated %d predictions.",
            len(predictions)
        )

        
        logger.debug(
            "Predictions: %s",
            predictions
        )

        # Create email content
        subject = (
            f"Weekly Financial Report - "
            f"{report_time.strftime('%Y-%m-%d')}"
        )

        html_content = self.create_email_content(
            metrics,
            predictions
        )

        # Generate attachments
        csv_file = db.export_csv_report()

        excel_file = db.export_excel_report()

        html_report = (
            rep_gen.generate_full_report()
        )

        attachments = [
            csv_file,
            excel_file,
            html_report
        ]

        for file in attachments:

            logger.info(
                "Generated attachment: %s",
                file
            )

        logger.info(
            "Report generation completed. "
            "Preparing to send email."
        )

        # Send email
        return self.send_email(
            subject,
            html_content,
            attachments,
            recipient_email
        )