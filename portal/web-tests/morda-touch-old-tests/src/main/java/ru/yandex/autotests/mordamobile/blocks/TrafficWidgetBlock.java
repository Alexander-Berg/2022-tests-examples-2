package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок пробок")
@FindBy(xpath = "//div[contains(@class, 'b-traffic-info')]")
public class TrafficWidgetBlock extends HtmlElement {

    @Name("Заголовок")
    @FindBy(xpath = ".//div[contains(@class,'traffic__title')]")
    public HtmlElement title;

    @Name("Ссылка трафика")
    @FindBy(xpath = ".//a")
    public HtmlElement trafficLink;

    @Name("Светофор")
    @FindBy(xpath = ".//i")
    public HtmlElement icon;

    @Name("Баллы")
    @FindBy(xpath = ".//div[contains(@class,'b-traffic__num')]")
    public HtmlElement trafficNum;

    @Name("Блок прогноза пробок")
    @FindBy(xpath = ".//div[@class='b-traffic-forecast']")
    public TrafficForecast trafficForecast;


    @Name("Настроенный блок пробок")
    @FindBy(xpath = ".//a[contains(@class,'b-traffic-personal')]")
    public HtmlElement trafficPersonal;

    public static class TrafficForecast extends HtmlElement {
        @Name("Заголовок")
        @FindBy(xpath = ".//div[contains(@class,'b-traffic-forecast__title')]")
        public HtmlElement title;

        @Name("Элементы прогноза")
        @FindBy(xpath = ".//div[contains(@class,'b-traffic-forecast__value')]")
        public List<HtmlElement> forecasts;

        @Name("Время прогнозов")
        @FindBy(xpath = ".//div[contains(@class,'b-traffic-forecast__hour')]")
        public List<HtmlElement> forecastTimes;
    }
}