from hive.schema import CompanyProfile

MAX_NAME_LENGTH = 200


class InvalidCompanyNameError(ValueError):
    pass


def intake(profile: CompanyProfile) -> CompanyProfile:
    name = " ".join(profile.input_name.split())

    if not name:
        raise InvalidCompanyNameError("Company name cannot be empty.")
    if not any(char.isalpha() for char in name):
        raise InvalidCompanyNameError(
            f"'{profile.input_name}' does not look like a company name (no letters found)."
        )
    if len(name) > MAX_NAME_LENGTH:
        raise InvalidCompanyNameError(
            f"Company name is too long ({len(name)} characters, max {MAX_NAME_LENGTH})."
        )

    profile.canonical_name = name
    return profile
