# application/use_cases/get_kpi_dashboard.py
# Calcula los KPIs del dashboard ejecutivo de Nexus-Corp.
# Capa: Application.
from datetime import datetime, timedelta
from typing import List

from backend.domain.repositories import IBusinessRuleRepository, IDecisionRepository, IFeedbackRepository
from backend.domain.entities.business_rule import RuleStatus
from backend.application.dtos.kpi_dto import KPIDashboardDTO, KPITrendsDTO, TrendPointDTO


class GetKPIDashboardUseCase:
    def __init__(
        self,
        rule_repo: IBusinessRuleRepository,
        decision_repo: IDecisionRepository,
        feedback_repo: IFeedbackRepository,
    ):
        self._rule_repo = rule_repo
        self._decision_repo = decision_repo
        self._feedback_repo = feedback_repo

    def get_dashboard(self) -> KPIDashboardDTO:
        history = self._decision_repo.get_history(limit=1000)
        total = len(history)

        accepted = sum(1 for h in history if h.get("outcome") == "aceptada")
        acceptance_rate = (accepted / total * 100) if total else 0.0

        all_fb = self._feedback_repo.get_all()
        avg_rating = (sum(f.rating for f in all_fb) / len(all_fb)) if all_fb else 0.0

        active_rules = len(self._rule_repo.get_active_rules())
        in_review = len(self._rule_repo.get_by_status(RuleStatus.IN_REVIEW))

        cutoff = datetime.utcnow() - timedelta(days=7)
        recent = [h for h in history if h.get("requested_at") and h["requested_at"] >= cutoff]

        return KPIDashboardDTO(
            total_decisions=total,
            acceptance_rate=round(acceptance_rate, 2),
            average_response_time_ms=0.0,
            active_rules_count=active_rules,
            average_feedback_rating=round(avg_rating, 2),
            decisions_last_7_days=len(recent),
            rules_in_review=in_review,
        )

    def get_trends(self, days: int = 30) -> KPITrendsDTO:
        history = self._decision_repo.get_history(limit=5000)
        today = datetime.utcnow().date()
        points: List[TrendPointDTO] = []

        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            day_records = [
                h for h in history
                if h.get("requested_at") and h["requested_at"].date() == day
            ]
            accepted = sum(1 for h in day_records if h.get("outcome") == "aceptada")
            confidences = [h.get("confidence", 0.0) for h in day_records if h.get("confidence") is not None]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
            points.append(TrendPointDTO(
                date=day.isoformat(),
                decisions=len(day_records),
                accepted=accepted,
                avg_confidence=round(avg_conf, 3),
            ))

        return KPITrendsDTO(trends=points)
