from dataclasses import dataclass


@dataclass
class APIResponse:
    is_success: bool
    body: dict = None
    error_message: str = None

    def __post_init__(self):
        if self.is_success:
            if self.error_message:
                raise ValueError("Success response should not have an error message.")
        else:
            if not self.error_message:
                raise ValueError("Failure response requires an error message.")
            if self.body is not None:
                raise ValueError("Failure response should not have a body.")
