package ru.yandex.autotests.mordamobile.searchform;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.mordamobile.pages.TunePage;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mordamobile.data.SearchData.REQUEST_DATA;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Саджест")
@RunWith(Parameterized.class)
@Features("Search")
@Stories("Suggest")
public class SuggestTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);
    private TunePage tunePage = new TunePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(REQUEST_DATA);
    }

    private String text;

    public SuggestTest(String text) {
        this.text = text;
    }

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
    }

    @Test
    public void suggestAppears() {
        user.shouldSeeElement(homePage.searchBlock.input);
        user.entersTextInInput(homePage.searchBlock.input, text);
        user.shouldSeeElement(homePage.searchBlock.suggest);
        user.clearsInput(homePage.searchBlock.input);
        user.clicksOn(homePage.searchBlock.input);
        user.shouldNotSeeElement(homePage.searchBlock.suggest);
    }
}
