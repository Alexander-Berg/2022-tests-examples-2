package ru.yandex.autotests.morda.pages.desktop.firefox.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.stocksblock.Lite;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;
import java.util.Optional;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldNotSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Информеры")
@FindBy(xpath = "//span[contains(concat(' ',@class,' '), ' informers ')]")
public class InformersBlock extends HtmlElement implements Validateable<DesktopFirefoxMorda> {

    @Name("Ссылка 'Изменить город'")
    @FindBy(xpath = "./span[1]/a")
    private HtmlElement changeCityLink;

    @Name("Информер погоды")
    @FindBy(xpath = "./span[2]/a")
    private WeatherInformer weatherInformer;

    @Name("Информер пробок")
    @FindBy(xpath = "./span/a[.//span[contains(@class,'informers__traffic__text')]]")
    private TrafficInformer trafficInformer;

    @Name("Информеры котировок")
    @FindBy(xpath = "./span/span[contains(@class,'informer__stocks__item')]/*")
    private List<HtmlElement> stocksInformers;

    @Override
    @Step("Check informers")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopFirefoxMorda> validator) {

        HierarchicalErrorCollector collector = collector();
        collector.check(validateChangeCityLink(changeCityLink, validator));
        collector.check(validateWeatherInformer(weatherInformer, validator));
        collector.check(validateTrafficInformer(trafficInformer, validator));

        List<Lite> expectedStocks = validator.getCleanvars().getStocks().getLite();

        for (int i = 0; i != Math.min(stocksInformers.size(), expectedStocks.size()); i++) {
            collector.check(validateStockInformer(stocksInformers.get(i), expectedStocks.get(i), validator));
        }

        HierarchicalErrorCollector informersCollector = collector().check(
                shouldSeeElementMatchingTo(stocksInformers, hasSize(expectedStocks.size()))
        );

        collector.check(informersCollector);

        return collector;
    }

    private String normalize(String scheme, String url) {
        if (url == null) {
            return "";
        } else if (url.startsWith("//")) {
            return scheme + ":" + url;
        }
        return url;
    }

    private String symbol(String code){
        return code.replace("&#128738;","\uD83D\uDEE2");
    }

