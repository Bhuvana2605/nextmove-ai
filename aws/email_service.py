import os
from botocore.exceptions import ClientError
import boto3
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
        self.client = boto3.client("ses", region_name=self.region)

    def _build_html(self, plan):
        greeting = "Hello Bhuvana 👋"
        mission_score = getattr(plan, "mission_score", 0)
        summary = getattr(plan, "summary", "") or ""
        schedule = getattr(plan, "schedule", []) or []

        recommendations_html = ""
        for index, item in enumerate(schedule[:3], start=1):
            title = getattr(item, "title", "") or ""
            source = getattr(item, "source", "") or ""
            action = getattr(item, "action", "") or ""
            reason = getattr(item, "reason", "") or ""
            why_selected = getattr(item, "why_selected", "") or ""
            estimated_minutes = getattr(item, "estimated_minutes", "") or ""
            confidence = getattr(item, "confidence", "") or ""
            url = getattr(item, "url", "") or ""
            priority = getattr(item, "priority", "") or ""

            recommendations_html += f"""
            <tr>
                <td style="padding:0 0 16px 0;">
                    <div style="border:1px solid #e5e7eb; border-radius:12px; padding:16px; background-color:#f9fafb;">
                        <p style="margin:0 0 8px 0; font-size:14px; font-weight:bold; color:#2563eb;">Recommendation {index}</p>
                        <p style="margin:0 0 8px 0;"><strong>Priority:</strong> {priority}</p>
                        <p style="margin:0 0 8px 0;"><strong>Title:</strong> {title}</p>
                        <p style="margin:0 0 8px 0;"><strong>Source:</strong> {source}</p>
                        <p style="margin:0 0 8px 0;"><strong>Action:</strong> {action}</p>
                        <p style="margin:0 0 8px 0;"><strong>Reason:</strong> {reason}</p>
                        <p style="margin:0 0 8px 0;"><strong>Why Selected:</strong> {why_selected}</p>
                        <p style="margin:0 0 8px 0;"><strong>Estimated Minutes:</strong> {estimated_minutes}</p>
                        <p style="margin:0 0 12px 0;"><strong>Confidence:</strong> {confidence}</p>
                        <a href="{url}" style="display:inline-block; background-color:#2563eb; color:#ffffff; text-decoration:none; padding:10px 16px; border-radius:8px; font-weight:bold;">View Opportunity →</a>
                    </div>
                </td>
            </tr>
            """

        if not recommendations_html:
            recommendations_html = """
            <tr>
                <td style="padding:0 0 16px 0;">
                    <div style="border:1px solid #e5e7eb; border-radius:12px; padding:16px; background-color:#f9fafb;">No recommendations available.</div>
                </td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NextMove AI Daily Brief</title>
        </head>
        <body style="margin:0; padding:0; background-color:#f3f4f6; font-family:Arial, sans-serif; color:#111827;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#f3f4f6; padding:24px 0;">
                <tr>
                    <td align="center" style="padding:0 12px;">
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                            <tr>
                                <td style="background-color:#2563eb; padding:24px; color:#ffffff;">
                                    <h1 style="margin:0; font-size:24px;">🌅 Your NextMove AI Daily Brief</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding:24px;">
                                    <p style="margin:0 0 12px; font-size:16px;">{greeting}</p>
                                    <p style="margin:0 0 12px;"><strong>Mission Score:</strong> {mission_score}</p>
                                    <p style="margin:0 0 20px;"><strong>Summary:</strong> {summary}</p>
                                    <h2 style="margin:0 0 12px; font-size:18px;">Today's Top 3 Recommendations</h2>
                                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-collapse:separate; border-spacing:0 12px;">
                                        {recommendations_html}
                                    </table>
                                    <div style="margin-top:24px; padding-top:16px; border-top:1px solid #e5e7eb; font-size:12px; color:#6b7280; text-align:center; line-height:1.6;">
                                        ------------------------------------<br>
                                        Generated automatically by NextMove AI<br>
                                        Powered by<br>
                                        Amazon Bedrock<br>
                                        Amazon DynamoDB<br>
                                        Amazon SES<br>
                                        AWS Lambda<br>
                                        Amazon EventBridge<br>
                                        ------------------------------------
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def send_daily_plan(self, plan):
        if not self.sender_email or not self.recipient_email:
            return False

        try:
            self.client.send_email(
                Source=self.sender_email,
                Destination={"ToAddresses": [self.recipient_email]},
                Message={
                    "Subject": {"Data": "🌅 Your NextMove AI Daily Brief"},
                    "Body": {
                        "Html": {"Data": self._build_html(plan)},
                        "Text": {"Data": "Your NextMove AI Daily Brief"},
                    },
                },
            )
            return True
        except ClientError as e:
            print(f"SES Error: {e}")
            return False
