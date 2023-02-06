package ru.yandex.autotests.turkey.search;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.SerpComTrPage;
import ru.yandex.autotests.turkey.steps.SearchSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.turkey.data.SearchData.SEARCH_TEST_DATA;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
@Aqua.Test(title = "Проброс запроса в поиск")
@RunWith(Parameterized.class)
@Features("Search")
@Stories("Request")
public class SearchTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private SearchSteps userSearch = new SearchSteps(driver);
    private SerpComTrPage serpComTrPage = new SerpComTrPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(SEARCH_TEST_DATA);
    }

    private String request;

    public SearchTest(String request) {
        this.request = request;
    }

    @Test
    public void requestIsThrownInSerp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        userSearch.searchFor(request);
        user.shouldSeeInputWithText(serpComTrPage.arrow.input, request);
    }
}
