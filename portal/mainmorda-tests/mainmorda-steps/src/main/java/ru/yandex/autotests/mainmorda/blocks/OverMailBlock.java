package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 12.07.12
 * Пространство над незалогинненым почтовым домиком(не включая текст 'настроить')
 */
@FindBy(xpath = "//div[contains(@class, 'b-topbar i-bem')]")
@Name("Пространство над незалогинненым почтовым домиком(не включая текст 'настроить')")
public class OverMailBlock extends HtmlElement {

    @Name("Ссылка 'Войти в почту' при полном домике")
    @FindBy(xpath = ".//div[contains(@class,'b-topbar__links')]/a[contains(@class,'b-topbar__switcher')]")
    public HtmlElement enterLink;

    @Name("Кнопка 'завести почту'")
    @FindBy(xpath = ".//div//a[contains(@class,'b-topbar__button')]")
    public HtmlElement createMailButton;

    @Name("Ссылка 'Выход'")
    @FindBy(xpath = ".//a[contains(@class,'logout')]")
    public HtmlElement exitLink;
}