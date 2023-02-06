package ru.yandex.autotests.morda.pages.touch.ru.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: asamar
 * Date: 16.06.16
 */
@Name("Промо скина")
@FindBy(xpath = "//div[contains(@class,'skin-greeting ')]")
public class SkinGreetingBlock extends HtmlElement implements Validateable<TouchRuMorda> {


    @Name("Заголовок")
    @FindBy(xpath = ".//div[contains(@class,'skin-greeting__title')]")
    public HtmlElement title;

    @Name("Ссылка на тюн")
    @FindBy(xpath = ".//a[contains(@class,'skin-greeting__notice')]")
    public HtmlElement tuneLink;


    @Override
    public HierarchicalErrorCollector validate(Validator<? extends TouchRuMorda> validator) {
        return null;
    }
}
