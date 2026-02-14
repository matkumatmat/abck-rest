from __future__ import annotations

import re
from pathlib import Path

from components.logger.LoggerFactory import loggerFactory


class emailTemplateEngine:

    def __init__(self, templates_dir: str) -> None:
        self._templates_dir = Path(templates_dir)
        self._cache: dict[str, str] = {}
        self._logger = loggerFactory.create("email_template")

    def _load_template(self, template_name: str) -> str:
        if template_name in self._cache:
            return self._cache[template_name]

        template_path = self._templates_dir / f"{template_name}.mjml"
        if not template_path.exists():
            html_path = self._templates_dir / f"{template_name}.html"
            if html_path.exists():
                template_path = html_path
            else:
                raise FileNotFoundError(f"Template not found: {template_name}")

        content = template_path.read_text()

        if template_path.suffix == ".mjml":
            content = self._compile_mjml(content)

        self._cache[template_name] = content
        return content

    def _compile_mjml(self, mjml_content: str) -> str:
        try:
            from mjml import mjml_to_html
            result = mjml_to_html(mjml_content)
            return result.html
        except ImportError:
            self._logger.warning("mjml_not_installed", detail="Using raw MJML content")
            return mjml_content
        except Exception as e:
            self._logger.error("mjml_compile_error", error=str(e))
            return mjml_content

    def render(self, template_name: str, **data) -> str:
        template = self._load_template(template_name)

        for key, value in data.items():
            pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
            template = re.sub(pattern, str(value), template)

        return template

    def extract_subject(self, template_name: str) -> str | None:
        template_path = self._templates_dir / f"{template_name}.mjml"
        if not template_path.exists():
            template_path = self._templates_dir / f"{template_name}.html"
            if not template_path.exists():
                return None

        content = template_path.read_text()
        match = re.search(r"<!--\s*subject:\s*(.+?)\s*-->", content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def list_templates(self) -> list[str]:
        templates: list[str] = []
        if self._templates_dir.exists():
            for path in self._templates_dir.iterdir():
                if path.suffix in (".mjml", ".html"):
                    templates.append(path.stem)
        return sorted(templates)

    def clear_cache(self) -> None:
        self._cache.clear()
