from __future__ import annotations

from typing import Any


class EstimateBuilder:
    """Build a simple estimate payload that can be rendered in English or Russian."""

    def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        strategy = payload.get("strategy", "lowest_price")
        output_language = payload.get("output_language", "keep_english")
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
            title = "Смета по программе"
            subtitle = "Натуральный русский перевод без кальки"
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
            title = "Estimate for the program"
            subtitle = "English version prepared for client delivery"

        total = round(sum(item["amount"] for item in items), 2)
        return {
            "title": title,
            "subtitle": subtitle,
            "strategy": strategy,
            "output_language": output_language,
            "items": items,
            "total": total,
            "summary": f"Selected strategy: {strategy}; total estimate: {total:.2f}",
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
