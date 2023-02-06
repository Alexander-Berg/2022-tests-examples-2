package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 17.05.12
 * Свёрнутый залогиненный домик
 */
@FindBy(xpath = "//div[contains(@class,'b-inline b-topbar__body')]")
@Name("Домик залогиновый свёрнутый")
public class MailLoggedFoldBlock extends HtmlElement {
    @Name("Ссылка Почта")
    @FindBy(xpath = ".//a[contains(@class,'b-topbar__title')]")
    public HtmlElement title;

    @Name("Иконка Конверт")
    @FindBy(xpath = ".//a[contains(@class,'type_mail')]/img")
    public HtmlElement letterIcon;

    @Name("Текст о новых письмах")
    @FindBy(xpath = ".//a[contains(@class,'type_mail')]")
    public HtmlElement letterText;

    @Name("Иконка Перо")
    @FindBy(xpath = ".//a[contains(@class,'type_compose')]/img")
    public HtmlElement composeIcon;

    @Name("Текст 'Написать письмо'")
    @FindBy(xpath = ".//a[contains(@class,'type_compose')]")
    public HtmlElement composeText;

    @Name("Кнопка-стрелка'Развернуть'")
    @FindBy(xpath = ".//span[contains(@class,'b-topbar__toggler')]")
    public HtmlElement expandButton;

    @Name("Иконка-стрелка'Развернуть'")
    @FindBy(xpath = ".//span[contains(@class,'b-topbar__toggler')]/img")
    public HtmlElement expandIcon;
}
