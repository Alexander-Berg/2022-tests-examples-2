Feature: Apps at application list
    Background:
        Given Authorize as 'yndx-robot-metrika-test'

    Scenario: Find an unexisting App
        When I search 'Wrong' app
        Then I see 'Нет совпадений' in the search result

    Scenario: Find an existing App
        When I search 'Yandex.Metro (Production)' app
        Then I see 'Yandex.Metro (Production)' in the app list
        And I see 'Yandex.Metro (Production)' in the search result
