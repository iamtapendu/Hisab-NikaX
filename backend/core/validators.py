import re
from fastapi import HTTPException, status


class Pattern:
    USERNAME_REGX = r"^(?=.{3,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$"
    NAME_REGX = r"^[A-Za-z][A-Za-z0-9 ]{3,49}$"
    EMAIL_REGX = (
        r"^(?!.*\.\.)"
        r"([A-Za-z0-9_+%-]+(?:\.[A-Za-z0-9_+%-]+)*)"
        r"@"
        r"([A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*)"
        r"\.[A-Za-z]{2,5}$"
    )
    PHONE_REGX = r"^[6-9]\d{9}$"
    PASSWORD_REGX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)" r"(?=.*[@$!%*?&#^])[A-Za-z\d@$!%*?&#^]{8,}$"
    ROLE_REGX = r"^(admin|manager|staff|guest)$"
    PAYMENT_STATUS_REGEX = r"^(paid|pending|partial)$"
    UNIT_REGEX = r"^(pcs|pair|kg|gram|grs|ltr|ml|box|pkt|set|dozen)$"
    IMAGE_REGX = r"^[A-Za-z0-9_/\-]+\.(jpg|jpeg|png)$"
    ADDRESS_REGX = r"^[A-Za-z0-9\s,\./\-]{5,200}$"
    GST_REGX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    ADHAAR_REGX = r"^[2-9]\d{11}$"
    BANK_REGX = r"^\d{9,18}$"
    IFSC_REGX = r"^[A-Z]{4}0[0-9]{6}$"
    PAN_REGX = r"^[A-Z]{5}\d{4}[A-Z]$"
    NUM_REGEX = r"^-?\d+(\.\d+)?$"
    HSN_REGEX = r"^\d{4}(\d{2})?(\d{2})?$"


def validate_map(data, validators: dict[str, str]):
    """
    Function for validation of given data with mapped patterns


    :Example:

    ```
    validate(car,{"engine": r"\\d+HP"})
    ```
    it will validate **car.engine** is following 600HP, 120HP like pattern or not.
    """
    for field, pattern in validators.items():
        value = getattr(data, field, None)

        if value is None:
            continue

        if not isinstance(value, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "msg": "Validation error",
                    "errors": f"{field} must be a string",
                },
            )
        if not re.fullmatch(pattern, value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"msg": "Validation error", "errors": f"Invalid {field}: {value}"},
            )
