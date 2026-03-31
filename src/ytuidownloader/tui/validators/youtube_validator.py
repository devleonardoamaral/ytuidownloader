from textual.validation import ValidationResult, Validator


class YoutubeValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if (
            value.startswith("https://www.youtube.com/")
            or value.startswith("www.youtube.com/")
            or value.startswith("https://youtu.be/")
        ):
            return self.success()
        else:
            return self.failure("Link inválido!")
