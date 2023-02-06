GET_CONTRACTOR_IDS_FROM_QUEUE = """
    SELECT contractor_id
    FROM contractors.processing_queue
    ORDER BY contractor_id
"""

GET_CONTRACTOR_IDS_WITH_REVISION_FROM_QUEUE = """
    SELECT contractor_id, revision
    FROM contractors.processing_queue
    ORDER BY contractor_id
"""

GET_CONTRACTOR_IDS_WITH_TS_FROM_QUEUE = """
    SELECT contractor_id, source_event_timestamp
    FROM contractors.processing_queue
    ORDER BY contractor_id
"""

GET_PROFILES_WITH_UDID = """
    SELECT id, park_id, profile_id, unique_driver_id
    FROM contractors.profiles
    ORDER BY park_id, profile_id
"""

GET_PROFILES_WITH_CARID = """
    SELECT id, park_id, profile_id, car_id
    FROM contractors.profiles
    ORDER BY park_id, profile_id
"""

GET_REVISIONS = """
    SELECT target, revision
    FROM state.revisions
    ORDER BY target
"""
