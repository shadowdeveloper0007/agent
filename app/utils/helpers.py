"""Utility helpers."""


def apply_partial_update(model_obj: object, updates: dict) -> None:
    for field, value in updates.items():
        setattr(model_obj, field, value)
