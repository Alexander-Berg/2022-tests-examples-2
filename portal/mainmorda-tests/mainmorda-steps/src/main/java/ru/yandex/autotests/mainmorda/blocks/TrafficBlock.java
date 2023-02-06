package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;


/**
 * User: alex89
 * Date: 09.06.12
 */
@FindBy(xpath = "//div[contains(@class,'b-wrapper-traffic')]")
@Name("Виджет пробок с баллами")
public class TrafficBlock extends Widget {
    @Name("Ссылка 'Пробки'")
    @FindBy(xpath = ".//div[contains(@class,'b-traffic__title')]/a[1]")
    public HtmlElement trafficLink;

    @Name("Светофор")
    @FindBy(xpath = ".//div[contains(@class,'b-traffic__title')]" +
            "/a[contains(@class,'b-traffic__status')]")
    public HtmlElement trafficLights;

    @Name("Баллы")
    @FindBy(xpath = ".//div[contains(@class,'b-traffic__title')]/span[@class='b-traffic__rate']")
    // @Required(false)
    public HtmlElement trafficPoints;

    @Name("Описание дорожной ситуации")
    @FindBy(xpath = ".//div[contains(@class,'b-traffic__info')]/a[contains(@class,'b-traffic__descr')]")
    public HtmlElement trafficDescription;

    @Name("Стрелка")
    @FindBy(xpath = ".//span[@class='b-traffic__arrow']")
    public HtmlElement trafficArrow;

    @Name("Прогноз")
    @FindBy(xpath = ".//div[@class='b-traffic__forecast']")
    public TrafficForecast trafficForecast;


    public static class TrafficForecast extends HtmlElement {
        @Name("текст Прогноз")
        @FindBy(xpath = ".//span[@class='b-traffic-forecast__title']")
        public HtmlElement forecastText;

        @Name("Значения прогноза")
        @FindBy(xpath = ".//div[contains(@class,'value')]")
        public List<HtmlElement> forecastValues;

        @Name("Значения прогноза")
        @FindBy(xpath = ".//span[contains(@class,'time')]")
        public List<HtmlElement> forecastTimes;
    }
}
