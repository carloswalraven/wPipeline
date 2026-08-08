"""Grammar of the names the pipeline lets you create.

Pure functions: no disk, no configuration loading. The grammar arrives as an
argument, read from the versioned policy by whoever calls. That is deliberate.
The moment a rule is written as a constant here, one studio's flavor is baked
into the tool, and the closed vocabulary stops being configuration.

Stage 1a only owns the project code and the project name. Sequences, shots and
assets get their grammar in stage 1b.
"""

from .errors import ValidationError


def validate_project_code(code, grammar):
    """Returns the code unchanged, or raises ValidationError explaining why not.

    The code is never corrected on the caller's behalf: 'dem' does not become
    'DEM'. A gatekeeper that guesses is a gatekeeper you cannot trust, and the
    cost of guessing wrong is a prefix welded to every published file of the
    show.
    """
    length = grammar["length"]
    alphabet = grammar["alphabet"]
    reserved = grammar["reserved"]

    if not isinstance(code, str):
        raise ValidationError(
            f"Project code must be text, got {type(code).__name__}."
        )

    if len(code) != length:
        raise ValidationError(
            f"Project code must be exactly {length} characters, got "
            f"{len(code)} in '{code}'."
        )

    for character in code:
        if character not in alphabet:
            raise ValidationError(
                "Project code accepts only uppercase A-Z, no digits and no "
                f"accents. Character '{character}' in '{code}' is not allowed."
            )

    if code in reserved:
        raise ValidationError(
            f"Project code '{code}' is reserved and cannot be used. Reserved "
            f"codes: {', '.join(sorted(reserved))}."
        )

    return code


def validate_project_name(name):
    """Returns the name with surrounding blanks removed, or raises.

    Free text in any language, accents included: the name never touches disk,
    because the folder is called after the code. Surrounding blanks are dropped
    because they are always a typo, never a decision.
    """
    if not isinstance(name, str):
        raise ValidationError(
            f"Project name must be text, got {type(name).__name__}."
        )

    cleaned = name.strip()
    if not cleaned:
        raise ValidationError("Project name cannot be empty.")

    return cleaned
