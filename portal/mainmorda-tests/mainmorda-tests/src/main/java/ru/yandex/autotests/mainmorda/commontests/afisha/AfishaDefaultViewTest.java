package ru.yandex.autotests.mainmorda.commontests.afisha;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TVAfishaData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.TvAfishaSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static org.junit.Assume.assumeTrue;

/**
 * User: alex89
 * Date: 28.02.13
 */
@Aqua.Test(title = "Афиша(вид по-умолчанию)")
@Features({"Main", "Common", "Afisha"})
@Stories("Default View")
public class AfishaDefaultViewTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private TvAfishaSteps userTvAfisha = new TvAfishaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.afishaBlock);
    }

    @Test
    public void afishaTitle() {
        userTvAfisha.shouldSeeAfishaTitle(mainPage.afishaBlock);
    }

    @Test
    public void afishaEvents() {
        user.shouldSeeListWithSize(mainPage.afishaBlock.afishaEvents,
                lessThanOrEqualTo(TVAfishaData.getExpectedNumberOfAfishaEvents()));
        userTvAfisha.shouldSeeAfishaEventsInWidget(mainPage.afishaBlock);
    }

    @Test
    public void afishaPremiere() {
        assumeTrue("Не проверяем наличие премьер после среды", TVAfishaData.isPremiereDay());
        userTvAfisha.shouldSeePremiereInTheMiddleOfWeek(mainPage.afishaBlock);
    }
}
