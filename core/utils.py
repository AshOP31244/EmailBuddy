from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.core.exceptions import ValidationError


def send_email_with_user_smtp(user, subject, body, to_emails, cc_list=None, bcc_list=None, is_html=False):
    """
    Send email using user's SMTP settings
    Returns: (success: bool, error_message: str or None)
    """
    try:
        # Check if user has email settings
        if not hasattr(user, 'email_settings'):
            return False, "Please configure your email settings first"
        
        settings = user.email_settings
        
        # Get decrypted password
        try:
            password = settings.get_password()
        except Exception as e:
            return False, f"Failed to decrypt email password: {str(e)}"
        
        # Create custom SMTP connection
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_email,
            password=password,
            use_tls=settings.smtp_use_tls,
            fail_silently=False,
        )
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=body if not is_html else 'This email requires HTML support.',
            from_email=settings.smtp_email,
            to=to_emails if isinstance(to_emails, list) else [to_emails],
            cc=cc_list if cc_list else None,
            bcc=bcc_list if bcc_list else None,
            connection=connection,
        )
        
        # Attach HTML version if needed
        if is_html:
            email.attach_alternative(body, "text/html")
        
        # Send
        email.send(fail_silently=False)
        return True, None
        
    except Exception as e:
        return False, str(e)


def test_smtp_connection(smtp_host, smtp_port, smtp_email, smtp_password, use_tls=True):
    """
    Test SMTP connection with given credentials
    Returns: (success: bool, error_message: str or None)
    """
    try:
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=smtp_host,
            port=smtp_port,
            username=smtp_email,
            password=smtp_password,
            use_tls=use_tls,
            fail_silently=False,
        )
        connection.open()
        connection.close()
        return True, None
    except Exception as e:
        return False, str(e)