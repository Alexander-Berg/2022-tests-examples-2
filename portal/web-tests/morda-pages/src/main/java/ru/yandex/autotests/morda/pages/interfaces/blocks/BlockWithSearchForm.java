package ru.yandex.autotests.morda.pages.interfaces.blocks;

import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public interface BlockWithSearchForm extends WrapsElement {

    TextInput getSearchInput();

    HtmlElement getSearchButton();

    HtmlElement getLr();
}
