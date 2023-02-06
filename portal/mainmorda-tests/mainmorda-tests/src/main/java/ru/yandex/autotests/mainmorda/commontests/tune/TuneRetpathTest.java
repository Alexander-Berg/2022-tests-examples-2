package ru.yandex.autotests.mainmorda.commontests.tune;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TuneData;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.TuneSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

/**
 * User: eoff
 * Date: 29.01.13
 */
@Aqua.Test(title = "Проверка установки региона в в tune")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Tune"})
@Stories("Retpath")
public class TuneRetpathTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private TuneSteps userTune = new TuneSteps(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(TuneData.DOMAINS);
    }

    private Domain domain;

    public TuneRetpathTest(Domain domain) {
        this.domain = domain;
    }

    @Before
    public void setUp() {
        user.opensPage(TuneData.YANDEX_RU);
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        user.setsLanguage(CONFIG.getLang());
    }

    @Test
    public void changeCity() {
        userTune.setRegion(CONFIG.getBaseDomain(), domain);
        userTune.setRegion(domain, CONFIG.getBaseDomain());
    }
}
