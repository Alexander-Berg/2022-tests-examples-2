package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;


/**
 * User: alex89
 * Date: 11.09.12
 */
@FindBy(xpath = "//div[contains(@class, 'b-wrapper-weather')]")
@Name("Блок Погоды")
public class WeatherBlock extends Widget {

    @Name("Заголовок виджета Погода")
    @FindBy(xpath = ".//div[@class='b-content-item__title']")
    public WeatherBlockHeader weatherBlockHeader;

    @Name("Прогноз")
    @FindBy(xpath = ".//div[@class='b-weather__info']")
    public WeatherForecastInfo weatherForecast;

    @Name("Особое сообщение о погоде")
    @FindBy(xpath = ".//div[@class='b-weather__codes']/a")
    public HtmlElement forecastInfoOccasion;

    @Name("Город")
    @FindBy(xpath = ".//div[@class='b-weather__city']")
    public HtmlElement city;

    public static class WeatherBlockHeader extends HtmlElement {
        @Name("Ссылка 'Погода'")
        @FindBy(xpath = "./a[1]")
        public HtmlElement weatherLink;

        @Name("Ссылка на иконке погоды")
        @FindBy(xpath = "./a[contains(@class,'b-weather__icon_link')]")
        public HtmlElement weatherIconLink;

        @Name("Иконка погоды")
        @FindBy(xpath = "./a[contains(@class,'b-weather__icon_link')]/i")
        public HtmlElement weatherIcon;

        @Name("Ссылка со значением текущей температуры")
        @FindBy(xpath = "./a[contains(.,'°C')]")
        public HtmlElement currentTemperature;
    }

    public static class WeatherForecastInfo extends HtmlElement {
        @Name("Полный прогноз на завтра")
        @FindBy(xpath = ".")
        public HtmlElement forecastInfo;

        @Name("Ссылки полного прогноза [1]")
        @FindBy(xpath = "./a[1]")
        public HtmlElement forecastLink1;

        @Name("Ссылки полного прогноза [2]")
        @FindBy(xpath = "./a[2]")
        public HtmlElement forecastLink2;

    }
}
