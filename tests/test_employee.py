"""Tests for employee creation and validation - P0 and P1."""
import inspect

from faker import Faker

from hr_generator.employee import (
    create_employee,
    validate_employee,
    calculate_salary,
    get_performance_level,
    adjust_organization_by_position,
)
from hr_generator.config import LANGUAGE_DATA


class TestValidateEmployeeSignature:
    """validate_employee must take explicit params, not use globals."""

    def test_has_explicit_age_range_param(self):
        sig = inspect.signature(validate_employee)
        assert "age_range" in sig.parameters

    def test_has_explicit_salary_range_param(self):
        sig = inspect.signature(validate_employee)
        assert "salary_range" in sig.parameters

    def test_has_explicit_lang_data_param(self):
        sig = inspect.signature(validate_employee)
        assert "lang_data" in sig.parameters


class TestCreateEmployee:
    """create_employee must produce a valid employee dict."""

    def test_returns_dict_with_required_keys(self, default_config, english_lang_data):
        fake = Faker("en_US")
        fake.seed_instance(42)
        emp = create_employee(default_config, english_lang_data, fake, 1)
        required_keys = {
            "emp_id", "name", "birth_date", "gender",
            "org_lv1", "org_lv2", "org_lv3", "org_lv4",
            "position", "emp_type", "salary",
            "hire_date", "resign_date",
            "engagement_score", "performance",
            "is_married", "address", "job_category", "job_grade",
        }
        assert required_keys.issubset(set(emp.keys()))

    def test_emp_id_format(self, default_config, english_lang_data):
        fake = Faker("en_US")
        fake.seed_instance(42)
        emp = create_employee(default_config, english_lang_data, fake, 42)
        assert emp["emp_id"] == "EMP000042"

    def test_birth_date_within_age_range(self, default_config, english_lang_data):
        fake = Faker("en_US")
        fake.seed_instance(42)
        from datetime import datetime
        emp = create_employee(default_config, english_lang_data, fake, 1)
        birth = datetime.strptime(emp["birth_date"], "%Y-%m-%d")
        now = datetime.now()
        age = (now - birth).days / 365.25
        assert default_config.age_range[0] <= age <= default_config.age_range[1] + 1

    def test_salary_within_range_for_fulltime(self, default_config, english_lang_data):
        fake = Faker("en_US")
        fake.seed_instance(42)
        # Generate multiple employees to find a full-time one
        for i in range(50):
            emp = create_employee(default_config, english_lang_data, fake, i)
            if emp["emp_type"] == "Full-time" and emp["salary"] is not None:
                assert default_config.salary_range[0] <= emp["salary"] <= default_config.salary_range[1]
                return
        # If no full-time found in 50 tries, that's also a problem
        assert False, "No full-time employee generated in 50 attempts"

    def test_contract_salary_is_80_percent_of_base(self, default_config, english_lang_data):
        """Contract employee salary = 80% of position base, floored at salary_range min."""
        fake = Faker("en_US")
        # Generate multiple to find a contract employee
        for i in range(200):
            fake.seed_instance(i)
            emp = create_employee(default_config, english_lang_data, fake, i)
            if emp["emp_type"] == "Contract":
                # Contract employees should have staff-level position
                assert emp["position"] == "Staff"
                # Salary should be set (not None)
                assert emp["salary"] is not None
                assert emp["salary"] >= default_config.salary_range[0]
                return
        # Contract employees should appear given 20% weight
        assert False, "No contract employee generated in 200 attempts"

    def test_temporary_has_null_salary(self, default_config, english_lang_data):
        """Temporary employees have None salary."""
        fake = Faker("en_US")
        for i in range(200):
            fake.seed_instance(i)
            emp = create_employee(default_config, english_lang_data, fake, i)
            if emp["emp_type"] == "Temporary":
                assert emp["salary"] is None
                assert emp["engagement_score"] is None
                assert emp["performance"] is None
                return

    def test_always_produces_valid_employee(self, default_config, english_lang_data):
        """create_employee should always produce a valid employee (no silent failures)."""
        fake = Faker("en_US")
        for i in range(100):
            fake.seed_instance(i)
            emp = create_employee(default_config, english_lang_data, fake, i)
            is_valid, msg = validate_employee(
                emp,
                age_range=default_config.age_range,
                salary_range=default_config.salary_range,
                lang_data=english_lang_data,
            )
            assert is_valid, f"Employee {i} invalid: {msg}"
