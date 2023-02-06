package ru.yandex.autotests.mainmorda.widgettests.wpattern;


import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.PatternsSteps;
import ru.yandex.autotests.mainmorda.steps.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.CoordinatesData.MDA_DOMAINS;
import static ru.yandex.autotests.mainmorda.data.PatternsData.OLD_PATTERNS_LIST;
import static ru.yandex.autotests.mainmorda.data.PatternsData.RU_URL;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: alex89
 * Date: 10.12.12
 * Копирование паттерна при МДА редиректе в домены .ua, .by, .kz
 */

@Aqua.Test(title = "Копирование/некопирование паттерна при редиректах")
@Features({"Main", "Widget", "Pattern"})
@Stories("Pattern Copy")
public class PatternCopyTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private WidgetSteps userWidget = new WidgetSteps(driver);
    private PatternsSteps userPattern = new PatternsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(OLD_PATTERNS_LIST);
    }

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        user.logsInAs(mordaAllureBaseRule.getUser(DEFAULT, Mode.WIDGET),
                CONFIG.getBaseURL());
    }

    /**
     * 1. Без залогинивания: если посещали национальные домены, то паттерн не копируется из .ru
     */
    @Test
    public void doNotCopyPatternToResetDomains() throws InterruptedException {
        userPattern.resetSettingsInAllDomains();
        user.setsRegion(MOSCOW);
        userPattern.setPattern(RU_URL);
        userPattern.shouldNotSeeSavedPatternInMdaDomains();
    }

    /**
     * 3. Под незалогином: если паттерн в домене настроен, то он не копируется из .ru
     */
    @Test
    public void doNotCopyPatternToDomainsWithOldPatterns() {
        userPattern.setWidgetModeInMdaDomains();
        user.setsRegion(MOSCOW);
        userPattern.setPattern(RU_URL);
        userPattern.shouldNotSeeSavedPatternInMdaDomains();
    }

    /**
     * 4. При добавлении виджета на *.yandex.ru происходит редирект в национальный домен
     */
    @Test
    public void redirectWhileAddingWidget() {
        for (Domain domain : MDA_DOMAINS) {
            user.setsRegion(domain.getCapital(), "");
            userPattern.addLentaRuWidgetByUrl(RU_URL + "/?add=28");
            user.shouldSeePage(CONFIG.getBaseURL().replace(CONFIG.getBaseDomain().toString(), domain.toString()));
            userWidget.acceptWidgetAddition();
        }
    }
}
