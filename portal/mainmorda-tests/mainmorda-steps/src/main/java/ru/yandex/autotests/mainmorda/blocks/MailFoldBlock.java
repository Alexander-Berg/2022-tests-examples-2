package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 17.05.12
 * Свёрнутый залогиненный домик
 */
@FindBy(xpath = "//div [@class='b-inline b-top-bar__item b-topbar__body']" +
        "[not(a[@class='b-link i-bem b-topbar__title'])]")
@Name("Домик свёрнутый")
public class MailFoldBlock extends HtmlElement {
    @Name("Ссылка 'Войти в почту' внутри свёрнутого незалогинового домика")
    @FindBy(xpath = ".//a")
    public HtmlElement loginLink;

    @Name("Кнопка-стрелка 'Развернуть'")
    @FindBy(xpath = ".//span[contains(@class,'b-topbar__toggler')]")
    public HtmlElement expandButton;

    @Name("Иконка-стрелка 'Развернуть'")
    @FindBy(xpath = ".//span[contains(@class,'b-topbar__toggler')]/img")
    public HtmlElement expandIcon;
}