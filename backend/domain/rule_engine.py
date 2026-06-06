# domain/rule_engine.py
# Motor de reglas determinista de Nexus-Corp para DistribLog S.A.
# Evalúa reglas de negocio contra datos de entrada sin depender de IA generativa.
# Capa: Domain — no depende de infraestructura ni aplicación.
from typing import Any, Dict, List
from .entities.business_rule import BusinessRule, RuleCondition


class RuleEngineError(Exception):
    pass


class RuleEngine:
    """
    Evalúa un conjunto de reglas activas contra un mapa de datos de entrada.
    Devuelve las reglas que cumplen TODAS sus condiciones, ordenadas por prioridad descendente.
    """

    SUPPORTED_OPERATORS = ("eq", "ne", "gt", "gte", "lt", "lte", "in", "contains")

    def evaluate(
        self, rules: List[BusinessRule], input_data: Dict[str, Any]
    ) -> List[BusinessRule]:
        matched: List[BusinessRule] = []
        for rule in rules:
            if not rule.is_active():
                continue
            if self._all_conditions_match(rule.conditions, input_data):
                matched.append(rule)
        matched.sort(key=lambda r: r.priority, reverse=True)
        return matched

    def _all_conditions_match(
        self, conditions: List[RuleCondition], data: Dict[str, Any]
    ) -> bool:
        return all(self._evaluate_condition(c, data) for c in conditions)

    def _evaluate_condition(
        self, condition: RuleCondition, data: Dict[str, Any]
    ) -> bool:
        if condition.field not in data:
            return False
        actual = data[condition.field]
        expected = condition.value
        op = condition.operator

        if op not in self.SUPPORTED_OPERATORS:
            raise RuleEngineError(f"Operador no soportado: {op}")

        if op == "eq":
            return actual == expected
        if op == "ne":
            return actual != expected
        if op == "gt":
            return self._to_number(actual) > self._to_number(expected)
        if op == "gte":
            return self._to_number(actual) >= self._to_number(expected)
        if op == "lt":
            return self._to_number(actual) < self._to_number(expected)
        if op == "lte":
            return self._to_number(actual) <= self._to_number(expected)
        if op == "in":
            return actual in expected
        if op == "contains":
            return str(expected).lower() in str(actual).lower()
        return False  # pragma: no cover

    @staticmethod
    def _to_number(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise RuleEngineError(
                f"No se puede convertir '{value}' a número para comparación."
            ) from exc

    def build_explanation(
        self, matched_rules: List[BusinessRule], input_data: Dict[str, Any]
    ) -> str:
        if not matched_rules:
            return "Ninguna regla activa aplica a la situación descrita."
        lines = ["Se activaron las siguientes reglas de negocio:"]
        for rule in matched_rules:
            lines.append(
                f"  • [{rule.name}] (prioridad {rule.priority}, "
                f"confianza {rule.confidence_level*100:.0f}%): {rule.suggested_action}"
            )
        return "\n".join(lines)

    def calculate_aggregate_confidence(self, matched_rules: List[BusinessRule]) -> float:
        if not matched_rules:
            return 0.0
        return sum(r.confidence_level for r in matched_rules) / len(matched_rules)

    def estimate_risk(self, matched_rules: List[BusinessRule]) -> str:
        if not matched_rules:
            return "bajo"
        avg_priority = sum(r.priority for r in matched_rules) / len(matched_rules)
        if avg_priority >= 8:
            return "alto"
        if avg_priority >= 5:
            return "medio"
        return "bajo"
