USER_AGENT_HEADER = 'User-Agent'

USER_AGENT_TAXIMETER = 'Taximeter 9.1 (1234)'
USER_AGENT_UBER = 'Taximeter-Uber 9.1 (1234)'


def get_app_family(user_agent):
    return (
        'uberdriver' if user_agent.lower().find('uber') >= 0 else 'taximeter'
    )


def create_session(
        driver_authorizer,
        user_agent: str,
        driver_id: str,
        park_id: str,
        session_id: str,
):
    app_family = get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, session_id, driver_id,
    )
