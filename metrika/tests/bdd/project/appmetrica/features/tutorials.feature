Feature: Reports tutorial

    Background:
        Given Authorize as 'yndx-robot-metrika-test'

    Scenario Outline: Tutorial <report_name> works
        When I open url '<report_url>'
        And I see <steps> steps tutorial
        And I click '<next_button>' to the last slide
        Then I can close the tutorial by clicking at <last_button>

        Examples:
            |         report_name |                                                                          report_url | steps |  next_button |        last_button |
            |              events |                          /statistic?appId=806976&report=events&enforceTutorial=true |     5 |       Дальше |  'Перейти в отчёт' |
            |             revenue |                         /statistic?appId=284530&report=revenue&enforceTutorial=true |     4 |       Дальше | 'Перейти к отчёту' |
            |  error logs android |   /statistic?appId=806976&report=error-logs-android&sampling=1&enforceTutorial=true |     4 |       Дальше |  'Перейти в отчёт' |
            |          crash logs |                /statistic?appId=1111&report=crash-logs-android&enforceTutorial=true |     4 |       Дальше | 'Перейти к отчёту' |
            |                  UA |                     /statistic?appId=137715&report=campaigns2&&enforceTutorial=true |     5 |       Дальше |  'Перейти в отчёт' |
            |           ecommerce |                        /statistic?appId=23098&report=ecommerce&enforceTutorial=true |     4 |       Дальше |  'Перейти в отчёт' |
