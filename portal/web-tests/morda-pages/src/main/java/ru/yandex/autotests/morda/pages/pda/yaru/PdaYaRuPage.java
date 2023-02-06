package ru.yandex.autotests.morda.pages.pda.yaru;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.pda.yaru.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.pda.yaru.blocks.SearchBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class PdaYaRuPage implements PageWithLogo<LogoBlock>, PageWithSearchBlock<SearchBlock> {

    public PdaYaRuPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    private LogoBlock logoBlock;
    private SearchBlock searchBlock;

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public SearchBlock getSearchBlock() {
        return searchBlock;
    }
}
