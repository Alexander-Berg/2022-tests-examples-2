package ru.yandex.autotests.mordacom.countries;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacom.steps.CountriesSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacom.data.CountriesData.CountryInfo;
import static ru.yandex.autotests.mordacom.data.CountriesData.getCountriesList;
import static ru.yandex.autotests.utils.morda.auth.User.COM_DEFAULT;

/**
 * User: leonsabr
 * Date: 18.08.2010
 */
@Aqua.Test(title = "Ссылки на страны")
@RunWith(Parameterized.class)
@Features("countries Block")
public class CountriesLinksTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private CountriesSteps userCountries = new CountriesSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> testData() {
        List<Object[]> data = new ArrayList<>();
        for (Language language : CONFIG.getMordaComLangs()) {
            for (CountryInfo country : getCountriesList(language)) {
                data.add(new Object[]{language, country});
            }
        }
        return data;
    }

    private final Language language;
    private final CountryInfo country;

    public CountriesLinksTest(Language language, CountryInfo country) {
        this.language = language;
        this.country = country;
    }

    @Test
    public void countryLinkLogin() {
        user.logsInAs(COM_DEFAULT, CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.shouldSeeElement(homePage.countriesBlock);
        userCountries.shouldSeeCountryLink(country);
    }

    @Test
    public void countryLinkLogoff() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.shouldSeeElement(homePage.countriesBlock);
        userCountries.shouldSeeCountryLink(country);
    }
}
