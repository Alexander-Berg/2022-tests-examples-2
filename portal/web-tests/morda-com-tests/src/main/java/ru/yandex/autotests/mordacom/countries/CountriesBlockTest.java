package ru.yandex.autotests.mordacom.countries;

import org.junit.Before;
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

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacom.data.CountriesData.getCountriesList;
import static ru.yandex.autotests.mordacom.data.CountriesData.getTextYandexInMatcher;

/**
 * User: eoff
 * Date: 20.11.12
 */
@Aqua.Test(title = "Внешний вид блока стран")
@Features("countries Block")
@RunWith(Parameterized.class)
public class CountriesBlockTest {
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

    public CountriesBlockTest(Language language) {
        this.language = language;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
    }

    @Test
    public void countriesNumber() {
        user.shouldSeeElement(homePage.countriesBlock);
        user.shouldSeeListWithSize(homePage.countriesBlock.allItems, equalTo(getCountriesList(language).size()));
    }

    @Test
    public void yandexInText() {
        user.shouldSeeElement(homePage.countriesBlock);
        user.shouldSeeElement(homePage.countriesBlock.yandexInText);
        user.shouldSeeElementWithText(homePage.countriesBlock.yandexInText, getTextYandexInMatcher(language));
    }
}
