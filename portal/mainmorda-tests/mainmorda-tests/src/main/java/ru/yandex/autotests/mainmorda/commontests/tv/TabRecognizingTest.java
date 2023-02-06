package ru.yandex.autotests.mainmorda.commontests.tv;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.RatesData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.TvAfishaSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.junit.Assume.assumeFalse;

/**
 * User: alex89
 * Date: 28.02.13
 * Проверка того, что Морда запоминает сделанный выбор предпочтения табов Афиши или ТВ
 */
@Aqua.Test(title = "Запоминание установленного таба")
@Features({"Main", "Common", "TV"})
@Stories("Tab Recognizing")
public class TabRecognizingTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private TvAfishaSteps userTvAfisha = new TvAfishaSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void initLanguage() {
        assumeFalse("Блоки раздельны при заинлайненых котировках",
                RatesData.isInline(CONFIG.getBaseDomain().getCapital()) && CONFIG.getMode().equals(Mode.PLAIN));
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        userTvAfisha.shouldSeeRuUaByDomainForTabTesting();
        user.shouldSeeElement(mainPage.tvBlock);
    }

    @Test
    public void afishaTabIsRecognized() {
        user.shouldSeeElementIsNotSelected(mainPage.tvBlock.afishaTab);
        userTvAfisha.switchesToTab(mainPage.tvBlock.afishaTab);
        user.shouldSeeElementIsSelected(mainPage.tvBlock.afishaTab);
        user.refreshPage();
        user.shouldSeeElementIsSelected(mainPage.tvBlock.afishaTab);
    }

    @Test
    public void afishaTabCanBeForgot() {
        user.shouldSeeElementIsNotSelected(mainPage.tvBlock.afishaTab);
        userTvAfisha.switchesToTab(mainPage.tvBlock.afishaTab);
        user.shouldSeeElementIsSelected(mainPage.tvBlock.afishaTab);
        user.refreshPage();
        user.shouldSeeElementIsSelected(mainPage.tvBlock.afishaTab);
        userTvAfisha.switchesToTab(mainPage.tvBlock.tvTab);
        user.refreshPage();
        user.shouldSeeElementIsNotSelected(mainPage.tvBlock.afishaTab);
    }
}