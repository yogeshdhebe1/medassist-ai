from pydantic import BaseModel, field_validator


class UserSettingsResponse(BaseModel):
    notifications_enabled: bool
    email_notifications: bool
    push_notifications: bool
    language: str
    theme: str

    class Config:
        from_attributes = True


class UserSettingsUpdateRequest(BaseModel):
    notifications_enabled: bool | None = None
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    language: str | None = None
    theme: str | None = None

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is not None and v not in {"en", "hi", "es", "fr"}:
            raise ValueError("language must be one of: en, hi, es, fr")
        return v

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: str | None) -> str | None:
        if v is not None and v not in {"light", "dark"}:
            raise ValueError("theme must be 'light' or 'dark'")
        return v
