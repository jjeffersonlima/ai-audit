"""Deterministic financial calculations for opportunities."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from typing import Any

from .models import RoiScenario


MONEY_PLACES = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_PLACES)


@dataclass(frozen=True)
class RoiInputs:
    hours_per_execution: Decimal
    executions_per_month: Decimal
    hourly_cost: Decimal
    error_rate: Decimal
    cost_per_error: Decimal
    automation_hours_per_execution: Decimal = Decimal("0")
    automation_error_rate: Decimal = Decimal("0")
    monthly_subscription: Decimal = Decimal("0")
    setup_hours: Decimal = Decimal("0")
    consultant_hourly_rate: Decimal = Decimal("0")

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "RoiInputs":
        """Build inputs from agent data without silently filling required values."""
        required = (
            "hours_per_execution",
            "executions_per_month",
            "hourly_cost",
            "error_rate",
            "cost_per_error",
        )
        missing = [name for name in required if name not in values or values[name] in (None, "")]
        if missing:
            raise ValueError(f"Operandos obrigatórios ausentes: {', '.join(missing)}")

        def decimal(name: str) -> Decimal:
            value = values.get(name, Decimal("0"))
            try:
                return value if isinstance(value, Decimal) else Decimal(str(value))
            except (InvalidOperation, ValueError) as exc:
                raise ValueError(f"Operando inválido: {name}") from exc

        return cls(**{name: decimal(name) for name in cls.__dataclass_fields__})

    def validate(self) -> None:
        numeric_fields = {
            "hours_per_execution": self.hours_per_execution,
            "executions_per_month": self.executions_per_month,
            "hourly_cost": self.hourly_cost,
            "error_rate": self.error_rate,
            "cost_per_error": self.cost_per_error,
            "automation_hours_per_execution": self.automation_hours_per_execution,
            "automation_error_rate": self.automation_error_rate,
            "monthly_subscription": self.monthly_subscription,
            "setup_hours": self.setup_hours,
            "consultant_hourly_rate": self.consultant_hourly_rate,
        }
        for name, value in numeric_fields.items():
            if not isinstance(value, Decimal):
                raise TypeError(f"{name} deve ser Decimal")
            if value < 0:
                raise ValueError(f"{name} não pode ser negativo")
        if self.error_rate > 1 or self.automation_error_rate > 1:
            raise ValueError("error_rate deve estar entre 0 e 1")


def calculate_roi(inputs: RoiInputs, name: str = "base") -> RoiScenario:
    inputs.validate()
    monthly_executions = inputs.executions_per_month
    manual_monthly_labor = inputs.hours_per_execution * monthly_executions * inputs.hourly_cost
    manual_monthly_errors = monthly_executions * inputs.error_rate * inputs.cost_per_error
    automated_monthly_labor = inputs.automation_hours_per_execution * monthly_executions * inputs.hourly_cost
    automated_monthly_errors = monthly_executions * inputs.automation_error_rate * inputs.cost_per_error

    annual_manual = money((manual_monthly_labor + manual_monthly_errors) * 12)
    annual_recurring_automated = money((automated_monthly_labor + automated_monthly_errors + inputs.monthly_subscription) * 12)
    setup_cost = money(inputs.setup_hours * inputs.consultant_hourly_rate)
    first_year_cost = money(annual_recurring_automated + setup_cost)
    annual_savings = money(annual_manual - annual_recurring_automated)
    net_first_year = money(annual_manual - first_year_cost)
    roi = None if first_year_cost == 0 else str(money(net_first_year / first_year_cost))
    monthly_savings = manual_monthly_labor + manual_monthly_errors - automated_monthly_labor - automated_monthly_errors - inputs.monthly_subscription
    breakeven = None if monthly_savings <= 0 else int((setup_cost / monthly_savings).to_integral_value(rounding=ROUND_CEILING))
    three_year_savings = money((annual_manual * 3) - (annual_recurring_automated * 3 + setup_cost))

    return RoiScenario(
        name=name,
        annual_manual_cost=str(annual_manual),
        annual_automated_cost=str(annual_recurring_automated),
        first_year_investment=str(first_year_cost),
        annual_savings=str(annual_savings),
        first_year_roi=roi,
        monthly_breakeven=breakeven,
        three_year_savings=str(three_year_savings),
        assumptions=["Custos e taxas devem ser confirmados pelo cliente antes da decisão."],
        inputs={name: str(value) for name, value in {
            field_name: getattr(inputs, field_name)
            for field_name in inputs.__dataclass_fields__
        }.items()},
    )


def calculate_roi_scenarios(
    scenarios: dict[str, RoiInputs],
) -> list[RoiScenario]:
    """Calculate only explicitly supplied scenarios in stable order."""
    order = ("conservative", "base", "optimistic")
    names = [name for name in order if name in scenarios]
    names.extend(sorted(name for name in scenarios if name not in order))
    return [calculate_roi(scenarios[name], name=name) for name in names]
