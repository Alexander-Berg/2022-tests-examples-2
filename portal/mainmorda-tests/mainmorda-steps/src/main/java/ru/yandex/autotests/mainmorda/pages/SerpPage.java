package ru.yandex.autotests.mainmorda.pages;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.blocks.SerpSearchBlock;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
public class SerpPage {
    public SerpPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Поисковая форма")
    public SerpSearchBlock search;
}
