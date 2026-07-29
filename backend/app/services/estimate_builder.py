from __future__ import annotations

from typing import Any


class EstimateBuilder:
    """Build a quote payload using either a default format or an agency-defined template."""

    def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        strategy = payload.get("strategy", "lowest_price")
        output_language = payload.get("output_language", "keep_english")
        template = payload.get("agency_template") or self._default_template()
        template_content = template.get("content") if isinstance(template, dict) else None
        template_lines = [line.strip() for line in str(template_content or "").splitlines() if line.strip()]
        template_title = template_lines[0] if template_lines else None
        template_section = template_lines[1] if len(template_lines) > 1 else None

        items = [
            {
                "category": "Accommodation",
                "description": "Hotel room for 1 night",
                "amount": 320.0,
                "source": "Supplier A",
            },
            {
                "category": "Transport",
                "description": "Airport transfer",
                "amount": 85.0,
                "source": "Supplier B",
            },
            {
                "category": "Meals",
                "description": "Lunch package",
                "amount": 48.0,
                "source": "Supplier C",
            },
        ]

        if output_language == "translate_russian":
            title = template.get("title_russian", "Смета по программе")
            subtitle = template.get("subtitle_russian", "Натуральный русский перевод без кальки")
            translated_items = []
            for item in items:
                translated_items.append(
                    {
                        "category": self._translate_category(item["category"]),
                        "description": self._translate_description(item["description"]),
                        "amount": item["amount"],
                        "source": item["source"],
                    }
                )
            items = translated_items
        else:
            title = template.get("title_english", template_title or "Estimate for the program")
            subtitle = template.get("subtitle_english", "English version prepared for client delivery")

        formatted_items = []
        for index, item in enumerate(items, start=1):
            formatted_items.append(
                {
                    **item,
                    "position": index,
                    "section": template.get("section_name", template_section or "Services"),
                    "template_name": template.get("name", "default"),
                }
            )

        total = round(sum(item["amount"] for item in formatted_items), 2)
        return {
            "title": title,
            "subtitle": subtitle,
            "strategy": strategy,
            "output_language": output_language,
            "items": formatted_items,
            "total": total,
            "summary": f"Selected strategy: {strategy}; total estimate: {total:.2f}",
            "template": template,
        }

    def _default_template(self) -> dict[str, Any]:
        return {
            "name": "default",
            "title_english": "Estimate for the program",
            "subtitle_english": "English version prepared for client delivery",
            "title_russian": "Смета по программе",
            "subtitle_russian": "Натуральный русский перевод без кальки",
            "section_name": "Services",
        }

    def _translate_category(self, category: str) -> str:
        mapping = {
            "Accommodation": "Размещение",
            "Transport": "Транспорт",
            "Meals": "Питание",
        }
        return mapping.get(category, category)

    def _translate_description(self, description: str) -> str:
        mapping = {
            "Hotel room for 1 night": "Номер в отеле на 1 ночь",
            "Airport transfer": "Трансфер из аэропорта",
            "Lunch package": "Комплексный обед",
        }
        return mapping.get(description, description)
