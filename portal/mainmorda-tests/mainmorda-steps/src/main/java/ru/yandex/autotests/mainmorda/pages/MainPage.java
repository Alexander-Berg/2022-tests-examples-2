package ru.yandex.autotests.mainmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mainmorda.blocks.EtrainsBlock;
import ru.yandex.autotests.mainmorda.blocks.HeaderBlock;
import ru.yandex.autotests.mainmorda.blocks.MailBlock;
import ru.yandex.autotests.mainmorda.blocks.MailFoldBlock;
import ru.yandex.autotests.mainmorda.blocks.MailLoggedBlock;
import ru.yandex.autotests.mainmorda.blocks.MailLoggedFoldBlock;
import ru.yandex.autotests.mainmorda.blocks.OverMailBlock;
import ru.yandex.autotests.mainmorda.blocks.RssWidget;
import ru.yandex.autotests.mainmorda.blocks.RssnewsWidget;
import ru.yandex.autotests.mainmorda.blocks.ThemeMenu;
import ru.yandex.autotests.mainmorda.blocks.Widget;
import ru.yandex.autotests.mainmorda.blocks.WidgetSettingsHeader;
import ru.yandex.autotests.mainmorda.settingpanels.AddWidgetBalloon;
import ru.yandex.autotests.mainmorda.settingpanels.DeleteWidgetBalloon;
import ru.yandex.autotests.mainmorda.settingpanels.EtrainsSettingsMenu;
import ru.yandex.autotests.mainmorda.settingpanels.NewsSettingsMenu;
import ru.yandex.autotests.mainmorda.settingpanels.RatesSettingsMenu;
import ru.yandex.autotests.mainmorda.settingpanels.RssWidgetSettingsPanel;
import ru.yandex.autotests.mainmorda.settingpanels.ServicesSettingsMenu;
import ru.yandex.autotests.mainmorda.settingpanels.ShareWidgetBalloon;
import ru.yandex.autotests.mainmorda.settingpanels.TVSettingMenu;
import ru.yandex.autotests.mainmorda.settingpanels.TrafficSettingsMenu;
import ru.yandex.autotests.mainmorda.settingpanels.WeatherSettingsMenu;
import ru.yandex.autotests.mainmorda.settingpanels.WidgetSettings;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

/**
 * User: leonsabr
 * Date: 04.10.12
 */
public class MainPage extends BasePage {
    public MainPage(WebDriver driver) {
        super(driver);
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Header")
    public HeaderBlock headerBlock;

    @Name("Паранджа")
    @FindBy(xpath = "//div[@class='v_sform_bg']")
    public HtmlElement veil;

    @Name("Паранджа iframe")
    @FindBy(xpath = "//iframe[contains(@class, 'popup__under_type_paranja')]")
    public HtmlElement iframeVeil;

    @Name("Незалогиновый большой домик")
    @FindBy(xpath = "//form[contains(@class, 'auth_js_inited')]")
    public MailBlock mailBlock;

    @Name("Незалогиновый свернутый домик")
    @FindBy(xpath = "//div[contains(@class,'b-inline b-topbar__body')]")
    public MailFoldBlock mailFoldBlock;

    @Name("Залогиновый большой почтовый домик")
    @FindBy(xpath = "//div[contains(@class, 'popup__content')][.//div[contains(@class, 'domik__title')]]")
    public MailLoggedBlock mailLoggedBlock;

    @Name("Залогиновый свёрнутый домик")
    public MailLoggedFoldBlock mailLoggedFoldBlock;

    @Name("Пространство над домиком")
    public OverMailBlock overMailBlock;

    //в доменах ru и ua
    @Name("Виджет Электричек")
    public EtrainsBlock etrainsBlock;

    @Name("Меню установки скинов")
    public ThemeMenu themeMenu;
    //    //=========================
    @Name("Виджеты на главной странице")
    @FindBy(xpath = "//div[contains(@id,'wd-') and contains(@class,'b-widget-data')]")
    public/* List<WebElement>*/ List<Widget> widgets;

    @Name("Кнопки возврата в каталог в виджетах")
    @FindBy(xpath = "//div[contains(@id,'wd-') and contains(@class,'b-widget-data')]//parent::div/*[@id='retToCat']")
    public List<HtmlElement> catalogButtonList;
    //
//    //Geoballoon-ы
//    @Name("Geoballoon 1-го или 2-го")
//    public GeoBalloon geoBalloonType1And2;
//    @Name("Geoballoon 3-типа")
//    public GeoBalloonType3 geoBalloonType3;
//    //====================================Rss-виджет
    @Name("Виджет LentaRu")
    @FindBy(xpath = "//div[contains(@id,'wd-wrapper-28')]")
    public Widget lentaRuWidget;

    public RssnewsWidget rssnewsWidget;
    //
    public AddWidgetBalloon addWidgetBalloon;
    public DeleteWidgetBalloon deleteWidgetBalloon;
    public ShareWidgetBalloon shareWidgetBalloon;
    //    //===================================================Режим редактирования
    @Name("Header режима редактирования")
    public WidgetSettingsHeader widgetSettingsHeader;
    //
    @Name("Меню настройки виджета новостей")
    public NewsSettingsMenu newsSettings;

    @Name("Окно настройки виджета ТВ")
    public TVSettingMenu tvSettings;

    @Name("Окно настройки виджета Погода")
    public WeatherSettingsMenu weatherSettings;

    @Name("Окно настройки виджета Котировка")
    public RatesSettingsMenu ratesSettings;

    @Name("Окно настройки виджета Электрички")
    public EtrainsSettingsMenu etrainsSettings;

    @Name("Фрейм виджета Электрички")
    @FindBy(xpath = "//iframe[contains(@id,'wd-prefs-_etrains-')]")
    public HtmlElement etrainsFrame;

    @Name("Окно настройки блока сервисов")
    public ServicesSettingsMenu servicesSettings;
    //
    @Name("Окно настройки виджета")
    public WidgetSettings widgetSettings;

    @Name("Окно настройки Rss виджета")
    public RssWidgetSettingsPanel rssSettings;

    @Name("Окно настройки Rss виджета")
    public RssWidget rssWidget;

    @Name("Окно настройки виджета пробок")
    public TrafficSettingsMenu trafficSettings;

    @Name("Все редактируемые виджеты")
    @FindBy(xpath = "//div[contains(@id,'wd-') and contains(@class,'b-widget-data')]" +
            "[.//parent::div//a[contains(@class,'setup')]]")
    public List<Widget> allEditableWidgets;

    @Name("Css скина")
    @FindBy(xpath = "//link[@rel='stylesheet' and contains(@href, 'skins')]")
    public HtmlElement skinCss;

    @Name("Script скина")
    @FindBy(xpath = "//script[contains(@src, 'skins')]")
    public HtmlElement skinScript;

    @Name("Каталог виджетов iframe")
    @FindBy(xpath = "//div[@id='wdgt-catalog']//iframe")
    public HtmlElement catalogIframe;

    @Name("поле ввода")
    @FindBy(xpath = "//input[@id='text']")
    public TextInput input;
}
