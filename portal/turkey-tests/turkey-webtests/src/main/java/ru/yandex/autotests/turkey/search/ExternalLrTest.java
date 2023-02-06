package ru.yandex.autotests.turkey.search;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.steps.SearchSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.turkey.data.SearchData.EXTERNAL_TURKEY_LR;
import static ru.yandex.autotests.turkey.data.SearchData.LR_EXTERNAL_URL_MATCHER;
import static ru.yandex.autotests.turkey.data.SearchData.SEARCH_REQUEST;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.exists;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
@Aqua.Test(title = "lr по умолчанию")
@Features("Search")
@Stories("External lr")
public class ExternalLrTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private SearchSteps userSearch = new SearchSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
    }

    @Test
    public void externalUserShouldSeeDefaultLr() {
        user.shouldSeeElementMatchingTo(yandexComTrPage.search.lr, exists());
        user.shouldSeeElementMatchingTo(yandexComTrPage.search.lr,
                hasAttribute(HtmlAttribute.VALUE, equalTo(EXTERNAL_TURKEY_LR)));
        userSearch.searchFor(SEARCH_REQUEST);
        user.shouldSeePage(LR_EXTERNAL_URL_MATCHER);
    }
}
