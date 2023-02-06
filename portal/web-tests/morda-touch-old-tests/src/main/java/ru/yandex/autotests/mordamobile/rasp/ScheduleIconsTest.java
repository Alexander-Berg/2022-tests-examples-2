package ru.yandex.autotests.mordamobile.rasp;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.mordamobile.steps.ScheduleSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mordamobile.data.ScheduleData.SCHEDULE_ICONS;
import static ru.yandex.autotests.mordamobile.data.ScheduleData.ScheduleInfo;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;


/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Блок расписания")
@RunWith(Parameterized.class)
@Features("Schedule")
@Stories("Links")
public class ScheduleIconsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ScheduleSteps userSchedule = new ScheduleSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return convert(SCHEDULE_ICONS);
    }

    private ScheduleInfo scheduleInfo;

    public ScheduleIconsTest(ScheduleInfo scheduleInfo) {
        this.scheduleInfo = scheduleInfo;
    }

    @Before
    public void setUp() throws Exception {
        user.opensPage(CONFIG.getBaseURL());
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        user.shouldSeeElement(homePage.scheduleBlock);
    }

    @Test
    public void scheduleItemLink() {
        userSchedule.shouldSeeScheduleItem(scheduleInfo);
    }
}
