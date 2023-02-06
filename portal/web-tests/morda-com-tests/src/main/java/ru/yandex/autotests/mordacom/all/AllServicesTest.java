package ru.yandex.autotests.mordacom.all;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

/**
 * User: leonsabr
 * Date: 26.01.12
 * Открытие www.yandex.com/all должно корректно редиректить на морду.
 */
@Aqua.Test(title = "Редирект /all на морду")
@Features("All Services")
@RunWith(Parameterized.class)
public class AllServicesTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(CONFIG.getMordaComLangs());
    }

    private final Language language;

    public AllServicesTest(Language language) {
        this.language = language;
    }

    @Test
    public void allRedirect() throws InterruptedException {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.opensPage(CONFIG.getBaseURL() + "/all", CONFIG.getBaseURL());
    }
}
