package ru.yandex.autotests.morda.pages.interfaces.pages;

import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public interface PageWithHeader<T extends HtmlElement> {
    T getHeaderBlock();
}
