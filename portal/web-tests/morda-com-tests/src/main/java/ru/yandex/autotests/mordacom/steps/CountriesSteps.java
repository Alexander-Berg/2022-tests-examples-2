package ru.yandex.autotests.mordacom.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.qatools.allure.annotations.Step;

import static org.junit.Assert.fail;
import static ru.yandex.autotests.mordacom.data.CountriesData.CountryInfo;
import static ru.yandex.autotests.mordacom.pages.CountriesBlock.CountryItem;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: eoff
 * Date: 20.11.12
 */
public class CountriesSteps {
    private WebDriver driver;
    private HomePage homePage;
    public CommonMordaSteps user;

    public CountriesSteps(WebDriver driver) {
        this.driver = driver;
        user = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public void shouldSeeCountryLink(CountryInfo country) {
        CountryItem item = findCountryLinkInSelect(country);
        if (item != null) {
            user.shouldSeeElement(item.countryText);
            user.shouldSeeElement(item.countryImg);
            user.shouldSeeElementMatchingTo(item.countryImg, hasAttribute(SRC, country.img));
            user.shouldSeeLink(item, country);
        }
    }

    @Step
    public CountryItem findCountryLinkInSelect(LinkInfo country) {
        for (CountryItem item : homePage.countriesBlock.allItems) {
            if (hasText(country.text).matches(item)) {
                return item;
            }
        }
        fail("Ссылка на " + country.text + " не найдена");
        return null;
    }
}
