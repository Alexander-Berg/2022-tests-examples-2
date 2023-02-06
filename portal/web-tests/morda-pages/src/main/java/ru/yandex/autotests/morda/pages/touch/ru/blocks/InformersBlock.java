package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.traffic.Future;
import ru.yandex.autotests.mordabackend.beans.traffic.Traffic;
import ru.yandex.autotests.mordabackend.beans.weather.Weather;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.pages.touch.ru.blocks.InformersBlock.MailInformer.validateMailInformer;
import static ru.yandex.autotests.morda.pages.touch.ru.blocks.InformersBlock.TrafficInformer.validateTrafficBlock;
import static ru.yandex.autotests.morda.pages.touch.ru.blocks.InformersBlock.WeatherInformer.validateWeatherInformer;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasClass;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/05/15
 */
@Name("Блок с информерами")
@FindBy(xpath = "//div[contains(@class, 'content__bg')]/div[contains(@class, 'informers3')]")
public class InformersBlock extends HtmlElement implements Validateable<TouchRuMorda> {

    @Name("Информер погоды")
    @FindBy(xpath = ".//div[contains(@class, 'item_type_weather')]/a")
    private WeatherInformer weatherInformer;

    @Name("Информер почты")
    @FindBy(xpath = ".//div[contains(@class, 'item_type_mail')]/a")
    private MailInformer mailInformer;

