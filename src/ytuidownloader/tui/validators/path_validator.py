import os

from textual.validation import ValidationResult, Validator


class PathValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if os.path.exists(value) and os.path.isdir(value):
            return self.success()
        else:
            return self.failure()
