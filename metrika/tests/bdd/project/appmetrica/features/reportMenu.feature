Feature: Report menu
    Background:
        Given Authorize as 'yndx-robot-metrika-test'

    Scenario: Open a report
        When I open the app 'Yandex.Metro (Production)'
        Then I see an 'Аудитория' report
        And I see 5 reports

    Scenario: I open report by name
        Given I open reports for 2 application id
        When I click 'Когортный анализ' report
        Then I see an 'Когортный анализ' report

    Scenario Outline: Reports menu has several group of reports <appId>
        Given I open reports for <appId> application id
        Then I see <reports> reports
        And I see <reportGroups> report groups

        Examples:
            | appId | reports | reportGroups |
            |     2 |       5 |            1 |
            | 28210 |      31 |            6 |
