package ru.yandex.autotests.morda.tests;

import org.apache.log4j.Logger;
import org.junit.Rule;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/08/16
 */
public abstract class BaseSearchApiTest {
    protected final Logger LOGGER = Logger.getLogger(this.getClass());
    protected static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();
//
//    protected SearchApiRequest request;
//    protected SearchApiChecker checker;
//
//    public BaseSearchApiTest(SearchApiRequest request) {
//        this.request = request;
//        this.checker = SearchApiChecker.getChecker(request);
//    }
//
//    @Test
//    @Stories(SCHEMA)
//    public void schema() throws Exception {
//        Response response = request
//                .readAsResponse();
//
//        checker.checkJsonSchema(response);
//    }
//
//    @Test
//    @Stories("block")
//    public void block() throws Exception {
//        MordaSearchApiResponse response = request
//                .withGeo(region)
//                .withLanguage(language)
//                .read();
//
//        checker.check(response);
//    }
//
//    @Test
//    @Stories("coords")
//    public void coords() throws Exception {
//        MordaSearchApiResponse response = request
//                .withCoords(region)
//                .withLanguage(language)
//                .read();
//
//        checker.check(response);
//    }
//
//    @Test
//    @Stories(PING_LINKS)
//    public void pingLinks() throws Exception {
//        assumeTrue("Disabled pings with config", CONFIG.isToPing());
//        MordaSearchApiResponse response = request
//                .withGeo(region)
//                .withLanguage(language)
//                .read();
//
//        checker.pingLinks(response, region, language);
//    }
}
