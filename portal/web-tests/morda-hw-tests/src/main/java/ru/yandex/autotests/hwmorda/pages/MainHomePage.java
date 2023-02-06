package ru.yandex.autotests.hwmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import static ru.yandex.qatools.htmlelements.matchers.common.DoesElementExistMatcher.exists;

/**
 * User: alex89
 * Date: 13.09.12
 */
public class MainHomePage {
    public MainHomePage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }


    @Name("Блок погоды")
    @FindBy(xpath = "//div[contains(@class,'weather')]")
    public WeatherBlock weather;

    @Name("Блок новостей")
    @FindBy(xpath = ".//div[contains(@class,'news')]")
    public NewsBlock news;

    @Name("Блок пробок")
    @FindBy(xpath = ".//div[contains(@class,'traffic')]")
    public TrafficBlock traffic;

    @Name("Блок котировок")
    @FindBy(xpath = ".//div[contains(@class,'stocks')]")
    public RatesBlock rates;

    public static class WeatherBlock extends HtmlElement {
        @Name("Текущая температура")
        @FindBy(xpath = ".//a[contains(.,'°C')]")
        public HtmlElement currentTemperature;

        @Name("Полный прогноз")
        @FindBy(xpath = ".//div[contains(@class,'info')]")
        public HtmlElement forecastInfo;

        @Override
        public String getText() {
            return (currentTemperature.getText() + forecastInfo.getText()).replace(" °C", "\n")
                    .replace("  ", " ").replaceAll("([\\d]+)", "$1°");
        }
    }

    public static class NewsBlock extends HtmlElement {
        @Name("Первая новость")
        @FindBy(xpath = ".//li[contains(@class,'item')]")
        public HtmlElement item;

        @Override
        public String getText() {
            return item.getText().substring(3);
        }
    }


    public static class TrafficBlock extends HtmlElement {
        @Name("Баллы")
        @FindBy(xpath = ".//span[contains(@class,'rate')]")
        public HtmlElement trafficPoints;

        @Name("Стрелка")
        @FindBy(xpath = "  .//span[contains(@class,'arrow')]")
        public HtmlElement trafficArrow;

        @Name("Состояние на дорогах")//Например, Серьёзные пробки
        @FindBy(xpath = ".//div[contains(@class,'traffic')]//div[contains(@class,'b-traffic__info') and ./a]")
        public HtmlElement trafficDescription;

        @Override
        public String getText() {
            if (exists().matches(trafficArrow)) {
                return trafficPoints.getText().replace(" ", "") + trafficArrow.getText() + "\n" +
                        trafficDescription.getText();
            } else {
                return trafficPoints.getText().replace(" ", "") + "\n" + trafficDescription.getText();
            }
        }
    }

    public static class RatesBlock extends HtmlElement {
        @Name("Курс доллара")
        @FindBy(xpath = ".//tr[contains(.,'USD')]//td[2]" +
                "//span[contains(@class,'currency-value')][1]")
        public HtmlElement usd;

        @Name("Курс евро")
        @FindBy(xpath = ".//tr[contains(.,'EUR')]//td[2]" +
                "//span[contains(@class,'currency-value')][1]")
        public HtmlElement euro;

        @Override
        public String getText() {
            return "USD ЦБ\n" + usd.getText() + "\nEUR ЦБ\n" + euro.getText();
        }
    }
}
