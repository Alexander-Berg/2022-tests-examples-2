package ru.yandex.autotests.morda.pages.common.blocks;

import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: leonsabr
 * Date: 09.10.12
 */
@FindBy(xpath = "//div[@class='b-keyboard-popup']")
@Name("Virtual Keyboard")
public class VirtualKeyboardBlock extends HtmlElement {
    @Name("переключатель языка")
    @FindBy(xpath = "//div[contains(@class,'b-keyboard__lang-i')]//span[contains(@class,'dropdown-menu__switcher')]")
    public HtmlElement switcher;

    @Name("закрыть клавиатуру")
    @FindBy(xpath = ".//span[contains(@class,'b-keyboard-popup__close')]")
    public HtmlElement close;

    @Name("Выпадушка выбора языка клавиатуры")
    @FindBy(xpath = "//div[contains(@class, 'popup__content')]//div[contains(@class, 'b-menu-vert b-keyboard__langs')]")
    public HtmlElement allLanguagesPopup;


    @Name("все языки клавиатуры")
    @FindBy(xpath = "//ul[@class='b-menu-vert__layout']//span[contains(@class, 'b-lang-switcher__lang')]")
    public List<HtmlElement> allLanguages;

    @Name("Кнопки")
    @FindBy(xpath = ".//table[@class='b-keyboard__row'][position() < 5]//td[position() > 1 and position() < 13]" +
            "//span[@class='b-keyboard__key-m']")
    public List<WebElement> buttons;

    @Name("Все кнопки")
    @FindBy(xpath = ".//div[contains(@class, 'b-keyboard_js_inited')]//span[@class='b-keyboard__key']" +
            "//span[@class='b-keyboard__key-m']")
    public List<HtmlElement> allButtons;

    @Name("Кнопка 'Ввод'")
    @FindBy(xpath = ".//table[@class='b-keyboard__row']//span[contains(@class, 'b-keyboard__key_special-enter')]" +
            "//span[@class='b-keyboard__key-m']")
    public HtmlElement enter;
}
