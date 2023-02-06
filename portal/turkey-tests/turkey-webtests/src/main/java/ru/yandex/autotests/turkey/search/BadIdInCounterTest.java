package ru.yandex.autotests.turkey.search;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.steps.YandexUidSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.equalTo;

/**
 * User: ivannik
 * Date: 10.07.13
 * Time: 18:41
 */
@Aqua.Test(title = "Отсутствие элементов с BADID")
@Features("Search")
@Stories("BADID")
public class BadIdInCounterTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private YandexUidSteps userUid = new YandexUidSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        userUid.setsUIDWithCounters();
        user.refreshPage();
    }

    @Test
    public void badIdNotExists() {
        user.shouldSeeListWithSize(yandexComTrPage.elementsWithBadId, equalTo(0));
    }
}
