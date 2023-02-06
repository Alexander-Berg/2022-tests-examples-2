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
import ru.yandex.autotests.mainmorda.steps.PatternsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.CoordinatesData.KUBR_DOMAINS;
import static ru.yandex.autotests.mainmorda.data.PatternsData.RU_URL;

/**
 * User: alex89
 * Date: 10.12.12
 */

@Aqua.Test(title = "Сохранение паттерна")
@RunWith(Parameterized.class)
@Features({"Main", "Widget", "Pattern"})
@Stories("Pattern Save")
public class PatternSaveTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private PatternsSteps userPattern = new PatternsSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(KUBR_DOMAINS);
    }

    private Domain domain;

    public PatternSaveTest(Domain domain) {
        this.domain = domain;

    }

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), domain.getCapital(), CONFIG.getLang());
    }

    @Test
    public void patternSaves() {
        String url = RU_URL.replace(Domain.RU.toString(), domain.toString());
        userPattern.setPattern(url);
        user.opensPage(url);
        userPattern.shouldSeePattern();
    }
}
