from app.schemas import GroupFilter


def test_group_filter_accepts_field_names():
    """Services construct GroupFilter by python field name, not by query alias."""
    group_filter = GroupFilter(section_id=5)

    assert group_filter.section_id == 5
    assert group_filter.model_dump(exclude_unset=True) == {"section_id": 5}


def test_group_filter_accepts_query_aliases():
    group_filter = GroupFilter.model_validate({"section-id": 7})

    assert group_filter.section_id == 7
