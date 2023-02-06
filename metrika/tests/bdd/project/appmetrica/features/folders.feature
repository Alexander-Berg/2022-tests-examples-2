Feature: Actions with folders
    Background:
        Given Authorize as 'yndx-robot-metrika-test'

    Scenario: Create and delete folder
        When I create a new folder with name 'SuperFolder'
        And I see a folder with name 'SuperFolder' in the folders list
        And I delete a folder with name 'SuperFolder'
        Then I do not see a folder with name 'SuperFolder'

    Scenario: Click to empty folder and see empty folder report
        Given I create a new folder with name 'EmptyFolder'
        When I click on the empty folder with name 'EmptyFolder'
        Then I see the empty folder report for the folder
        Given I delete a folder with name 'EmptyFolder'

    @createApp
    Scenario: Put and remove application from folder
        #{"appName": "PutToFolder"}
        Given I create a new folder with name 'FolderToPut'
        When I put an app with name 'PutToFolder' from the applist to a folder with name 'FolderToPut'
        And I see the app 'PutToFolder' in a folder with name 'FolderToPut'
        And I remove an app with name 'PutToFolder' from a folder with name 'FolderToPut'
        Then I see 'PutToFolder' in the app list
        And I see a folder with name 'FolderToPut' in the folders list
        Given I delete a folder with name 'FolderToPut'
