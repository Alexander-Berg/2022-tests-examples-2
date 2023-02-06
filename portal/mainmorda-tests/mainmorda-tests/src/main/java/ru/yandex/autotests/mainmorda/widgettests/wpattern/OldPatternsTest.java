package ru.yandex.autotests.mainmorda.widgettests.wpattern;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PatternsSteps;
import ru.yandex.autotests.mainmorda.steps.SkinsSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mainmorda.utils.PatternInfo;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.PatternsData.OLD_PATTERNS_LIST;
import static ru.yandex.autotests.mainmorda.data.PatternsData.RU_URL;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: alex89
 * Date: 28.01.13
 * 1)Проверка установки старых паттернов для настроенных логинов
 * 2)Установка скина не приводит к падению морды
 */
@Aqua.Test(title = "Проверка установки старых паттернов для настроенных логинов")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Pattern"})
@Stories("Old Pattern")
public class OldPatternsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private PatternsSteps userPattern = new PatternsSteps(driver);
    private SkinsSteps userSkins = new SkinsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(OLD_PATTERNS_LIST);
    }

    private PatternInfo patternInfo;

    public OldPatternsTest(PatternInfo patternInfo) {
        this.patternInfo = patternInfo;
    }

    @Before
    public void before() {
        user.initTest(RU_URL, MOSCOW, CONFIG.getLang());
        user.logsInAs(patternInfo.getLogin(), RU_URL);
    }

    @Test
    public void oldPatternWasSaved() {
        userMode.shouldSeeWidgetMode();
        userSkins.shouldSeeSkin(patternInfo.getSkinId());
        userWidget.shouldSeeWidgets(patternInfo.getWidgets());
        userPattern.shouldSeeThatSomeImportantMordaElementsArePresent();
    }
}