    @Name("Информер пробок")
    @FindBy(xpath = "//div[contains(@class, 'informers3__other-line') or contains(@class, 'informers3__short-item_type_traffic')]")
    private TrafficInformer trafficInformer;

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return collector()
                .check(
                        validateWeatherInformer(weatherInformer, validator),
                        validateMailInformer(mailInformer, validator),
                        validateTrafficBlock(trafficInformer, validator)
                );
    }

    public static class WeatherInformer extends HtmlElement {

        @Name("Заголовок")
        @FindBy(xpath = ".//span[contains(@class, 'title')]")
        private HtmlElement title;

        @Name("Иконка")
        @FindBy(xpath = ".//span[contains(@class, 'informers__icon__weather')]")
        private HtmlElement icon;

        @Name("Температура")
        @FindBy(xpath = ".//span[contains(@class, 'item-num')]")
        private HtmlElement temperature;

        @Name("Прогноз погоды")
        @FindBy(xpath = ".//span[contains(@class, 'item-data')]")
        private HtmlElement temperatureData;

        public static HierarchicalErrorCollector validateWeatherTitle(HtmlElement title,
                                                                      Validator<? extends TouchRuMorda> validator) {
            String titleText = getTranslation("home", "mobile", "informers.weather", validator.getMorda().getLanguage());
            return collector()
                    .check(shouldSeeElement(title))
                    .check(shouldSeeElementMatchingTo(title, hasText(titleText)));
        }

        public static HierarchicalErrorCollector validateWeatherIcon(HtmlElement icon,
                                                                     Validator<? extends TouchRuMorda> validator) {
            Weather weather = validator.getCleanvars().getWeather();
            String clazz = "informers__icon__weather_" + weather.getIv3U1();
//                    .replaceAll("\\-", "minus-");
            return collector()
                    .check(shouldSeeElement(icon))
                    .check(shouldSeeElementMatchingTo(icon, hasClass(containsString(clazz))));
        }

        public static HierarchicalErrorCollector validateWeatherTemperature(HtmlElement temperature,
                                                                            Validator<? extends TouchRuMorda> validator) {
            Weather weather = validator.getCleanvars().getWeather();
            return collector()
                    .check(shouldSeeElement(temperature))
                    .check(shouldSeeElementMatchingTo(temperature, hasText(weather.getT1())));
        }

        public static HierarchicalErrorCollector validateWeatherData(HtmlElement data,
                                                                     Validator<? extends TouchRuMorda> validator) {
            Weather weather = validator.getCleanvars().getWeather();
            return collector()
                    .check(shouldSeeElement(data))
                    .check(shouldSeeElementMatchingTo(data, hasText(weather.getT1() + "\n" + weather.getT2Name() +
                            " " + weather.getT2())));
        }

        public static HierarchicalErrorCollector validateWeatherInformer(WeatherInformer weatherInformer,
                                                                         Validator<? extends TouchRuMorda> validator) {
            Weather weather = validator.getCleanvars().getWeather();
            HierarchicalErrorCollector informerHref = collector()
                    .check(shouldSeeElementMatchingTo(weatherInformer,
                            hasAttribute(HREF, startsWith(weather.getUrl()))));

            return collector()
                    .check(shouldSeeElement(weatherInformer))
                    .check(
                            informerHref,
                            validateWeatherTitle(weatherInformer.title, validator),
                            validateWeatherIcon(weatherInformer.icon, validator),
//                            validateWeatherTemperature(weatherInformer.temperature, validator),
                            validateWeatherData(weatherInformer.temperatureData, validator)
                    );
        }
    }

    public static class MailInformer extends HtmlElement {

        @Name("Заголовок")
        @FindBy(xpath = ".//span[contains(@class, 'title')]")
        private HtmlElement title;

        @Name("Иконка")
        @FindBy(xpath = ".//span[contains(@class, 'informers__icon__mail')]")
        private HtmlElement icon;

        @Name("Данные почты")
        @FindBy(xpath = ".//span[contains(@class, 'item-data')]")
        private HtmlElement mailData;

        public static HierarchicalErrorCollector validateMailTitle(HtmlElement title,
                                                                   Validator<? extends TouchRuMorda> validator) {
            return collector()
                    .check(shouldSeeElement(title))
                    .check(shouldSeeElementMatchingTo(title,
                            hasText(getTranslation(Dictionary.Home.Mail.TITLE, validator.getMorda().getLanguage()))));
        }

        public static HierarchicalErrorCollector validateMailIcon(HtmlElement icon,
                                                                  Validator<? extends TouchRuMorda> validator) {
            return collector()
                    .check(shouldSeeElement(icon));
        }

        public static HierarchicalErrorCollector validateMailData(HtmlElement data,
                                                                  Validator<? extends TouchRuMorda> validator) {
            return collector()
                    .check(shouldSeeElement(data))
                    .check(shouldSeeElementMatchingTo(data,
                                    hasText(getTranslation(Dictionary.Home.Mail.LOGIN, validator.getMorda().getLanguage()).toLowerCase()))
                    );
        }

        public static HierarchicalErrorCollector validateMailInformer(MailInformer mailInformer,
                                                                      Validator<? extends TouchRuMorda> validator) {
            HierarchicalErrorCollector informerHref = collector()
                    .check(shouldSeeElementMatchingTo(mailInformer,
                            hasAttribute(HREF, startsWith(validator.getCleanvars().getMail().getHref()))));
            return collector()
                    .check(shouldSeeElement(mailInformer))
                    .check(
                            informerHref,
                            validateMailTitle(mailInformer.title, validator),
                            validateMailIcon(mailInformer.icon, validator),
                            validateMailData(mailInformer.mailData, validator)
                    );
        }
    }

    public static class TrafficInformer extends HtmlElement {

        @FindBy(xpath = ".//a[contains(@class, 'informers3__short-link')]")
        private CurrentRateBlock rate;
        @FindBy(xpath = "//a[contains(@class, 'informers3__traffic-forecast')]")
        private ForecastBlock forecast;

        @Step("{0}")
        public static HierarchicalErrorCollector validateTrafficBlock(TrafficInformer trafficInformer,
                                                                      Validator<? extends TouchRuMorda> validator) {
            HierarchicalErrorCollector collector = collector()
                    .check(
                            shouldSeeElement(trafficInformer)
                    );

            int geoId = validator.getCleanvars().getGeoID();

            String isHoliday = validator.getCleanvars().getIsHoliday();

            if ((geoId == 2 || geoId == 213 || geoId == 143) && "0".equals(isHoliday)) {
                collector.check(
                        validateForecastBlock(trafficInformer.forecast, validator)
                );
            }

            return collector
                    .check(
                            validateCurrentRateBlock(trafficInformer.rate, validator)
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateForecastBlock(ForecastBlock forecastBlock,
                                                                       Validator<? extends TouchRuMorda> validator) {
            HierarchicalErrorCollector collector = collector()
                    .check(shouldSeeElement(forecastBlock));

            collector.check(
                    shouldSeeElementMatchingTo(forecastBlock,
                            hasAttribute(HREF,
                                    equalTo(validator.getCleanvars().getTraffic().getHref().replaceAll("&amp;", "&")))
                    ))
                    .check(validateFutures(forecastBlock.forecast, validator));

            return collector;
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateFutures(List<ForecastBlock.Futures> futures,
                                                                 Validator<? extends TouchRuMorda> validator) {

            HierarchicalErrorCollector collector = collector();

            if (validator.getCleanvars().getTraffic().getFutureMax() < 4) {
                return collector;
            }

            List<Future> listOfFutures = validator.getCleanvars().getTraffic().getFuture();

            for (int i = 0; i < Math.min(futures.size(), listOfFutures.size()); i++) {
                collector.check(validateFutureItem(futures.get(i), listOfFutures.get(i), validator));
            }

            HierarchicalErrorCollector countCollector = collector().check(
                    shouldSeeElementMatchingTo(futures, hasSize(listOfFutures.size()))
            );
            collector.check(countCollector);

            return collector;
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateFutureItem(ForecastBlock.Futures futures,
                                                                    Future future,
                                                                    Validator<? extends TouchRuMorda> validator) {
            return collector()
                    .check(shouldSeeElement(futures))
                    .check(shouldSeeElementMatchingTo(futures.mark,
                                    hasText(String.valueOf(future.getJams()))
                            ),
                            shouldSeeElementMatchingTo(futures.time,
                                    hasText(startsWith(String.valueOf(future.getHour())))
                            )
                    );

        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateCurrentRateBlock(CurrentRateBlock currentRateBlock,
                                                                          Validator<? extends TouchRuMorda> validator) {
            HierarchicalErrorCollector collector = collector()
                    .check(shouldSeeElement(currentRateBlock));

            collector.check(
                    shouldSeeElementMatchingTo(currentRateBlock,
                            hasAttribute(HREF,
                                    equalTo(validator.getCleanvars().getTraffic().getHref().replaceAll("&amp;", "&")))
                    ));

            if (validator.getCleanvars().getTraffic().getRate() == null) {
                return collector
                        .check(
                                validateTrafficLights(currentRateBlock.icons, validator)
                        );
            }
            return collector
                    .check(
                            validateCurrentRateTitle(currentRateBlock.title, validator),
                            validateCurrentRateIcons(currentRateBlock.icons, validator),
                            validateCurrentRateText(currentRateBlock.mark, validator)
//                            validateCurrentRateNum(currentRateBlock.currentRate, validator)
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateTrafficLights(List<HtmlElement> icons,
                                                                       Validator<? extends TouchRuMorda> validator) {
            HierarchicalErrorCollector collector = collector().check(
                    shouldSeeElementMatchingTo(icons, hasSize(3)));

            icons.forEach(icon -> collector
                    .check(shouldSeeElement(icon)));

            return collector;
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateCurrentRateTitle(HtmlElement title,
                                                                          Validator<? extends TouchRuMorda> validator) {
            return collector()
                    .check(shouldSeeElement(title))
                    .check(shouldSeeElementMatchingTo(title,
                            hasText(getTranslation("home", "traffic", "title", validator.getMorda().getLanguage()))));
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateCurrentRateIcons(List<HtmlElement> icons,
                                                                          Validator<? extends TouchRuMorda> validator) {
            HierarchicalErrorCollector collector = collector().check(
                    shouldSeeElementMatchingTo(icons, hasSize(1)));

            return collector
                    .check(
                            shouldSeeElement(icons.stream().findFirst().get())
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateCurrentRateText(HtmlElement mark,
                                                                         Validator<? extends TouchRuMorda> validator) {
            Traffic traffic = validator.getCleanvars().getTraffic();

            HierarchicalErrorCollector collector = collector();
            collector
                    .check(shouldSeeElement(mark));

            if (traffic.getRate() == 0) {
                return collector
                        .check(
                                shouldSeeElementMatchingTo(mark,
                                        hasText(getTranslation("home","traffic","personal.nojam", validator.getMorda().getLanguage()))
                                ));
            }


            return collector
                    .check(shouldSeeElementMatchingTo(mark, allOfDetailed(
                            hasText(startsWith(String.valueOf(traffic.getRate()))),
                            hasText(containsString(traffic.getRateaccus()))
                    )));
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateCurrentRateNum(HtmlElement currentRate,
                                                                        Validator<? extends TouchRuMorda> validator) {
            Traffic traffic = validator.getCleanvars().getTraffic();

            return collector()
                    .check(shouldSeeElement(currentRate))
                    .check(shouldSeeElementMatchingTo(currentRate,
                            hasText(startsWith(String.valueOf(traffic.getRate())))
                    ));
        }

    }

    @Name("Блок с прогнозом")
    public static class ForecastBlock extends HtmlElement {

        @Name("Заголовок")
        @FindBy(xpath = ".//div[@class = 'traffic-icon-forecast__title-inner']")
        public HtmlElement title;

        @Name("Прогноз пробок")
        @FindBy(xpath = ".//div[contains(@class, 'traffic-icon-forecast__item')]")
        public List<Futures> forecast;

        public class Futures extends HtmlElement {

            @Name("Иконка с баллами")
            @FindBy(xpath = ".//div[contains(@class, 'notifications_type_traffic__icon__text')]")
            public HtmlElement mark;

            @Name("Время")
            @FindBy(xpath = ".//div[contains(@class, 'traffic-icon-forecast__hour')]")
            public HtmlElement time;
        }

    }

    @Name("Блок с баллами/светофориком")
    public static class CurrentRateBlock extends HtmlElement {

        @Name("Заголовок")
        @FindBy(xpath = ".//span[contains(@class, 'informers3__item-title')]")
        public HtmlElement title;

        @Name("Иконка")
        @FindBy(xpath = ".//span[contains(@class, 'informers3__icon')]")
        public List<HtmlElement> icons;

        @Name("Текст \"баллов\"")
        @FindBy(xpath = ".//span[contains(@class, 'informers3__item-data')]")
        public HtmlElement mark;

    }
}
