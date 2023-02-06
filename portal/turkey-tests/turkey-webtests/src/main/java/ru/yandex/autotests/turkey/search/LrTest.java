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
import ru.yandex.autotests.turkey.data.SearchData;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.steps.SearchSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.turkey.data.SearchData.SEARCH_REQUEST;
import static ru.yandex.autotests.turkey.data.SearchData.getLrUrlMatcher;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.exists;

/**
 * User: leonsabr
 * Date: 08.10.12
 */
@Aqua.Test(title = "Параметр lr")
@RunWith(Parameterized.class)
@Features("Search")
@Stories("Lr")
public class LrTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private SearchSteps userSearch = new SearchSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(SearchData.LR_TEST_DATA);
    }

    private Region region;

    public LrTest(Region region) {
        this.region = region;
    }

    @Test
    public void lrDependsOnRegion() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(region);
        user.shouldSeeElementMatchingTo(yandexComTrPage.search.lr, exists());
        userSearch.searchFor(SEARCH_REQUEST);
        user.shouldSeePage(getLrUrlMatcher(region));
    }
}