//    private List<StocksInfo> getStocks(Validator<? extends DesktopFirefoxMorda> validator) {
//        return validator.getCleanvars().getStocks().getLite().stream()
//                .map(lite -> new StocksInfo(
//                                lite.getText(),
//                                normalize(validator.getMorda().getScheme(), lite.getHref()),
//                                r.getData().get(0).getValue().replace(',', '.'),
//                                String.format(
//                                        getTranslation("home", "rates", "newalt." + r.getAlt(), validator.getMorda().getLanguage()),
//                                        r.getText()))
//                )
//                .collect(Collectors.toList());
//    }

    @Step("Check change city link")
    private HierarchicalErrorCollector validateChangeCityLink(HtmlElement changeCityLink,
                                                              Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(shouldSeeElement(changeCityLink))
                .check(
                        shouldSeeElementMatchingTo(changeCityLink, allOfDetailed(
                                        hasText(validator.getCleanvars().getBigCityName()),
                                        hasAttribute(HREF,
                                                startsWith(normalize(validator.getMorda().getScheme(),
                                                        validator.getCleanvars().getSetupURLRegion())
                                                        .replace("&amp;", "&"))),
                                        hasAttribute(TITLE,
                                                equalTo(getTranslation(Dictionary.Home.Head.REGION, validator.getMorda().getLanguage())))
                                )
                        )
                );
    }

    @Step("Check weather informer")
    private HierarchicalErrorCollector validateWeatherInformer(WeatherInformer weatherInformer,
                                                               Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(shouldSeeElement(weatherInformer))
                .check(
                        shouldSeeElementMatchingTo(weatherInformer, allOfDetailed(
                                        hasText(validator.getCleanvars().getWeather().getT1() + " °C"),
                                        hasAttribute(HREF, equalTo(validator.getCleanvars().getWeather().getUrl())),
                                        hasAttribute(TITLE, equalTo(validator.getCleanvars().getWeather().getIconalt()))
                                )
                        )
                )
                .check(
                        shouldSeeElement(weatherInformer.icon),
                        shouldSeeElementMatchingTo(weatherInformer.icon,
                                hasAttribute(CLASS, containsString("b-ico-" + validator.getCleanvars().getWeather().getIv3U1()))
                        )
                );
    }

    @Step("Check traffic informer")
    private HierarchicalErrorCollector validateTrafficInformer(TrafficInformer trafficInformer,
                                                               Validator<? extends DesktopFirefoxMorda> validator) {
        if (validator.getCleanvars().getTraffic().getShow() == 1) {
            return collector()
                    .check(shouldSeeElement(trafficInformer))
                    .check(
                            shouldSeeElementMatchingTo(trafficInformer,
                                    hasAttribute(HREF, equalTo(validator.getCleanvars().getTraffic().getHref()))
                            )
                    )
                    .check(
                            shouldSeeElement(trafficInformer.iconWithRate),
                            shouldSeeElementMatchingTo(trafficInformer.iconWithRate, allOfDetailed(
                                            hasText(String.valueOf(validator.getCleanvars().getTraffic().getRate())),
                                            hasAttribute(CLASS,
                                                    containsString("b-ico-traffic-" + validator.getCleanvars().getTraffic().getClazz()))
                                    )
                            )
                    )
                    .check(
                            shouldSeeElement(trafficInformer.text),
                            shouldSeeElementMatchingTo(trafficInformer.text,
                                    hasText(String.valueOf(validator.getCleanvars().getTraffic().getRateaccus()))
                            )
                    );
        } else {
            return collector()
                    .check(shouldNotSeeElement(trafficInformer));
        }
    }

    @Step("Check stock informer: {1}")
    private HierarchicalErrorCollector validateStockInformer(HtmlElement stockInformer,
                                                             Lite lite,
                                                             Validator<? extends DesktopFirefoxMorda> validator) {
        String alt = Optional.ofNullable(lite.getAlt()).orElse("");


        return collector()
                .check(shouldSeeElement(stockInformer))
                .check(
                        shouldSeeElementMatchingTo(stockInformer, allOfDetailed(
                                        hasText(containsString(symbol(lite.getSymbol()) + lite.getValue())),
                                        hasAttribute(HREF, equalTo(
                                                        normalize(validator.getMorda().getScheme(),
                                                                lite.getHref()))
                                        ),
                                        hasAttribute(TITLE, equalTo(alt))
                                )
                        )
                );
    }

    public static class WeatherInformer extends HtmlElement {

        @Name("Иконка погоды")
        @FindBy(xpath = "//span[contains(@class,'informers__icon')]")
        private HtmlElement icon;
    }

    public static class TrafficInformer extends HtmlElement {

        @Name("Иконка с баллом пробок")
        @FindBy(xpath = "//span[contains(@class,'b-ico-trate')]")
        private HtmlElement iconWithRate;

        @Name("Текст 'баллов'")
        @FindBy(xpath = "//span[contains(@class,'informers__traffic__text')]")
        private HtmlElement text;

    }

    public static class StocksInfo {
        private final String text;
        private final String href;
        private final String ariaLabel;
        private final String title;

        public StocksInfo(String text, String href, String ariaLabel, String title) {
            this.text = text;
            this.href = href;
            this.ariaLabel = ariaLabel;
            this.title = title;
        }

        public String getText() {
            return text;
        }

        public String getHref() {
            return href;
        }

        public String getAriaLabel() {
            return ariaLabel;
        }

        public String getTitle() {
            return title;
        }

        @Override
        public String toString() {
            return title;
        }
    }
}
