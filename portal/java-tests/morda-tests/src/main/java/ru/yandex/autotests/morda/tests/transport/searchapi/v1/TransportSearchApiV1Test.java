package ru.yandex.autotests.morda.tests.transport.searchapi.v1;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.qatools.allure.annotations.Features;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = MordaTestTags.TRANSPORT)
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V1, MordaTestTags.TRANSPORT})
@RunWith(Parameterized.class)
public class TransportSearchApiV1Test {//extends BaseSearchApiTest {

//    public TransportSearchApiV1Test(GeobaseRegion region, MordaLanguage language) {
//        super(V1, TRANSPORT, region, language);
//    }
//
//    @Parameterized.Parameters(name = "{0}, {1}")
//    public static Collection<Object[]> data() {
//        return new TransportSearchApiCasesProvider(CONFIG.pages().getEnvironment())
//                .getTestCases(CONFIG.getTestMode());
//    }

}
