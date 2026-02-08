"""Data models for HR Data Generator."""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class GeneratorConfig:
    language: str
    employee_count: int
    num_months: int
    age_range: Tuple[int, int]
    salary_range: Tuple[int, int]
    resignation_rate: float = 0.10  # annual
    include_concurrent_positions: bool = False  # 兼務レコードを含むか
    concurrent_position_rate: float = 0.05  # 兼務者の割合 (5%)
    random_seed: Optional[int] = None
