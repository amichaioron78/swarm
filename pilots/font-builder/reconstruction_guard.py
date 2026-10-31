"""Verify reconstructed TrueType geometry before editing an existing glyph.

Hints are intentionally excluded: an isolated unhinted prototype must compare
with a matched unhinted control. This does not establish visual quality.
"""


def verify_geometry(original, rebuilt, glyf):
    old_coords, old_ends, old_flags = original.getCoordinates(glyf)
    new_coords, new_ends, new_flags = rebuilt.getCoordinates(glyf)
    checks = {
        'coordinates_equal': list(old_coords) == list(new_coords),
        'contour_endpoints_equal': list(old_ends) == list(new_ends),
        'point_flags_equal': list(old_flags) == list(new_flags),
    }
    if not all(checks.values()):
        raise ValueError('Baseline reconstruction mismatch: ' +
                         ', '.join(key for key, value in checks.items() if not value))
    return checks
