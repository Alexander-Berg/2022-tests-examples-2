package ru.yandex.autotests.mainmorda.commontests.resources;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.ResourcesSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.lessThan;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.PLAIN;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: leonsabr
 * В коде плоской морды не осталось dev-ресурсов.
 */

@Aqua.Test(title = "Ресурсы с dev-машин")
@Features({"Main", "Common", "Resources"})
public class ResourcesTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private ResourcesSteps userResource = new ResourcesSteps(driver);

    @Before
    public void setUp() {
        userResource.ifNotDev();
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }

    @Test
    public void resources() {
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        userResource.shouldNotSeeDevResources();
    }

    @Test
    public void mordaSize() {
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, WIDGET), CONFIG.getBaseURL());
        userMode.setModeLogged(PLAIN);
        int plainSize = driver.getPageSource().length();
        userMode.setModeLogged(WIDGET);
        int widgetSize = driver.getPageSource().length();
        assertThat(1.0 * widgetSize / plainSize, lessThan(2.0));
    }
}
