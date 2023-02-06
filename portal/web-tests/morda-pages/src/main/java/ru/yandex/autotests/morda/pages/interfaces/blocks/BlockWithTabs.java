package ru.yandex.autotests.morda.pages.interfaces.blocks;

import org.openqa.selenium.internal.WrapsElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public interface BlockWithTabs<T> extends WrapsElement, BlockWithSearchForm {
    List<? extends T> getSearchTabs();
}
