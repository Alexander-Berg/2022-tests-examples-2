package ru.yandex.autotests.mordamobile.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordamobile.blocks.*;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: alex89
 * Date: 13.09.12
 */
public class HomePage {
    public HomePage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Логотип")
    @FindBy(xpath = "//div[contains(@class, 'b-logo')]")
    public HtmlElement logotype;

    @Name("Блок промо")
    public PoiBlock poiBlock;

    @Name("Блок поиска")
    public SearchBlock searchBlock;

    @Name("Баннер")
    @FindBy(xpath = "//div[contains(@class, 'b-banner ')]")
    public HtmlElement banner;

    @Name("Региональный блок")
    public GeoBlock geoBlock;

    @Name("Блок денег")
    public MoneyBlock moneyBlock;

    @Name("Информер погоды")
    public WeatherBlock weatherBlock;

    @Name("Информер почты")
    public MailBlock mailBlock;

    @Name("Блок новостей")
    public NewsBlock newsBlock;

    @Name("Блок блогов")
    public BlogsBlock blogsBlock;

    @Name("Блок афиши")
    public AfishaBlock afishaBlock;

    @Name("Блок ТВ")
    public TvBlock tvBlock;

    @Name("Фото дня")
    public ImageOfDayBlock photoOfTheDayBlock;

    @Name("Блок котировок")
    public RatesBlock ratesBlock;

    @Name("Выпадающее меню")
    public MenuBlock menuBlock;

    @Name("Приложения")
    public AppsBlock appsBlock;

    @Name("Блок расписания")
    public ScheduleBlock scheduleBlock;

    @Name("Блок электричек")
    public EtrainsBlock etrainsBlock;

    @Name("Блок пробок")
    public TrafficWidgetBlock trafficWidgetBlock;

    @Name("Кнопка открытия меню")
    @FindBy(xpath = "//span[contains(@class, 'sideslide__switcher')]")
    public HtmlElement menuButton;

    @Name("Кнопка закрытия меню")
    @FindBy(xpath = "//div[contains(@class, 'fake-switcher')]")
    public HtmlElement menuButtonClose;

    @Name("Домик авторизации")
    public LoginPopupBlock loginPopup;

    @Name("Блок метро")
    @FindBy(xpath = "//div [@class='b-widget b-metro']")
    public MetroBlock metroBlock;
}

