from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

import requests

from database.config import settings


class EmailService:
    def send(self, to_email: str, subject: str, html: str) -> bool:
        try:
            provider = settings.email_provider.lower()
            if provider == "resend":
                return self._send_resend(to_email, subject, html)
            if provider == "smtp":
                return self._send_smtp(to_email, subject, html)

            print(f"[email:console] to={to_email} subject={subject}\n{html}\n")
            return True
        except Exception as exc:
            print(f"[email:error] to={to_email} subject={subject} error={exc}")
            return False

    def _send_resend(self, to_email: str, subject: str, html: str) -> bool:
        if not settings.resend_api_key:
            return False

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.email_from,
                "to": [to_email],
                "subject": subject,
                "html": html,
            },
            timeout=20,
        )
        return response.status_code < 300

    def _send_smtp(self, to_email: str, subject: str, html: str) -> bool:
        if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
            return False

        msg = MIMEText(html, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = settings.email_from
        msg["To"] = to_email

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.email_from, [to_email], msg.as_string())
        return True


email_service = EmailService()


def send_welcome_email(to_email: str):
    subject = "Bienvenido a TrendML"
    html = """
    <h2>Bienvenido a TrendML</h2>
    <p>Tu cuenta ya está activa. Empieza detectando productos tendencia hoy.</p>
    <p><a href=\"{frontend}/dashboard\">Ir al dashboard</a></p>
    """.format(frontend=settings.frontend_url)
    return email_service.send(to_email, subject, html)


def send_checkout_started_email(to_email: str, plan: str, checkout_url: str):
    subject = f"Completa tu suscripción {plan.upper()} en TrendML"
    html = """
    <h2>Tu plan {plan} está casi listo</h2>
    <p>Haz clic para completar el pago y desbloquear funciones premium:</p>
    <p><a href=\"{checkout_url}\">Completar pago</a></p>
    """.format(plan=plan.upper(), checkout_url=checkout_url)
    return email_service.send(to_email, subject, html)


def send_payment_approved_email(to_email: str, plan: str):
    subject = "Pago aprobado: tu plan TrendML está activo"
    html = """
    <h2>Pago aprobado</h2>
    <p>Tu plan <strong>{plan}</strong> ya está activo.</p>
    <p><a href=\"{frontend}/dashboard\">Ir al dashboard</a></p>
    """.format(plan=plan.upper(), frontend=settings.frontend_url)
    return email_service.send(to_email, subject, html)


def send_checkout_reminder_email(to_email: str, plan: str, checkout_url: str):
    subject = f"Recordatorio: activa tu plan {plan.upper()} en TrendML"
    html = """
    <h2>Tu acceso premium sigue pendiente</h2>
    <p>Completa tu pago y desbloquea alertas, predicciones y análisis avanzados.</p>
    <p><a href=\"{checkout_url}\">Finalizar suscripción ahora</a></p>
    """.format(checkout_url=checkout_url)
    return email_service.send(to_email, subject, html)
