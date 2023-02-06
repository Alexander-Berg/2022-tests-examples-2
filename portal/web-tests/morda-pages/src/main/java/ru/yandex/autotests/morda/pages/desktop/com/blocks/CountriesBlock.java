package ru.yandex.autotests.morda.pages.desktop.com.blocks;

import org.hamcrest.CoreMatchers;
import org.hamcrest.Matcher;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.ImageLink;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.CoreMatchers.startsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_BE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_KK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_RU;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_TR;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.WORLDWIDE_UK;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: asamar
 * Date: 25.09.2015.
 */
@Name("Блок стран")
@FindBy(xpath = "//div[contains(@class, 'b-line b-line__worldwide')]")
public class CountriesBlock extends HtmlElement implements Validateable<DesktopComMorda> {

    private static final String HTTP_WWW_YANDEX_RU = "https://yandex.ru/";
    private static final String YANDEX_RU_IMG = "https://yastatic.net/lego/_/Spb22l3caaD3xN3g-_nuzdnS2FA.png";

    private static final String HTTP_WWW_YANDEX_BY = "https://yandex.by/";
    private static final String YANDEX_BY_IMG = "https://yastatic.net/lego/_/O-tmndNZfQ0UH_3x69kKVSzOLpY.png";

    private static final String HTTP_WWW_YANDEX_UA = "https://yandex.ua/";
    private static final String YANDEX_UA_IMG = "https://yastatic.net/lego/_/QaG3XxXylZ5KP1AZC_bZ0nO3u5M.png";

    private static final String HTTP_WWW_YANDEX_KZ = "https://yandex.kz/";
    private static final String YANDEX_KZ_IMG = "https://yastatic.net/lego/_/uzZ71PWcVXtsIkeTuwAakheaPOY.png";

    private static final String HTTP_WWW_YANDEX_COM_TR = "https://yandex.com.tr/";
    private static final String YANDEX_COM_TR_IMG = "https://yastatic.net/lego/_/WEqF7-mdxlQe_LncWQpTHfzqEeE.png";

    @Name("Текст 'Yandex in'")
    @FindBy(xpath = ".//span[contains(@class, 'worldwide__title')]")
    public HtmlElement yandexInText;

    @Name("Ссылки на страны")
    @FindBy(xpath = ".//span[contains(@class, 'worldwide__list')]//a")
    public List<ImageLink> allItems;

    @Override
    @Step("Check countries block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateYandexIn(yandexInText, validator),
                        validateCountries(allItems, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateYandexIn(HtmlElement yandexIn, Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(yandexIn))
                .check(
                        shouldSeeElementMatchingTo(yandexIn,
                                hasText(getTranslation(WORLDWIDE_TITLE, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateCountries(List<ImageLink> allItems, Validator<? extends DesktopComMorda> validator) {

        List<CountryInfo> countryInfos = new ArrayList<>();
        countryInfos.add(new CountryInfo(
                WORLDWIDE_RU, validator.getMorda().getLanguage(),
                startsWith(HTTP_WWW_YANDEX_RU),
                equalTo(YANDEX_RU_IMG)
        ));
        countryInfos.add(new CountryInfo(
                WORLDWIDE_UK, validator.getMorda().getLanguage(),
                startsWith(HTTP_WWW_YANDEX_UA),
                CoreMatchers.equalTo(YANDEX_UA_IMG)
        ));
        countryInfos.add(new CountryInfo(
                WORLDWIDE_BE, validator.getMorda().getLanguage(),
                startsWith(HTTP_WWW_YANDEX_BY),
                CoreMatchers.equalTo(YANDEX_BY_IMG)
        ));
        countryInfos.add(new CountryInfo(
                WORLDWIDE_KK, validator.getMorda().getLanguage(),
                startsWith(HTTP_WWW_YANDEX_KZ),
                CoreMatchers.equalTo(YANDEX_KZ_IMG)
        ));
        countryInfos.add(new CountryInfo(
                WORLDWIDE_TR, validator.getMorda().getLanguage(),
                startsWith(HTTP_WWW_YANDEX_COM_TR),
                CoreMatchers.equalTo(YANDEX_COM_TR_IMG)
        ));

        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(allItems.size(), countryInfos.size()); i++) {
            collector.check(validateCountry(allItems.get(i), countryInfos.get(i), validator));
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(allItems, hasSize(countryInfos.size()))
        );
        collector.check(countCollector);

        return collector;
    }

    @Step("Check counrty \"{0}\"")
    public static HierarchicalErrorCollector validateCountry(ImageLink imageLink, CountryInfo countryInfo, Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(imageLink))
                .check(
                        shouldSeeElementMatchingTo(imageLink,
                                allOfDetailed(
                                        hasAttribute(HREF, countryInfo.url),
                                        hasText(countryInfo.text))),
                        shouldSeeElementMatchingTo(imageLink.img,
                                hasAttribute(SRC, countryInfo.img))
                );
    }

    public static class CountryInfo extends LinkInfo {
        public Matcher<String> img;

        public CountryInfo(TextID textID, Language language, Matcher<String> url, Matcher<String> img) {
            super(CoreMatchers.equalTo(getTranslation(textID, language)), url);
            this.img = img;
        }

        @Override
        public String toString() {
            return text.toString();
        }
    }

}
