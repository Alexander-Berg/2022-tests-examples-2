package ru.yandex.autotests.widgets.url;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.Properties;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.autotests.widgets.steps.WidgetSteps;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.widgets.data.SearchData.URL_REQUESTS;

/**
 * User: leonsabr
 * Date: 09.12.11
 */
@Aqua.Test(title = "Поиск по url")
@Features("Search By URL")
@RunWith(Parameterized.class)
public class UrlSearchTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return convert(URL_REQUESTS);
    }

    private String urlRequest;
    private String expectedUrl;

    public UrlSearchTest(String urlRequest, String expectedUrl) {
        this.urlRequest = urlRequest;
        this.expectedUrl = expectedUrl;
    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }

    @Test
    public void urlPassedInWidgets() {
        user.opensPage(CONFIG.getBaseURL() + "/?url=" + urlRequest);
        user.shouldSeeListWithSize(widgetPage.allWidgets, greaterThan(0));
        user.shouldSeeListWithSize(widgetPage.allWidgetUrls,
                equalTo(widgetPage.allWidgets.size()));
        userWidget.shouldSeeWidgetLinks(widgetPage.allWidgetUrls, containsString(expectedUrl));

    }
}
