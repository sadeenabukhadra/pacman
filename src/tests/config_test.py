from config_validater import config_validator


def run_test(name: str, config: dict) -> None:
    print("\n" + "=" * 60)
    print(f"TEST: {name}")
    print("=" * 60)

    try:
        result = config_validator(config)

        print("\nValidated config:")
        for key, value in result.items():
            print(f"{key}: {value}")

        print("\nRESULT: PASSED - No crash")

    except Exception as error:
        print(f"\nRESULT: FAILED - {type(error).__name__}: {error}")


# --------------------------------------------------
# Test 1: Correct config
# --------------------------------------------------

run_test(
    "Valid config",
    {
        "highscore_filename": "scores.json",
        "theme": "ice",
        "lives": 5,
        "pacgum": 50,
        "point_per_pacgum": 20,
        "point_per_super_pacgum": 100,
        "point_per_ghost": 300,
        "seed": 100,
        "level_max_time": 120,
        "level": [
            {"width": 14, "height": 14},
            {"width": 18, "height": 18},
            {"width": 22, "height": 22},
            {"width": 26, "height": 26},
            {"width": 30, "height": 30},
            {"width": 34, "height": 34},
            {"width": 38, "height": 38},
            {"width": 42, "height": 42},
            {"width": 46, "height": 46},
            {"width": 50, "height": 50},
        ],
    },
)


# --------------------------------------------------
# Test 2: Empty config
# --------------------------------------------------

run_test(
    "Empty config",
    {},
)


# --------------------------------------------------
# Test 3: Wrong types
# --------------------------------------------------

run_test(
    "Wrong types",
    {
        "highscore_filename": 42,
        "theme": 42,
        "lives": "three",
        "pacgum": "42",
        "point_per_pacgum": "10",
        "point_per_super_pacgum": [],
        "point_per_ghost": None,
        "seed": "random",
        "level_max_time": 90.5,
        "level": "not a list",
    },
)


# --------------------------------------------------
# Test 4: Invalid integer values
# --------------------------------------------------

run_test(
    "Invalid integer values",
    {
        "highscore_filename": "scores.json",
        "theme": "cosmic",
        "lives": -1,
        "pacgum": -42,
        "point_per_pacgum": -10,
        "point_per_super_pacgum": -50,
        "point_per_ghost": -200,
        "seed": -42,
        "level_max_time": 0,
        "level": [
            {"width": 14, "height": 14},
            {"width": 18, "height": 18},
            {"width": 22, "height": 22},
            {"width": 26, "height": 26},
            {"width": 30, "height": 30},
            {"width": 34, "height": 34},
            {"width": 38, "height": 38},
            {"width": 42, "height": 42},
            {"width": 46, "height": 46},
            {"width": 50, "height": 50},
        ],
    },
)


# --------------------------------------------------
# Test 5: Invalid theme and empty filename
# --------------------------------------------------

run_test(
    "Invalid strings",
    {
        "highscore_filename": "   ",
        "theme": "banana",
        "lives": 3,
        "pacgum": 42,
        "point_per_pacgum": 10,
        "point_per_super_pacgum": 50,
        "point_per_ghost": 200,
        "seed": 42,
        "level_max_time": 90,
        "level": [
            {"width": 14, "height": 14},
            {"width": 18, "height": 18},
            {"width": 22, "height": 22},
            {"width": 26, "height": 26},
            {"width": 30, "height": 30},
            {"width": 34, "height": 34},
            {"width": 38, "height": 38},
            {"width": 42, "height": 42},
            {"width": 46, "height": 46},
            {"width": 50, "height": 50},
        ],
    },
)


# --------------------------------------------------
# Test 6: Less than 10 levels
# --------------------------------------------------

run_test(
    "Less than 10 levels",
    {
        "highscore_filename": "scores.json",
        "theme": "cosmic",
        "lives": 3,
        "pacgum": 42,
        "point_per_pacgum": 10,
        "point_per_super_pacgum": 50,
        "point_per_ghost": 200,
        "seed": 42,
        "level_max_time": 90,
        "level": [
            {"width": 14, "height": 14},
            {"width": 18, "height": 18},
        ],
    },
)


# --------------------------------------------------
# Test 7: Invalid level
# --------------------------------------------------

run_test(
    "Invalid level structure",
    {
        "highscore_filename": "scores.json",
        "theme": "cosmic",
        "lives": 3,
        "pacgum": 42,
        "point_per_pacgum": 10,
        "point_per_super_pacgum": 50,
        "point_per_ghost": 200,
        "seed": 42,
        "level_max_time": 90,
        "level": [
            {"width": 14, "height": 14},
            {"width": 18, "height": 18},
            {"width": 22, "height": 22},
            {"width": 26, "height": 26},
            {"width": 30, "height": 30},
            {"width": 34, "height": 34},
            {"width": 38, "height": 38},
            {"width": 42, "height": 42},
            {"width": 46, "height": 46},

            # Invalid level
            {"width": -10, "height": 50},
        ],
    },
)


# --------------------------------------------------
# Test 8: Boolean instead of integer
# --------------------------------------------------

run_test(
    "Boolean instead of integer",
    {
        "highscore_filename": "scores.json",
        "theme": "ice",
        "lives": True,
        "pacgum": False,
        "point_per_pacgum": True,
        "point_per_super_pacgum": False,
        "point_per_ghost": True,
        "seed": False,
        "level_max_time": True,
        "level": [
            {"width": 14, "height": 14},
            {"width": 18, "height": 18},
            {"width": 22, "height": 22},
            {"width": 26, "height": 26},
            {"width": 30, "height": 30},
            {"width": 34, "height": 34},
            {"width": 38, "height": 38},
            {"width": 42, "height": 42},
            {"width": 46, "height": 46},
            {"width": 50, "height": 50},
        ],
    },
)
