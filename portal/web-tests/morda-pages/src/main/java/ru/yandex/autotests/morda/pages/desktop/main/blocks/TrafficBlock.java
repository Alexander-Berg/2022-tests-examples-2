package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.traffic.Future;
import ru.yandex.autotests.mordabackend.beans.traffic.Traffic;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static java.lang.String.valueOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TrafficBlock.TrafficForecast.TrafficForecastItem.validateForecastItem;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TrafficBlock.TrafficForecast.validateForecast;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.TrafficBlock.TrafficHeader.validateHeader;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldNotSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TRAFFIC_FORECAST;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasClass;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Пробки")
@FindBy(xpath = "//div[contains(@id,'wd-wrapper-_traffic')]")
public class TrafficBlock extends Widget<TrafficSettingsBlock> implements Validateable<DesktopMainMorda> {

    public TrafficHeader title;
    public TrafficForecast forecast;

    @Name("Маршрут домой/на работу")
    @FindBy(xpath = ".//div[contains(@class, 'route_to_home')]")
    public HtmlElement route;

    @Name("Описание пробок")
    @FindBy(xpath = ".//a[contains(@class, 'traffic__informer-link')]")
    public HtmlElement description;

    public TrafficSettingsBlock trafficSettingsBlock;

    @Override
    protected TrafficSettingsBlock getSetupPopup() {
        return trafficSettingsBlock;
    }


    @Step("{0}")
    public static HierarchicalErrorCollector validateDescription(HtmlElement description,
                                                                 Validator<? extends DesktopMainMorda> validator) {

        Traffic trafficData = validator.getCleanvars().getTraffic();
//        if (trafficData.getDescr() == null || trafficData.getDescr().isEmpty() || trafficData.getFuture().size() > 0) {
//            return collector()
//                    .check(shouldNotSeeElement(description));
//        }

        HierarchicalErrorCollector collector = collector();


        if (trafficData.getDescr() != null && trafficData.getFuture() == null) {
            return collector
                    .check(shouldSeeElement(description))
                    .check(
                            shouldSeeElementMatchingTo(description, allOfDetailed(
                                    hasText(trafficData.getDescr()),
                                    hasAttribute(HREF, equalTo(
                                            url(trafficData.getHref(), validator.getMorda().getScheme())
                                                    .replace("&amp;", "&")))
                            ))
                    );
        }

        if (trafficData.getInformer() != null) {
            return collector
                    .check(shouldSeeElement(description))
                    .check(
                            shouldSeeElementMatchingTo(description, allOfDetailed(
                                    hasText(trafficData.getInformer().getText()),
                                    hasAttribute(HREF, equalTo(
                                            trafficData.getInformer().getUrl().replace("&amp", "&")))
                            ))
                    );
        }

        return collector;
    }

