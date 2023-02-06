package ru.yandex.autotests.turkey.search;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.turkey.data.SearchData.FAMILY_SEARCH_PARAMETER_MATCHER;
import static ru.yandex.autotests.turkey.data.SearchData.FAMILY_SEARCH_URL;
import static ru.yandex.autotests.turkey.data.SearchData.SEARCH_REQUEST;

/**
 * User: ivannik
 * Date: 24.06.13
 * Time: 17:09
 */
@Aqua.Test(title = "Проброс параметра family в серп при запросе")
@Features("Search")
@Stories("Family Request")
public class FamilyParameterTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Before
    public void setUp() {
        user.opensPage(FAMILY_SEARCH_URL);
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
    }

    @Test
    public void familyParameterThrown() {
        user.shouldSeeElement(yandexComTrPage.search.input);
        user.entersTextInInput(yandexComTrPage.search.input, SEARCH_REQUEST);
        user.clicksOn(yandexComTrPage.search.submit);
        user.shouldSeePage(FAMILY_SEARCH_PARAMETER_MATCHER);
    }
}
