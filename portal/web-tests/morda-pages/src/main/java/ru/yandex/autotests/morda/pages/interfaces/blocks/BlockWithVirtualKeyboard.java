package ru.yandex.autotests.morda.pages.interfaces.blocks;

import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public interface BlockWithVirtualKeyboard<T> extends WrapsElement, BlockWithSearchForm {
    HtmlElement getVirtualKeyboardButton();
    T getVirtualKeyboardBlock();
}
