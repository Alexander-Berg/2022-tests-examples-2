package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;

/**
 * User: asamar
 * Date: 29.12.2015.
 */

//@FindBy(xpath = "//div[contains(@id, 'wd-')][.//h1[contains(@class, 'b-widget__title_type_rss')]]")
@FindBy(xpath = "//div[contains(@id, 'wd-')][./h1]")//[.//div[contains(@class, 'w-rss_type')]]")
public class RssBlock extends Widget<RssSettingsBlock> implements Validateable<DesktopMainMorda> {

    public RssSettingsBlock rssSettingsBlock;

    @Override
    protected RssSettingsBlock getSetupPopup(){
        return rssSettingsBlock;
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector();
    }
}
