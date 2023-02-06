package ru.yandex.autotests.morda.pages.interfaces.pages;

import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public interface PageWithLoginDomik<T extends HtmlElement> {
    T getLoginDomik();

    @Step("Open logon domik")
    void openLoginDomik();
}
