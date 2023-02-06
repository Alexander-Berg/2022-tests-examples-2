package ru.yandex.autotests.turkey.pages;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.turkey.blocks.SerpSearchBlock;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
public class SerpComTrPage {
    public SerpComTrPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Поисковая форма")
    public SerpSearchBlock arrow;
}
