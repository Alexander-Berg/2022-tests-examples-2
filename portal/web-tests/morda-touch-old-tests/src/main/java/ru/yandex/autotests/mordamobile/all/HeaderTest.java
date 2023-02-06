package ru.yandex.autotests.mordamobile.all;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.AllServicesPage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordamobile.data.AllServicesData.LOGO_LINK;
import static ru.yandex.autotests.mordamobile.data.AllServicesData.MOBILE_APPS_LINK;
import static ru.yandex.autotests.mordamobile.data.AllServicesData.MOBILE_SITES_TEXT_MATCHER;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 05.02.2015.
 */
@Aqua.Test(title = "Header на странице всех сервисов")
@Features("All Services")
@Stories("Header")
public class HeaderTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private AllServicesPage allServicesPage = new AllServicesPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL() + "/all");
    }

    @Test
    public void logo() {
        user.shouldSeeLinkLight(allServicesPage.allServicesPageHeader.logo, LOGO_LINK);
    }

    @Test
    public void mobileAppsLink() {
        user.shouldSeeLinkLight(allServicesPage.allServicesPageHeader.mobileAppsLink, MOBILE_APPS_LINK);
    }

    @Test
    public void mobileSitesText() {
        user.shouldSeeElement(allServicesPage.allServicesPageHeader.mobileSitesText);
        user.shouldSeeElementWithText(allServicesPage.allServicesPageHeader.mobileSitesText, MOBILE_SITES_TEXT_MATCHER);
    }
}
