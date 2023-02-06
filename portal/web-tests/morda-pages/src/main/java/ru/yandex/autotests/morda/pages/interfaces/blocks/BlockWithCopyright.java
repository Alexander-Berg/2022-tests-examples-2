package ru.yandex.autotests.morda.pages.interfaces.blocks;

import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
public interface BlockWithCopyright extends WrapsElement {
    HtmlElement getCopyright();
}
