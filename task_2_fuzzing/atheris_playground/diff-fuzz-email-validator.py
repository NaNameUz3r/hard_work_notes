import atheris
import sys

from email_validator import validate_email, EmailNotValidError
import validators


def TestInput(input_bytes):
    fuzz_data_provider = atheris.FuzzedDataProvider(input_bytes)
    email = fuzz_data_provider.ConsumeString(25)
    is_valid = validators.email(email)

    try:
        is_valid_2 = validate_email(email)
        if not is_valid:
            print(email)
            print(is_valid)
            print(is_valid_2)
            raise Exception(
                "Diff between validators.email and validate_email: validators False, email_validator True"
            )

    except EmailNotValidError:
        if is_valid:
            print(email)
            print(is_valid)
            raise Exception(
                "Diff between validators.email and validate_email: validators True, email_validator False"
            )


atheris.Setup(sys.argv, TestInput)
atheris.Fuzz()
