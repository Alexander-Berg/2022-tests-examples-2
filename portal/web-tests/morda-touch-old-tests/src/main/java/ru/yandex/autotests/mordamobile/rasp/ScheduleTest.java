package ru.yandex.autotests.mordamobile.rasp;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordamobile.data.ScheduleData.SCHEDULE_ICONS;
import static ru.yandex.autotests.mordamobile.data.ScheduleData.TITLE_LINK;


/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Блока расписания")
@Features("Schedule")
@Stories("Appearance")
public class ScheduleTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.scheduleBlock);
    }

    @Test
    public void scheduleTitle() {
        user.shouldSeeLink(homePage.scheduleBlock.title, TITLE_LINK);
    }

    @Test
    public void scheduleLinksSize() {
        user.shouldSeeListWithSize(homePage.scheduleBlock.allItems, equalTo(SCHEDULE_ICONS.size()));
    }

    @Test
    public void scheduleIcon() {
        user.shouldSeeElement(homePage.scheduleBlock.icon);
    }
}
