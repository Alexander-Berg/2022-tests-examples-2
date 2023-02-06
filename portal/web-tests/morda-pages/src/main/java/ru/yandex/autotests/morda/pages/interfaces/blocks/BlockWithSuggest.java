package ru.yandex.autotests.morda.pages.interfaces.blocks;

import org.openqa.selenium.internal.WrapsElement;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public interface BlockWithSuggest extends WrapsElement, BlockWithSearchForm{
    HtmlElement getSuggest();

    List<HtmlElement> getSuggestItems();
}
