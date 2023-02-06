package ru.yandex.autotests.mainmorda.widgettests.rates;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.RatesData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.RatesSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 27.04.12
 * Проверяет корректное наличие и переводы текстов:
 * Котировки/Наличные курсы, Сегодня/покупка, Завтра/продажа.
 * Работает пока только для русского языка и столиц доменов.
 */
@Aqua.Test(title = "Заголовки котировок")
@Features({"Main", "Widget", "Rates Block"})
@Stories("Texts")
public class RatesTextsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private RatesSteps userRates = new RatesSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userWidget.addWidget("_stocks");
        user.shouldSeeElement(mainPage.ratesBlock);
    }

    @Test
    public void ratesTexts() {
        user.shouldSeeElement(mainPage.ratesBlock.today);
        user.shouldSeeElementWithText(mainPage.ratesBlock.today, RatesData.TODAY_SELL_TEXT);
        userRates.tomorrowText();
    }

    @Test
    public void ratesNumeralsForTodayAreCorrect() {
        userRates.shouldSeeRateNumerals();
    }
}