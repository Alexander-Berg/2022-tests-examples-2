package ru.yandex.autotests.widgets.sid;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.widgets.Properties;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.autotests.widgets.rule.UriInterceptor;
import ru.yandex.autotests.widgets.steps.SidSteps;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.List;

import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.RequestInterceptorAction.addRequestInterceptor;
import static ru.yandex.autotests.widgets.data.SidData.CLCK_HOST;
import static ru.yandex.autotests.widgets.data.SidData.MAIN_URL;

/**
 * Наличие sid'а в каталоге виджетов<br>
 * По мотивам HOME-7897
 */
@Aqua.Test(title = "Sid на ссылках каталога")
@Features("Sid")
public class SidTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule rule() {
        return mordaAllureBaseRule.withProxyAction(addRequestInterceptor(uriInterceptor));
    }

    private UriInterceptor uriInterceptor = new UriInterceptor(CLCK_HOST);
    private MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule(DesiredCapabilities.chrome());
    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);
    private SidSteps userSid = new SidSteps(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        uriInterceptor.resetUri();
    }

    @Test
    public void categorySid() {
        List<WidgetPage.CategoryElement> categories = widgetPage.allCategories;
        userSid.clicksOnRandomElementIn(categories.subList(1, categories.size()));
        user.shouldSeePage(startsWith(CONFIG.getBaseURL()));
        userSid.shouldSeeSidInUrl(uriInterceptor.getUriList());
    }

    @Test
    public void tagSid() {
        userSid.clicksOnRandomElementIn(widgetPage.allTags);
        user.shouldSeePage(startsWith(CONFIG.getBaseURL()));
        userSid.shouldSeeSidInUrl(uriInterceptor.getUriList());
    }

    @Test
    public void nextPageButtonSid() {
        user.clicksOn(widgetPage.nextPageButton);
        user.shouldSeePage(startsWith(CONFIG.getBaseURL()));
        userSid.shouldSeeSidInUrl(uriInterceptor.getUriList());
    }

    @Test
    public void widgetItemLinkSid() {
        userSid.clicksOnRandomElementIn(widgetPage.allWidgetLinks);
        user.shouldSeePage(startsWith(MAIN_URL));
        userSid.shouldSeeSidInUrl(uriInterceptor.getUriList());
    }
}
