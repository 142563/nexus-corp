# tests/unit/test_rule_engine.py
# Pruebas unitarias del motor de reglas — verifica cada operador.
import pytest
from datetime import datetime
from backend.domain.rule_engine import RuleEngine, RuleEngineError
from backend.domain.entities.business_rule import BusinessRule, RuleCondition, RuleStatus


def make_rule(conditions, priority=5, confidence=0.9):
    return BusinessRule(
        id=1, name="Test", description="Test", conditions=conditions,
        suggested_action="Acción", priority=priority,
        area_id=1, expert_id=1, status=RuleStatus.ACTIVE, confidence_level=confidence,
    )


engine = RuleEngine()


class TestRuleEngineOperators:
    def test_eq_true(self):
        rule = make_rule([RuleCondition("tipo", "eq", "alta")])
        assert engine.evaluate([rule], {"tipo": "alta"}) == [rule]

    def test_eq_false(self):
        rule = make_rule([RuleCondition("tipo", "eq", "alta")])
        assert engine.evaluate([rule], {"tipo": "baja"}) == []

    def test_ne(self):
        rule = make_rule([RuleCondition("estado", "ne", "inactivo")])
        assert engine.evaluate([rule], {"estado": "activo"}) == [rule]

    def test_gt(self):
        rule = make_rule([RuleCondition("delay", "gt", 120)])
        assert engine.evaluate([rule], {"delay": 150}) == [rule]
        assert engine.evaluate([rule], {"delay": 120}) == []

    def test_gte(self):
        rule = make_rule([RuleCondition("delay", "gte", 120)])
        assert engine.evaluate([rule], {"delay": 120}) == [rule]

    def test_lt(self):
        rule = make_rule([RuleCondition("stock", "lt", 50)])
        assert engine.evaluate([rule], {"stock": 30}) == [rule]
        assert engine.evaluate([rule], {"stock": 50}) == []

    def test_lte(self):
        rule = make_rule([RuleCondition("stock", "lte", 50)])
        assert engine.evaluate([rule], {"stock": 50}) == [rule]

    def test_in(self):
        rule = make_rule([RuleCondition("zone", "in", ["A", "B", "C"])])
        assert engine.evaluate([rule], {"zone": "B"}) == [rule]
        assert engine.evaluate([rule], {"zone": "D"}) == []

    def test_contains(self):
        rule = make_rule([RuleCondition("notes", "contains", "urgente")])
        assert engine.evaluate([rule], {"notes": "Pedido URGENTE confirmado"}) == [rule]

    def test_missing_field_no_match(self):
        rule = make_rule([RuleCondition("campo_inexistente", "eq", "x")])
        assert engine.evaluate([rule], {"otro_campo": "x"}) == []

    def test_invalid_operator_raises(self):
        rule = make_rule([RuleCondition("x", "between", 1)])
        with pytest.raises(RuleEngineError):
            engine.evaluate([rule], {"x": 5})

    def test_inactive_rule_ignored(self):
        rule = make_rule([RuleCondition("tipo", "eq", "alta")])
        rule.status = RuleStatus.INACTIVE
        assert engine.evaluate([rule], {"tipo": "alta"}) == []

    def test_multiple_conditions_all_must_match(self):
        rule = make_rule([
            RuleCondition("priority", "eq", "alta"),
            RuleCondition("delay", "gt", 100),
        ])
        assert engine.evaluate([rule], {"priority": "alta", "delay": 150}) == [rule]
        assert engine.evaluate([rule], {"priority": "alta", "delay": 50}) == []

    def test_priority_order(self):
        r1 = make_rule([RuleCondition("x", "eq", 1)], priority=3)
        r2 = make_rule([RuleCondition("x", "eq", 1)], priority=9)
        r1.id = 1
        r2.id = 2
        result = engine.evaluate([r1, r2], {"x": 1})
        assert result[0].priority == 9

    def test_aggregate_confidence(self):
        r1 = make_rule([], confidence=0.80)
        r2 = make_rule([], confidence=0.90)
        conf = engine.calculate_aggregate_confidence([r1, r2])
        assert abs(conf - 0.85) < 0.001

    def test_risk_estimation(self):
        high = make_rule([], priority=9)
        mid = make_rule([], priority=6)
        low = make_rule([], priority=2)
        assert engine.estimate_risk([high]) == "alto"
        assert engine.estimate_risk([mid]) == "medio"
        assert engine.estimate_risk([low]) == "bajo"
        assert engine.estimate_risk([]) == "bajo"
