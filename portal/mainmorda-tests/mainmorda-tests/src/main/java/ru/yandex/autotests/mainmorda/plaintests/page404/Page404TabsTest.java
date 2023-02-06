package ru.yandex.autotests.mainmorda.plaintests.page404;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.Page404;
import ru.yandex.autotests.mainmorda.steps.TabSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.not;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.mainmorda.data.Page404Data.PAGE_404_URL;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
@Aqua.Test(title = "Табы на странице 404")
//@RunWith(Parameterized.class)
@Features({"Main", "Plain", "Page 404"})
@Stories("Tabs")
public class Page404TabsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private TabSteps userTabs = new TabSteps(driver);
    private Page404 page404 = new Page404(driver);

//    @Parameterized.Parameters(name = "{0}")
//    public static Collection<Object[]> testData() {
//        return ParametrizationConverter.convert(TABS_PAGE_404);
//    }

//    public Page404TabsTest(TabInfo tab) {
//        this.tab = tab;
//    }

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.opensPage(PAGE_404_URL);
    }

    @Test
    public void tabs() {
        for (Page404.Page404Service service : page404.services) {
            user.shouldSeeElement(service);
            user.shouldSeeElement(service.icon);
            user.shouldSeeElement(service.serviceName);
            user.shouldSeeElementWithText(service.serviceName, not(isEmptyOrNullString()));
            user.shouldSeeElement(service.serviceSign);
            user.shouldSeeElementWithText(service.serviceSign, not(isEmptyOrNullString()));
        }
    }
}
