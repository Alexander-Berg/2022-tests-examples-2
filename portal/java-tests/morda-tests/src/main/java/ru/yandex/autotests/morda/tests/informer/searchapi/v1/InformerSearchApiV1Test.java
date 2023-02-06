package ru.yandex.autotests.morda.tests.informer.searchapi.v1;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.qatools.allure.annotations.Features;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = MordaTestTags.INFORMER)
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V1, MordaTestTags.INFORMER})
@RunWith(Parameterized.class)
public class InformerSearchApiV1Test {//extends BaseSearchApiTest {

//    public InformerSearchApiV1Test(GeobaseRegion region, MordaLanguage language) {
//        super(V1, INFORMER, region, language);
//    }
//
//    @Parameterized.Parameters(name = "{0}, {1}")
//    public static Collection<Object[]> data() {
//        return new InformerSearchApiCasesProvider(CONFIG.pages().getEnvironment())
//                .getTestCases(CONFIG.getTestMode());
//    }
}
