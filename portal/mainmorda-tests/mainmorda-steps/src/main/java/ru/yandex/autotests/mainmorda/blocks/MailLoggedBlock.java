package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;


/**
 * User: alex89
 * Date: 15.05.12
 * Почтовый домик под залогином несвёрнутый
 */
@FindBy(xpath = "//div[contains(@class, 'popup__content')][.//div[contains(@class, 'domik__title')]]")
@Name("Домик залогиненный")
public class MailLoggedBlock extends HtmlElement {
    private static final String TOPBAR_XPATH = ".//div[@class='b-topbar__mail']";

    @Name("Ссылка Почта")
    @FindBy(xpath = ".//div[contains(@class,'domik__title')]//a")
    public HtmlElement title;

    @Name("Иконка Конверт")
    @FindBy(xpath = TOPBAR_XPATH + "/a[contains(@class,'type_mail')]/img")
    public HtmlElement letterIcon;

    @Name("Текст о новых письмах")
    @FindBy(xpath = TOPBAR_XPATH + "/a[contains(@class,'type_mail')]")
    public HtmlElement letterText;

    @Name("Иконка Перо")
    @FindBy(xpath = TOPBAR_XPATH + "/a[contains(@class,'type_compose')]/img")
    public HtmlElement composeIcon;

    @Name("Текст 'Написать письмо'")
    @FindBy(xpath = TOPBAR_XPATH + "/a[contains(@class,'type_compose')]")
    public HtmlElement composeText;

    @Name("Иконка-стрелка'Свернуть'")
    @FindBy(xpath = ".//div[@class='b-topbar__toggler']/span/img")
    public HtmlElement foldIcon;

    @Name("Текст 'Свернуть'")
    @FindBy(xpath = ".//div[@class='b-topbar__toggler']/span/span")
    public HtmlElement foldText;
}

