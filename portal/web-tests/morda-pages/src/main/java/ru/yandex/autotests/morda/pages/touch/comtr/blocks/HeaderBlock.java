package ru.yandex.autotests.morda.pages.touch.comtr.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithLocateIcon;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithLoginLink;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithRegionName;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithUsername;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.header.RegionBlock;
import ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.header.UserBlock;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Хедер")
@FindBy(xpath = "//div[contains(@class, 'content__head')]")
public class HeaderBlock extends HtmlElement implements BlockWithRegionName, BlockWithLocateIcon,
        BlockWithUsername, BlockWithLoginLink, Validateable<TouchComTrMorda> {

    public RegionBlock regionBlock;
    public UserBlock userBlock;

    @Override
    public HtmlElement getLocateIcon() {
        return regionBlock.getLocateIcon();
    }

    @Override
    public HtmlElement getRegionBlock() {
        return regionBlock.getRegionBlock();
    }

    @Override
    public HtmlElement getLoginLink() {
        return userBlock.getLoginLink();
    }

    @Override
    public HtmlElement getUsername() {
        return userBlock.getUsername();
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(
                        regionBlock.validate(validator),
                        userBlock.validate(validator)
                );
    }
}
