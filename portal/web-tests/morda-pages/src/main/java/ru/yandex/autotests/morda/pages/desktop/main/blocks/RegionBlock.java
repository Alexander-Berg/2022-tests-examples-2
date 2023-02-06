package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.IconLink;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.geo.Geo;
import ru.yandex.autotests.mordabackend.beans.geo.GeoItem;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static java.lang.String.format;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldNotSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Maps.REG_TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Name("Региональный блок")
@FindBy(xpath = "//div[@class='region']")
public class RegionBlock extends HtmlElement implements Validateable<DesktopMainMorda> {

    public RegionHeader regionHeader;

    @Name("Региональные ссылки")
    @FindBy(xpath = ".//a[contains(@class, 'region__link')]")
    public List<HtmlElement> regionLinks;

    @Step("{0}")
    public static HierarchicalErrorCollector validateRegionLink(HtmlElement link, GeoItem geoItem, Validator<? extends DesktopMainMorda> validator) {
        if (geoItem.getService().equals("informer")) {
            return collector()
                    .check(shouldSeeElement(link))
                    .check(
                            shouldSeeElementMatchingTo(link, allOfDetailed(
                                    hasText(geoItem.getText()),
                                    hasAttribute(HREF, equalTo(
                                                    url(geoItem.getUrl(), validator.getMorda().getScheme())
                                                            .replace("&amp;", "&"))
                                    )
                            ))
                    );
        } else {
            String text = getTranslation("home", "region_links", format("%s.title", geoItem.getService()),
                    validator.getMorda().getLanguage());

            return collector()
                    .check(shouldSeeElement(link))
                    .check(
                            shouldSeeElementMatchingTo(link, allOfDetailed(
                                    hasText(text),
                                    hasAttribute(HREF, equalTo(
                                                    url(geoItem.getUrl(), validator.getMorda().getScheme())
                                                            .replace("&amp;", "&"))
                                    )
                            ))
                    );
        }
    }

    @Step("Check region links")
    public HierarchicalErrorCollector validateRegionLinks(Validator<? extends DesktopMainMorda> validator) {
        Geo geoData = validator.getCleanvars().getGeo();
        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(regionLinks.size(), geoData.getList().size()); i++) {
            collector.check(validateRegionLink(regionLinks.get(i), geoData.getList().get(i), validator));
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(regionLinks, hasSize(geoData.getList().size()))
        );
        collector.check(countCollector);

        return collector;
    }

    @Override
    @Step("Check region block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        regionHeader.validate(validator),
                        validateRegionLinks(validator)
                );
    }

    @Name("Хедер регионального блока")
    @FindBy(xpath = ".//h1")
    public static class RegionHeader extends HtmlElement implements Validateable<DesktopMainMorda> {

        @Name("Заголовок")
        @FindBy(xpath = ".//a[2]")
        public HtmlElement title;

        @Name("Шестеренка настройки")
        @FindBy(xpath = ".//a[1]")
        public IconLink settingsIcon;

        @Step("{0}")
        public static HierarchicalErrorCollector validateTitle(HtmlElement title, Validator<? extends DesktopMainMorda> validator) {
            Geo geoData = validator.getCleanvars().getGeo();
            return collector()
                    .check(shouldSeeElement(title))
                    .check(
                            shouldSeeElementMatchingTo(title, allOfDetailed(
                                    hasText(format(getTranslation(REG_TITLE, validator.getMorda().getLanguage()), geoData.getMaps().getObj().getName())),
                                    hasAttribute(HREF, equalTo(url(geoData.getMaps().getObj().getUrl(), validator.getMorda().getScheme())))
                            ))
                    );
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateSettingsIcon(IconLink settingsIcon, Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldNotSeeElement(settingsIcon));
        }

        @Override
        @Step("Check region header")
        public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(this))
                    .check(
                            validateTitle(title, validator),
                            validateSettingsIcon(settingsIcon, validator)
                    );
        }
    }
}
