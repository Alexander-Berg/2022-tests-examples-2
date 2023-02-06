package ru.yandex.autotests.mainmorda.widgettests.wproperties;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PatternsSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mainmorda.utils.WidgetPattern;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: alex89
 * Date: 07.12.12
 */

@Aqua.Test(title = "Координаты виджетов после настройки и автообновления")
@Features({"Main", "Widget", "Pattern"})
@Stories("Patterns")
public class PatternRebindAfterSetupTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private PatternsSteps userPattern = new PatternsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());

        user.shouldSeeElement(mainPage.teaserBlock);
        user.shouldSeeElement(mainPage.teaserBlock.closeCross);
        user.clicksOn(mainPage.teaserBlock.closeCross);
        user.shouldSeeElement(mainPage.widgetSettingsHeader.undoButton);
        user.clicksOn(mainPage.widgetSettingsHeader.undoButton);
    }

    /**
     * Режим редактирования:настраиваем виджет, ждем автообновления виджетов (320с)
     * Режим редактирования -> Удалили 'teaser' и отменили удаление,  настроили блоги -> дождались автообновления
     */
    @Test
    public void rebindAfterSetup() {
        WidgetPattern workPattern = userPattern.getPatternInEditMode();

        userWidget.editsNewsBlock(workPattern);

        userWidget.updatesAllWidgets();

        userPattern.shouldSeePatternRequest(workPattern);
    }
}
