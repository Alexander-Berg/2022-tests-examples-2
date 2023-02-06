package ru.yandex.autotests.mordacom.pages;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff
 * Date: 16.11.12
 */
@FindBy(xpath = "//div[contains(concat(' ', @class, ' '), ' b-line__bar ')]")
@Name("Header")
public class HeaderBlock extends HtmlElement {

    @Name("Ссылка на паспорт с логином пользователем")
    @FindBy(xpath = ".//div[contains(@class, 'b-line__bar__right')]/a[@class='link user']")
    public HtmlElement loginNameLink;

    @Name("Ссылка почты")
    @FindBy(xpath = ".//div[contains(@class, 'b-line__bar__right')]/a[@tabindex='3']")
    public HtmlElement mailLink;

    @Name("Ссылка выхода")
    @FindBy(xpath = ".//div[contains(@class, 'b-line__bar__right')]/a[contains(@class, 'user__exit')]")
    public HtmlElement exitLink;

    @Name("Переключалка языка")
    @FindBy(xpath = ".//div[contains(@class, 'langswitch')]/span[contains(@class, 'dropdown-menu__switcher')]")
    public HtmlElement languageSwitcher;

    @Name("Попап переключалки языков")
    public LangSwitcherPopupBlock languageSwitcherPopup;

}
