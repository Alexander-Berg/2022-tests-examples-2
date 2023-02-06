package ru.yandex.autotests.mordacom.logo;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

/**
 * User: eoff
 * Date: 28.11.12
 */
@Aqua.Test(title = "Логотип Яндекса")
@Features("Logo")
@RunWith(Parameterized.class)
public class YandexLogoTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(CONFIG.getMordaComLangs());
    }

    private final Language language;

    public YandexLogoTest(Language language) {
        this.language = language;
    }

    @Test
    public void yandexLogo() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.shouldSeeElement(homePage.yandexLogo);
    }
}
