package ru.yandex.autotests.morda.pages.interfaces.blocks;

import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24/03/15
 */
public interface TabWithIcon extends WrapsElement, Tab {
    HtmlElement getTabIcon();
}
