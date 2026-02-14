from __future__ import annotations

import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

import aiosmtplib

from components.email.EmailTemplateEngine import emailTemplateEngine
from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from components.config.ComponentSettings import componentSettings


class emailService:

    def __init__(
        self,
        config: componentSettings,
        template_engine: emailTemplateEngine | None = None,
    ) -> None:
        self._config = config
        self._template_engine = template_engine or emailTemplateEngine(config.email_templates_dir)
        self._logger = loggerFactory.create("email_service")

    async def _send_email(self, to: str, subject: str, html_body: str) -> bool:
        message = MIMEMultipart("alternative")
        message["From"] = f"{self._config.smtp_from_name} <{self._config.smtp_from_email or self._config.smtp_user}>"
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html"))

        try:
            await aiosmtplib.send(
                message,
                hostname=self._config.smtp_host,
                port=self._config.smtp_port,
                username=self._config.smtp_user,
                password=self._config.smtp_password,
                start_tls=self._config.smtp_use_tls,
            )
            self._logger.info("email_sent", to=to, subject=subject)
            return True
        except Exception as e:
            self._logger.error("email_send_error", to=to, subject=subject, error=str(e))
            return False

    async def send(
        self,
        to: str,
        template_name: str,
        subject: str | None = None,
        **data,
    ) -> bool:
        try:
            html_body = self._template_engine.render(template_name, **data)
            email_subject = subject or self._template_engine.extract_subject(template_name) or template_name
        except FileNotFoundError as e:
            self._logger.error("template_not_found", template=template_name, error=str(e))
            return False
        except Exception as e:
            self._logger.error("template_render_error", template=template_name, error=str(e))
            return False

        for attempt in range(1, self._config.email_retry_attempts + 1):
            success = await self._send_email(to, email_subject, html_body)
            if success:
                return True

            if attempt < self._config.email_retry_attempts:
                delay = 2 ** (attempt - 1)
                self._logger.warning(
                    "email_retry",
                    to=to,
                    attempt=attempt,
                    max_attempts=self._config.email_retry_attempts,
                    delay=delay,
                )
                await asyncio.sleep(delay)

        return False

    async def send_raw(self, to: str, subject: str, html_body: str) -> bool:
        for attempt in range(1, self._config.email_retry_attempts + 1):
            success = await self._send_email(to, subject, html_body)
            if success:
                return True

            if attempt < self._config.email_retry_attempts:
                delay = 2 ** (attempt - 1)
                await asyncio.sleep(delay)

        return False

    async def send_bulk(self, recipients: list[dict]) -> dict:
        results = {"success": 0, "failed": 0, "errors": []}

        for recipient in recipients:
            to = recipient.get("to")
            template = recipient.get("template")
            subject = recipient.get("subject")
            data = recipient.get("data", {})

            if not to or not template:
                results["failed"] += 1
                results["errors"].append({"to": to, "error": "Missing to or template"})
                continue

            success = await self.send(to, template, subject, **data)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"to": to, "error": "Send failed"})

        return results
