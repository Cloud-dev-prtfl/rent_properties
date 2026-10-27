class DomainError(Exception):
    """Base class for business-rule violations.

    `code` is stable and safe to show in logs and templates; messages may change.
    """

    code: str = "domain_error"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.code)
        if code is not None:
            self.code = code
