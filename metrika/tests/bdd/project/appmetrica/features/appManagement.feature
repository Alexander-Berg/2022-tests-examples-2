Feature: Application management
    Background:
         Given Authorize as 'yndx-robot-metrika-test'

    Scenario: Create application
        Given I open url '/application/new'
        When I create an app with name 'TestApp'
        Then I see 'TestApp' in the app list
        Given I delete an app with name 'TestApp' from the app list
