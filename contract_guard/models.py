from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    BREAKING = "breaking"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class ContractChange:
    path: str
    severity: Severity
    kind: str
    message: str


@dataclass(frozen=True)
class ComparisonResult:
    changes: tuple[ContractChange, ...]

    @property
    def breaking(self) -> tuple[ContractChange, ...]:
        return tuple(
            change
            for change in self.changes
            if change.severity is Severity.BREAKING
        )

    @property
    def has_breaking_changes(self) -> bool:
        return bool(self.breaking)
