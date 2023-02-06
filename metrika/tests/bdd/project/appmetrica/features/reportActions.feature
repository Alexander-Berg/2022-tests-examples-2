Feature: Actions with reports
    Background:
        Given Authorize as 'yndx-robot-metrika-test'

   Scenario Outline: Default preset of dimensions and metrics in <report>
       Given I open reports for 185600 application id
       When I click <report> report
       And I see metrics <metrics> picked for report in this order
       Then I see dimensions <dimensions> picked for report in this order
       Examples:
           | report                         | metrics                  | dimensions                  |
           | 'User Acquisition'             | 'UAMetricsRu'            | 'UADimensionsRu'            |
           | 'Remarketing'                  | 'remarketingMetricsRu'   | 'remarketingDimensionsRu'   |
           | 'User Acquisition SKAdNetwork' | 'SKADMetricsRu'          | 'SKADDimensionsRu'          |
           | 'Revenue'                      | 'revenueMetricsRu'       | 'revenueDimensionsRu'       |
           | 'Анализ покупок'               | 'ecommerceMetricsRu'     | 'ecommerceDimensionsRu'     |
           | 'Вовлеченность'                | 'engagementMetricsRu'    | 'engagementDimensionsRu'    |
           | 'События'                      | 'eventsMetricsRu'        | 'eventsDimensionsRu'        |
           | 'Push-кампании'                | 'pushCampaignsMetricsRu' | 'pushCampaignsDimensionsRu' |


   Scenario: Adding dimensions to report
      Given I open reports for 185600 application id
      Given I click 'User Acquisition' report
      When I add dimensions 'Континент; Страна; Округ; Пол; Возраст; Тип установки; День; Неделя'
      Then I see 10 dimensions in the picked dimensions list

   Scenario: Max count of dimensions to pick
       Given I open reports for 2 application id
       Given I click 'User Acquisition' report
       When I add dimensions 'Континент; Страна; Округ; Пол; Возраст; Тип установки; День; Неделя'
       Then  I can not add eleventh dimension to report

   Scenario: Deleting dimensions from report
       Given I open url '/statistic?appId=2&report=campaigns2'
       When I delete dimensions 'Партнёры'
       Then I see dimensions 'Трекеры' picked for report in this order

   Scenario: Actions with list table view
       Given I open url '/statistic?appId=2&report=campaigns2'
       Given I add dimensions 'Континент; Пол; Возраст'
       When I click on the dimension cell repeatedly to the last dimension cell in the list
       And I see 4 previously clicked dimension cells in the breadcrumbs
       And I click to the last link in the breadcrumbs
       Then I see a dimension cell with name 'Женский'


   Scenario: Actions with driildown table view
       Given I open url '/statistic?appId=2&report=campaigns2'
       Given I add dimensions 'Тип установки; День'
       When I click to the drilldown table view button
       And I click on expand button at the 1 dimension cell for each level to last level of the table
       And I see 7 rows of data in the last level of the table
       And I click on reduce button at the 1 dimension cell for each level from last to parent level of the table
       Then I see 1 rows of data in the table

   Scenario: Adding a metric by event with specified event
       Given I open url '/statistic?appId=806979&report=campaigns2'
       When I add metric 'Количество событий' with the event 'AppTheme'
       Then I see the 'Количество событий' metric as a table column

