package ru.yandex.autotests.mainmorda.settingpanels;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 09.01.13
 */
@Name("Всплывающее окно 'Поделиться виджетом'")
@FindBy(xpath = "//div[@id='linkToWidgetWindow']")
public class ShareWidgetBalloon extends HtmlElement {
    @Name("Заголовок всплывающего окна 'Поделиться виджетом'")
    @FindBy(xpath = ".//h3[@class='b-modal-window__head']")
    public HtmlElement shareHead;

    @Name("Крестик \"Закрыть окно 'Поделиться виджетом'\"")
    @FindBy(xpath = "./i[contains(@class,'popup__close')]")
    public HtmlElement closeCross;

    @Name("Кнопка \"Закрыть окно 'Поделиться виджетом'\"")
    @FindBy(xpath = ".//button[contains(@class, 'b-wdgt-share__close')]")
    public HtmlElement closeButton;

    @Name("Поле со ссылкой")
    @FindBy(xpath = ".//input[@id='linkToWidget']")
    public TextInput linkInput;

    @Name("Информация о том, как делиться виджетом")
    @FindBy(xpath = ".//div[@class='b-modal-window__data']/p")
    public HtmlElement infoText;

    @Name("Соц-иконка ВКонтакте")
    @FindBy(xpath = ".//a[starts-with(@href,'//share.yandex.ru/go.xml?service=vkontakte')]")
    public HtmlElement vkIcon;

    @Name("Соц-иконка Facebook")
    @FindBy(xpath = ".//a[starts-with(@href,'//share.yandex.ru/go.xml?service=facebook')]")
    public HtmlElement fbIcon;

    @Name("Соц-иконка Twitter")
    @FindBy(xpath = ".//a[starts-with(@href,'//share.yandex.ru/go.xml?service=twitter')]")
    public HtmlElement twIcon;

    /*
    public static final String CloseButtonXpath = ShareBaseXpath + "/div[@class='controls']" +
            "/input[@class='closeLinkToWidgetWindow']";
    public static final String InfoTextXpath = ShareBaseXpath + "/div[@class='b-modal-window__data']/p";
    public static final String LinkInputXpath = ShareBaseXpath + "//input[@id='linkToWidget']";
    private static final String SocialNetworksXpath = ShareBaseXpath + "//span[@id='socialNetworks']" +
            "/a[starts-with(@href,'http://share.yandex.ru/go.xml?service=";
     */
}
