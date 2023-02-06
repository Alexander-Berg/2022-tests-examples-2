package ru.yandex.autotests.mordacom.pages;

import org.openqa.selenium.WebDriver;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
public class SerpComPage {
    public SerpComPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Поисковая форма")
    public SerpSearchBlock arrow;
}
