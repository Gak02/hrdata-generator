"""Tests for organization hierarchy adjustments - P1 deduplication."""
from hr_generator.employee import adjust_organization_by_position


class TestAdjustOrganizationByPosition:
    def test_executive_nullifies_lv2_lv3_lv4(self, english_lang_data):
        emp = {"org_lv2": "Sales", "org_lv3": "Team", "org_lv4": "Alpha"}
        position_data = english_lang_data["positions"]
        result = adjust_organization_by_position(emp, position_data, "VP")
        assert result["org_lv2"] is None
        assert result["org_lv3"] is None
        assert result["org_lv4"] is None

    def test_clevel_nullifies_lv2_lv3_lv4(self, english_lang_data):
        emp = {"org_lv2": "Sales", "org_lv3": "Team", "org_lv4": "Alpha"}
        position_data = english_lang_data["positions"]
        result = adjust_organization_by_position(emp, position_data, "C-level")
        assert result["org_lv2"] is None
        assert result["org_lv3"] is None
        assert result["org_lv4"] is None

    def test_director_nullifies_lv3_lv4(self, english_lang_data):
        emp = {"org_lv2": "Sales", "org_lv3": "Team", "org_lv4": "Alpha"}
        position_data = english_lang_data["positions"]
        result = adjust_organization_by_position(emp, position_data, "General Manager")
        assert result["org_lv2"] == "Sales"
        assert result["org_lv3"] is None
        assert result["org_lv4"] is None

    def test_manager_nullifies_lv4(self, english_lang_data):
        emp = {"org_lv2": "Sales", "org_lv3": "Team", "org_lv4": "Alpha"}
        position_data = english_lang_data["positions"]
        result = adjust_organization_by_position(emp, position_data, "Manager")
        assert result["org_lv2"] == "Sales"
        assert result["org_lv3"] == "Team"
        assert result["org_lv4"] is None

    def test_staff_keeps_all_levels(self, english_lang_data):
        emp = {"org_lv2": "Sales", "org_lv3": "Team", "org_lv4": "Alpha"}
        position_data = english_lang_data["positions"]
        result = adjust_organization_by_position(emp, position_data, "Staff")
        assert result["org_lv2"] == "Sales"
        assert result["org_lv3"] == "Team"
        assert result["org_lv4"] == "Alpha"

    def test_japanese_executive(self, japanese_lang_data):
        emp = {"org_lv2": "営業", "org_lv3": "チーム", "org_lv4": "第一"}
        position_data = japanese_lang_data["positions"]
        result = adjust_organization_by_position(emp, position_data, "取締役")
        assert result["org_lv2"] is None
        assert result["org_lv3"] is None
        assert result["org_lv4"] is None


class TestNoDuplicateOrgFunction:
    """update_organization_hierarchy should not exist."""

    def test_no_duplicate_function(self):
        from hr_generator import employee
        assert not hasattr(employee, "update_organization_hierarchy")
