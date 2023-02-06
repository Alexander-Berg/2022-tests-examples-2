package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.hamcrest.Matcher;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.weather.Weather;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.equalToIgnoringCase;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Weather.WEATHER_TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Погода")
@FindBy(xpath = "//div[contains(@id,'wd-wrapper-_weather')]")
public class WeatherBlock extends Widget<WeatherSettingsBlock> implements Validateable<DesktopMainMorda> {

    public WeatherHeader weatherHeader;
    public WeatherForecast weatherForecast;

    @Name("Город")
    @FindBy(xpath = ".//span[@class='weather__geo']")
    public HtmlElement city;

    public WeatherSettingsBlock weatherSettingsBlock;

    @Override
    protected WeatherSettingsBlock getSetupPopup() {
        return weatherSettingsBlock;
    }

    @Override
    @Step("Check weather")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        weatherHeader.validate(validator),
                        weatherForecast.validate(validator)
                );
    }

    @Name("Хедер погоды")
    @FindBy(xpath = ".//h1")
    public static class WeatherHeader extends HtmlElement implements Validateable<DesktopMainMorda> {

        @Name("Заголовок")
        @FindBy(xpath = ".//a[1]")
        public HtmlElement title;

        @Name("Иконка погоды")
        @FindBy(xpath = ".//a[2]/i")
        public HtmlElement icon;

        @Name("Температура")
        @FindBy(xpath = ".//a[2]")
        public HtmlElement temperature;

        @Step("{0}")
        public static HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends DesktopMainMorda> validator) {
            Weather weatherData = validator.getCleanvars().getWeather();
            return collector()
                    .check(shouldSeeElement(title))
                    .check(
                            shouldSeeElementMatchingTo(title, allOfDetailed(
                                    hasText(getTranslation(WEATHER_TITLE, validator.getMorda().getLanguage())),
                                    hasAttribute(HREF, equalTo(url(weatherData.getUrl(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateIcon(HtmlElement icon, Validator<? extends DesktopMainMorda> validator) {
            Weather weatherData = validator.getCleanvars().getWeather();
            Matcher<String> iconClass = containsString("weather__icon_" + weatherData.getIv3U1());
            return collector()
                    .check(shouldSeeElement(icon))
                    .check(
                            shouldSeeElementMatchingTo(icon, allOfDetailed(
                                            hasAttribute(CLASS, iconClass),
                                            hasAttribute(TITLE, equalTo(weatherData.getIconalt())))
                            )
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateTemperature(HtmlElement temperature, Validator<? extends DesktopMainMorda> validator) {
            Weather weatherData = validator.getCleanvars().getWeather();
            return collector()
                    .check(shouldSeeElement(temperature))
                    .check(
                            shouldSeeElementMatchingTo(temperature, allOfDetailed(
                                    hasText(weatherData.getT1() + " °C"),
                                    hasAttribute(HREF, equalTo(url(weatherData.getUrl(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Override
        @Step("Check weather header")
        public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(this))
                    .check(
                            validateTitle(title, validator),
                            validateIcon(icon, validator),
                            validateTemperature(temperature, validator)
                    );
        }
    }

    @Name("Прогноз погоды")
    @FindBy(xpath = ".//ul[contains(@class, 'list')]")
    public static class WeatherForecast extends HtmlElement implements Validateable<DesktopMainMorda> {

        @Name("Прогноз 1")
        @FindBy(xpath = ".//li[contains(@class, 'list__item')][1]//a[1]")
        public HtmlElement t2;

        @Name("Прогноз 2")
        @FindBy(xpath = ".//li[contains(@class, 'list__item')][1]//a[2]")
        public HtmlElement t3;

        @Name("Прогноз воды")
        @FindBy(xpath = ".//a[1]")
        public HtmlElement water;

        @Step("{0}")
        public static HierarchicalErrorCollector validateT2(HtmlElement t2, Validator<? extends DesktopMainMorda> validator) {
            Weather weatherData = validator.getCleanvars().getWeather();
            return collector()
                    .check(shouldSeeElement(t2))
                    .check(
                            shouldSeeElementMatchingTo(t2, allOfDetailed(
                                    hasText(equalToIgnoringCase(weatherData.getT2Name() + " " + weatherData.getT2())),
                                    hasAttribute(HREF, equalTo(url(weatherData.getUrl(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateT3(HtmlElement t3, Validator<? extends DesktopMainMorda> validator) {
            Weather weatherData = validator.getCleanvars().getWeather();
            return collector()
                    .check(shouldSeeElement(t3))
                    .check(
                            shouldSeeElementMatchingTo(t3, allOfDetailed(
                                    hasText(equalTo(weatherData.getT3Name() + " " + weatherData.getT3())),
                                    hasAttribute(HREF, equalTo(url(weatherData.getUrl(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Override
        @Step("Check weather forecast")
        public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(this))
                    .check(
                            validateT2(t2, validator),
                            validateT3(t3, validator)
                    );
        }
    }

}
