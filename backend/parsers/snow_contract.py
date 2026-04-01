"""Shared normalization for scraper snow depth / new-snow dict values (data contract)."""

# Resorts often use "-" or unicode dashes when season ended or depth is not reported.
DASH_PLACEHOLDERS = frozenset({"-", "--", "–", "―"})


def normalize_depth_value(raw):
    """Return a digit-only string suitable for tests and export; unknown → '0'."""
    if raw is None:
        return "0"
    if isinstance(raw, bool):
        return "0"
    if isinstance(raw, int):
        return str(raw)
    if isinstance(raw, float):
        return str(int(raw)) if raw.is_integer() else "0"

    s = str(raw).strip().replace("cm", "").strip()
    if s in DASH_PLACEHOLDERS:
        return "0"
    return s if s.isdigit() else "0"


def normalize_snow_dict(d):
    if not isinstance(d, dict):
        return d
    return {k: normalize_depth_value(v) for k, v in d.items()}


def normalize_scraper_result(data):
    """Apply snow dict rules to indices 1 (depth) and 2 (new snow) of the contract list."""
    if data is None:
        return None
    if not isinstance(data, list) or len(data) < 3:
        return data
    if isinstance(data[1], dict):
        data[1] = normalize_snow_dict(data[1])
    if isinstance(data[2], dict):
        data[2] = normalize_snow_dict(data[2])
    return data
