import pytest

EVENT_BUS_SETTINGS = pytest.mark.config(
    GROCERY_EVENT_BUS_EVENT_SETTINGS={
        '__default__': {
            'is-processing-enabled': True,
            'fetch-delay-if-disabled-ms': 1,
            'fetch-deadline-ms': 1,
            'bulk-max-size': 1,
            'start-retry-sleep-ms': 1,
            'max-retry-sleep-ms': 2000,
            'max-retries': 5,
        },
    },
)
