from enum import StrEnum


class GroupStatus(StrEnum):
    FORMING = "FORMING"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