    @Override
    @Step("Check traffic block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        Traffic trafficData = validator.getCleanvars().getTraffic();
        if (trafficData == null || trafficData.getShow() == 0) {
            return collector()
                    .check(shouldNotSeeElement(this));
        }

        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateHeader(title, validator),
                        validateDescription(description, validator),
                        validateForecast(forecast, validator)
                );
    }

    @Name("Хедер пробок")
    @FindBy(xpath = ".//h1")
    public static class TrafficHeader extends HtmlElement {

        @Name("Заголовок")
        @FindBy(xpath = ".//a[1]")
        public HtmlElement title;

        @Name("Светофор")
        @FindBy(xpath = ".//a[2]/i")
        public HtmlElement icon;

        @Name("Балл пробок")
        @FindBy(xpath = ".//a[2]")
        public HtmlElement jams;

        @Step("{0}")
        public static HierarchicalErrorCollector validateTitle(HtmlElement title,
                                                               Validator<? extends DesktopMainMorda> validator) {

            Traffic trafficData = validator.getCleanvars().getTraffic();
            return collector()
                    .check(shouldSeeElement(title))
                    .check(
                            shouldSeeElementMatchingTo(title, allOfDetailed(
                                    hasText(getTranslation(Dictionary.Home.Traffic.TRAFFIC_PROBKI, validator.getMorda().getLanguage())),
                                    hasAttribute(HREF, equalTo(
                                            url(trafficData.getHref(), validator.getMorda().getScheme())
                                                    .replace("&amp;", "&")))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateIcon(HtmlElement icon, Validator<? extends DesktopMainMorda> validator) {
            Traffic trafficData = validator.getCleanvars().getTraffic();
            return collector()
                    .check(shouldSeeElement(icon))
                    .check(
                            shouldSeeElementMatchingTo(icon,
                                    hasClass(containsString("b-ico-traffic-" + trafficData.getClazz())))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateJams(HtmlElement jams, Validator<? extends DesktopMainMorda> validator) {
            Traffic trafficData = validator.getCleanvars().getTraffic();
            if (trafficData.getRate() == null) {
                return collector()
                        .check(shouldNotSeeElement(jams));
            }

            return collector()
                    .check(shouldSeeElement(jams))
                    .check(
                            shouldSeeElementMatchingTo(jams, allOfDetailed(
                                    hasText(trafficData.getRate() + " " + trafficData.getRateaccus()),
                                    hasAttribute(HREF, equalTo(
                                            url(trafficData.getHref(), validator.getMorda().getScheme())
                                                    .replace("&amp;", "&")))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateHeader(TrafficHeader header, Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(header))
                    .check(
                            validateTitle(header.title, validator),
                            validateIcon(header.icon, validator),
                            validateJams(header.jams, validator)
                    );
        }
    }

    @Name("Прогноз пробок")
    @FindBy(xpath = ".//div[@class='traffic__forecast' or contains(@class, 'traffic__text-forecast')]")
    public static class TrafficForecast extends HtmlElement {

        @Name("Заголовок прогноза")
        @FindBy(xpath = ".//span[@class = 'traffic__forecast__title']")
        public HtmlElement forecastTitle;

        @Name("Кружки прогноза")
        @FindBy(xpath = ".//span[@class = 'traffic__forecast__item']")
        public List<TrafficForecastItem> forecastItems;

        @Step("{0}")
        public static HierarchicalErrorCollector validateForecastTitle(HtmlElement forecastTitle,
                                                                       Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(forecastTitle))
                    .check(shouldSeeElementMatchingTo(forecastTitle,
                            hasText(getTranslation(TRAFFIC_FORECAST, validator.getMorda().getLanguage()))));
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateForecastItems(List<TrafficForecastItem> forecastItems,
                                                                       Validator<? extends DesktopMainMorda> validator) {
            Traffic trafficData = validator.getCleanvars().getTraffic();

            HierarchicalErrorCollector collector = collector();

            for (int i = 0; i != Math.min(forecastItems.size(), trafficData.getFuture().size()); i++) {
                collector.check(validateForecastItem(forecastItems.get(i), trafficData.getFuture().get(i), validator));
            }

            HierarchicalErrorCollector countCollector = collector().check(
                    shouldSeeElementMatchingTo(forecastItems, hasSize(trafficData.getFuture().size()))
            );
            collector.check(countCollector);

            return collector;
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateForecast(TrafficForecast forecast,
                                                                  Validator<? extends DesktopMainMorda> validator) {
            Traffic trafficData = validator.getCleanvars().getTraffic();

            if (trafficData.getFuture().size() == 0) {
                return collector()
                        .check(shouldNotSeeElement(forecast));
            }
            String classAttribute = forecast.getAttribute("class");

            HierarchicalErrorCollector collector = collector()
                    .check(shouldSeeElement(forecast));

            //у текстового прогноза @class=traffic__text-forecast traffic__informer
            if(classAttribute.contains("traffic__forecast")){
                collector.check(
                        validateForecastTitle(forecast.forecastTitle, validator),
                        validateForecastItems(forecast.forecastItems, validator)
                );
            }
            return collector;
        }

        @Name("Элемент прогноза")
        public static class TrafficForecastItem extends HtmlElement {
            @Name("Кружок с баллом")
            @FindBy(xpath = ".//div[contains(@class, 'traffic__forecast__item__value')]")
            public HtmlElement value;

            @Name("Время")
            @FindBy(xpath = ".//span[contains(@class, 'traffic__forecast__item__time')]")
            public HtmlElement time;

            @Step("{0}")
            public static HierarchicalErrorCollector validateForecastItem(TrafficForecastItem forecastItem,
                                                                          Future forecastItemData,
                                                                          Validator<? extends DesktopMainMorda> validator) {
                boolean isFirstItem = validator.getCleanvars().getTraffic().getFuture().indexOf(forecastItemData) == 0;
                String timeText = isFirstItem
                        ? forecastItemData.getHour() + " " + getTranslation(Dictionary.Local.Traffic.TRAFFIC_FORECAST_HOUR, validator.getMorda().getLanguage())
                        : valueOf(forecastItemData.getHour());

                HierarchicalErrorCollector timeCheck = collector()
                        .check(shouldSeeElement(forecastItem.time))
                        .check(shouldSeeElementMatchingTo(forecastItem.time, hasText(timeText)));

                HierarchicalErrorCollector valueCheck = collector()
                        .check(shouldSeeElement(forecastItem.value))
                        .check(shouldSeeElementMatchingTo(forecastItem.value, allOfDetailed(
                                hasText(valueOf(forecastItemData.getJams())),
                                hasClass(containsString("traffic__forecast__item__value_" + forecastItemData.getJams()))
                        )));

                return collector()
                        .check(shouldSeeElement(forecastItem))
                        .check(
                                valueCheck,
                                timeCheck
                        );
            }

        }


    }
}