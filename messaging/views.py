import pandas as pd
from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib import messages
from .models import Message
from .forms import UploadFileForm, MessageForm


# HTML Email Template with Styling
EMAIL_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
            text-align: center;
        }
        .email-container {
            max-width: 600px;
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            margin: auto;
        }
        h2 {
            color: #2b2b2b;
        }
        p {
            font-size: 16px;
            color: #555;
            line-height: 1.5;
        }
        .cta-button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-size: 18px;
            display: inline-block;
            margin-top: 10px;
        }
        .cta-button:hover {
            background-color: #0056b3;
        }
        .footer {
            font-size: 12px;
            color: #888;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <h2>🚀 Let's Grow Your Business, {company_name}!</h2>
        <p>Hi {company_name} Team,</p>
        <p>I'm <b>Adarsh B S</b>, the founder of <b>Digital Product</b>. We specialize in <b>creating stunning websites, SEO optimization, and social media automation</b> to help businesses like yours attract more customers and boost sales.</p>
        <p>Would you be open to a quick chat to explore how we can help you scale?</p>
        <a href="https://www.adarshbs.com/#contact" class="cta-button">Schedule a Free Consultation</a>
        <p>Looking forward to working together!</p>
        <p>Best regards,</p>
        <p><b>Adarsh B S</b><br>
        📧 <a href="mailto:digitalproductkerala@gmail.com">digitalproductkerala@gmail.com</a><br>
        📞 <a href="tel:+919400355185">+91 9400355185</a><br>
        🌐 <a href="https://digitalproduct.adarshbs.com/">https://digitalproduct.adarshbs.com/</a><br>
        📸 <a href="https://www.instagram.com/digital_product_kerala/">Instagram</a></p>
        <p class="footer">If you are not interested, you can ignore this email. No further emails will be sent.</p>
    </div>
</body>
</html>
"""


def send_custom_email(subject, recipient_email, company_name):
    """Helper function to send an email using HTML formatting."""
    try:
        # Format the HTML email template with company details
        html_message = EMAIL_HTML_TEMPLATE.format(company_name=company_name)

        # Send the email
        email = EmailMultiAlternatives(
            subject=subject,
            body="This is an HTML email. Please enable HTML in your email client.",
            from_email="digitalproductkerala@gmail.com",
            to=[recipient_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

def send_email(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            company_name = message.company_name

            # Replace {company_name} in the email template
            email_html = EMAIL_HTML_TEMPLATE.replace("{company_name}", company_name)

            try:
                subject = f"Grow Your Business, {company_name}!"
                from_email = "digitalproductkerala@gmail.com"
                recipient_list = [message.recipient_email]
                text_content = strip_tags(email_html)  # Convert HTML to plain text

                email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
                email.attach_alternative(email_html, "text/html")  # Attach HTML version
                email.send()

                message.status = "Sent"
            except Exception as e:
                message.status = "Failed"
                print(f"Error sending email: {e}")

            message.save()
            return redirect("success")
    else:
        form = MessageForm()

    return render(request, "send_email.html", {"form": form})



def upload_excel(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            try:
                print("working here 1")
                df = pd.read_excel(file)
                df.rename(columns={"company_name": "company_name"}, inplace=True)  # Fix column name
                
                for _, row in df.iterrows():
                    recipient_email = str(row.get("gmail", "")).strip()
                    company_name = str(row.get("company_name", "")).strip()
                    
                    if recipient_email and company_name and "@gmail.com" in recipient_email:
                        message = Message.objects.create(
                            recipient_email=recipient_email,
                            company_name=company_name,
                            status="Pending",
                        )
                        
                        email_html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
            text-align: center;
        }}
        .email-container {{
            max-width: 600px;
            background: #ffffff;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
        }}
        h2 {{
            color: #2b2b2b;
            font-size: 32px;
            margin-bottom: 20px;
            animation: fadeIn 2s ease-in-out;
        }}
        p {{
            font-size: 16px;
            color: #555;
            line-height: 1.6;
            margin: 10px 0;
        }}
        .cta-button {{
            background-color: #007bff;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            font-size: 18px;
            display: inline-block;
            margin: 20px 0;
            transition: background-color 0.3s ease, transform 0.3s ease;
        }}
        .cta-button:hover {{
            background-color: #0056b3;
            transform: scale(1.05);
        }}
        .footer {{
            font-size: 12px;
            color: #888;
            margin-top: 30px;
        }}
        .highlight {{
            color: #007bff;
            font-weight: bold;
        }}
        .social-links a {{
            color: #007bff;
            text-decoration: none;
            margin: 0 10px;
            font-size: 14px;
        }}
        .social-links a:hover {{
            text-decoration: underline;
        }}
        .logo {{
            width: 120px;
            margin-bottom: 20px;
        }}
        .service-list {{
            text-align: left;
            margin: 20px auto;
            max-width: 400px;
        }}
        .service-list li {{
            margin: 10px 0;
            font-size: 16px;
            color: #555;
        }}
        .inquiry-section {{
            background-color: #f4f4f4;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }}
        .inquiry-section p {{
            font-size: 18px;
            color: #2b2b2b;
            margin-bottom: 15px;
        }}
        .inquiry-button {{
            background-color: #28a745;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-size: 16px;
            display: inline-block;
            transition: background-color 0.3s ease, transform 0.3s ease;
        }}
        .inquiry-button:hover {{
            background-color: #218838;
            transform: scale(1.05);
        }}
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Logo -->
        <img src="https://digitalproduct.adarshbs.com/logo.png" alt="Digital Product Logo" class="logo">

        <!-- Heading -->
        <h2 class="animated-text">🚀 Let's Grow Your Business, <span class="highlight">{company_name}</span>!</h2>

        <!-- Introduction -->
        <p>Hi <span class="highlight">{company_name}</span> Team,</p>
        <p>I'm <b>Adarsh B S</b>, the founder of <b>Digital Product</b>. We specialize in:</p>
        <ul class="service-list">
            <li>🌐 <b>Stunning Website Design</b></li>
            <li>🔍 <b>SEO Optimization</b></li>
            <li>🤖 <b>Social Media Automation</b></li>
        </ul>
        <p>Our goal is to help businesses like yours attract more customers and boost sales.</p>

        <!-- Call to Action -->
        <p>Would you be open to a quick chat to explore how we can help you scale?</p>
        <a href="https://www.adarshbs.com/#contact" class="cta-button">Schedule a Free Consultation</a>

        <!-- Inquiry Section -->
        <div class="inquiry-section">
            <p>Have questions or need more information? We're here to help!</p>
            <a href="mailto:digitalproductkerala@gmail.com" class="inquiry-button">Contact Us Now</a>
        </div>

        <!-- Closing -->
        <p>Looking forward to working together!</p>
        <p>Best regards,</p>
        <p><b>Adarsh B S</b></p>

        <!-- Contact Information -->
        <div class="social-links">
            📧 <a href="mailto:digitalproductkerala@gmail.com">digitalproductkerala@gmail.com</a><br>
            📞 <a href="tel:+919400355185">+91 9400355185</a><br>
            🌐 <a href="https://digitalproduct.adarshbs.com/">https://digitalproduct.adarshbs.com/</a><br>
            📸 <a href="https://www.instagram.com/digital_product_kerala/">Instagram</a>
        </div>

        <!-- Footer -->
        <p class="footer">If you are not interested, you can ignore this email. No further emails will be sent.</p>
    </div>
</body>
</html>
"""
                        
                        try:
                            email = EmailMultiAlternatives(
                                subject=f"Boost Your Business with Digital Product!",
                                body=f"Hello {company_name}, check out our services at www.adarshbs.com",
                                from_email="digitalproductkerala@gmail.com",
                                to=[recipient_email],
                            )
                            email.attach_alternative(email_html_template, "text/html")
                            email.send()
                            
                            message.status = "Sent"
                        except Exception as e:
                            message.status = "Failed"
                            print(f"Error sending email: {e}")
                        
                        message.save()
                
                messages.success(request, "Emails sent successfully!")
            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
            
            return redirect("upload_excel")
    else:
        form = UploadFileForm()

    return render(request, "upload_excel.html", {"form": form})


def home(request):
    return render(request, "home.html")


def success(request):
    return render(request, "success.html")
