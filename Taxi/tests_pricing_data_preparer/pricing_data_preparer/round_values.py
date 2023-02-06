import decimal


# Returns same data structure but with all floats rounded
def round_values(
        response, rounding=decimal.ROUND_HALF_UP, rounding_factor='0.0000001',
):
    if isinstance(response, list):
        for idx, item in enumerate(response):
            response[idx] = round_values(item)
    elif isinstance(response, dict):
        for key, val in response.items():
            response[key] = round_values(val)
    elif isinstance(response, float):
        response = float(
            decimal.Decimal(response).quantize(
                decimal.Decimal(rounding_factor), rounding=rounding,
            ),
        )
    return response
