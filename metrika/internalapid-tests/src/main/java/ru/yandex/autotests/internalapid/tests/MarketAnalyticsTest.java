package ru.yandex.autotests.internalapid.tests;

import ru.yandex.qatools.allure.annotations.Title;

@Title("Тесты ручек Маркет.Аналитики")
public class MarketAnalyticsTest extends InternalApidTest {

//    @Test
//    @Ignore("Нужно либо замокать blackbox, либо брать только UID'ы, существующие в проде. uid'ы, отсутствующие в blackbox internalapid игнорирует")
//    @Title("Тест ручки /market_analytics/check_access") //https://st.yandex-team.ru/METR-33760
//    public void testCounterAccess() {
//        Map<String, List<MarketAnalyticsCheckAccessResponse>> body = new HashMap<>();
//        List<Long> allUids = new ArrayList<>(Users.allByUid.keySet());
//        List<MarketAnalyticsCheckAccessResponse> request = Counters.allCounters.stream()
//                .map(Counter::getId)
//                .map(it -> new MarketAnalyticsCheckAccessResponse(it, allUids))
//                .limit(1)
//                .collect(Collectors.toList());
//        body.put("request", request);
//
//        ListResponse<MarketAnalyticsCheckAccessResponse> response = userSteps.onInternalApidSteps().getCheckAccess(body);
//        System.out.println(response);
//    }
}
