import pytest
from hr_generator.models import GeneratorConfig
from hr_generator.config import LANGUAGE_DATA


@pytest.fixture
def default_config():
    return GeneratorConfig(
        language="English",
        employee_count=200,
        num_months=1,
        age_range=(25, 55),
        salary_range=(4000000, 10000000),
        random_seed=42,
    )


@pytest.fixture
def multi_month_config():
    return GeneratorConfig(
        language="English",
        employee_count=100,
        num_months=12,
        age_range=(25, 55),
        salary_range=(4000000, 10000000),
        random_seed=42,
    )


@pytest.fixture
def english_lang_data():
    return LANGUAGE_DATA["English"]


@pytest.fixture
def japanese_lang_data():
    return LANGUAGE_DATA["Japanese"]
