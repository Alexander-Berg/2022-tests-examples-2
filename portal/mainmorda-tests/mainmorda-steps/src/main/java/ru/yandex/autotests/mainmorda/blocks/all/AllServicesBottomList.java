package ru.yandex.autotests.mainmorda.blocks.all;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 26.02.2015.
 */
@Name("Блок с сервисами для бизнеса")
@FindBy(xpath = "//div[contains(@class,'b-line__services-bottom b-line__center')]")
public class AllServicesBottomList extends HtmlElement {
    @Name("Сервис #")
    @FindBy(xpath = ".//td/div[contains(@class,'services-big__wrapper')]")
    public List<ServiceItem> items;
}
