package ru.yandex.autotests.mainmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.*;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

/**
 * User: leonsabr
 * Date: 04.10.12
 */
public class BasePage {
    public BasePage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Логотип")
    @FindBy(xpath = "//div[contains(@class,'logo')]//div[contains(@class,'b-logo__image_bg')]")
    public HtmlElement logotype;

    @Name("Баннер")
    @FindBy(xpath = "//div[@id='banner']")
    public Banner banner;

    @Name("Вертикальный баннер")
    @FindBy(xpath = "//div[contains(@class, 'b-banner-left') and ./object[@id='leftBanner']]")
    public Banner verticalBanner;

    @Name("Футер")
    public FooterBlock footerBlock;

    @Name("Виджет Афиша (одиночный)")
    @FindBy(xpath = "//div[contains(@class, 'afisha') and ./div[@class='b-afisha']]")
    public AfishaTvBlock afishaBlock;

    @Name("Виджет ТВ")
    @FindBy(xpath = "//div[contains(@class, 'tv') and ./div[@class='b-afisha']]")
    public AfishaTvBlock tvBlock;

    @Name("Блок poi иконок")
    public GeoBlock geoBlock;

    @Name("Виртуальная клавиатура")
    public VirtualKeyboard keyboard;

    @Name("Блок Новостей")
    public NewsBlock newsBlock;

    @Name("Тизер")
    public TeaserBlock teaserBlock;

    @Name("Виджет котировок")
    public RatesBlock ratesBlock;

    @Name("Блок котировок под новостями")
    public InlineRatesBlock inlineRatesBlock;

    @Name("Попап котировок")
    public RatesPopupBlock ratesPopupBlock;

    @Name("Региональный блок")
    public RegionBlock regionBlock;

    @Name("Поисковая форма")
    public SearchArrowBlock search;

    @Name("Полный блок пробок")
    public TrafficBlock trafficFullBlock;

    @Name("Блок сервисов")
    public ServicesBlock servicesBlock;

    @Name("Виджет погоды")
    public WeatherBlock weatherBlock;

    @Name("Элементы с BADID")
    @FindBy(xpath = "//*[contains(@onmousedown, 'BADID')]")
    public List<HtmlElement> elementsWithBadId;

}
