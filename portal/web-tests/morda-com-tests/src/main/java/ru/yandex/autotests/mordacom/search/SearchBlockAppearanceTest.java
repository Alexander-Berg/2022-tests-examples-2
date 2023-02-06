package ru.yandex.autotests.mordacom.search;

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
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mordacom.data.SearchData.getSearchButtonTextMatcher;

/**
 * User: eoff
 * Date: 28.11.12
 */
@Aqua.Test(title = "Внешний вид блока поиска")
@Features("Search")
@Stories("Appearance")
@RunWith(Parameterized.class)
public class SearchBlockAppearanceTest {
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

    public SearchBlockAppearanceTest(Language language) {
        this.language = language;
    }

    @Test
    public void searchButtonText() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.shouldSeeElement(homePage.search.submit);
        user.shouldSeeElementWithText(homePage.search.submit, getSearchButtonTextMatcher(language));
    }

    @Test
    public void inputField() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.shouldSeeElement(homePage.search.input);
    }
}
