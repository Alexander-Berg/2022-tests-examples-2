package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.common.blocks.Suggest;
import ru.yandex.autotests.morda.pages.common.blocks.VirtualKeyboardBlock;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.ImageLink;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithVirtualKeyboard;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordabackend.beans.bannerdebug.BrowserPromo;
import ru.yandex.autotests.mordabackend.beans.bannerundersearch.Value;
import ru.yandex.autotests.mordabackend.beans.servicestabs.ServicesTab;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.SearchBlock.BrowserPromoBlock.validateBrowserPromo;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.SearchBlock.SearchForm.SearchSample.validateSearchSample;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.SearchBlock.SearchForm.validateSearchForm;
import static ru.yandex.autotests.morda.pages.desktop.mainall.DesktopMainAllMorda.desktopMainAll;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldExistElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.steps.CheckSteps.url;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.VALUE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
@Name("Поисковый блок")
@FindBy(xpath = "//div[contains(@class, 'col') and contains(@class, 'home-arrow')]")
public class SearchBlock extends HtmlElement implements BlockWithSearchForm, BlockWithSuggest, Validateable<DesktopMainMorda>,
        BlockWithVirtualKeyboard<VirtualKeyboardBlock> {

    public SearchForm searchForm;
    private Suggest suggest;
    public BrowserPromoBlock browserPromoBlock;
    private VirtualKeyboardBlock virtualKeyboardBlock;

    @Name("Иконка клавиатуры")
    @FindBy(xpath = ".//div[contains(@class,' keyboard-loader')]/i")
    public HtmlElement virtualKeyboardButton;

    @Name("Поисковые табы")
    @FindBy(xpath = ".//div[contains(@class, 'home-tabs')]/a[contains(@class, 'home-tabs__link')]")
    public List<HtmlElement> allTabs;

    @Name("Ссылка \"Ещё\"")
    @FindBy(xpath = ".//a[contains(@class, 'home-tabs__more')]")
    public HtmlElement more;

    @Name("Табы \"Ещё\"")
    @FindBy(xpath = "//a[contains(@class, 'home-tabs__more-link')]")
    public List<HtmlElement> moreTabs;

    @Step("{0}")
    public static HierarchicalErrorCollector validateSearchTab(HtmlElement tab,
                                                               ServicesTab tabData,
                                                               Validator<? extends DesktopMainMorda> validator) {
        String tabText = getTranslation("home", "tabs", tabData.getId(), validator.getMorda().getLanguage());
        return collector()
                .check(shouldSeeElement(tab))
                .check(
                        shouldSeeElementMatchingTo(tab, allOfDetailed(
                                hasText(tabText),
                                hasAttribute(HREF, equalTo(url(tabData.getUrl(), validator.getMorda().getScheme())))
                        ))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateMore(HtmlElement more,
                                                          Validator<? extends DesktopMainMorda> validator) {
        String href = desktopMainAll(
                validator.getMorda().getScheme(),
                validator.getMorda().getEnvironment().getEnvironment(),
                validator.getMorda().getRegion()
        ).getUrl().toString();

        return collector()
                .check(shouldSeeElement(more))
                .check(shouldSeeElementMatchingTo(more, allOfDetailed(
                        hasText(getTranslation(Dictionary.Home.Tabs.MORE, validator.getMorda().getLanguage())),
                        hasAttribute(HREF, equalTo(href))
                )));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateSearchTabs(List<HtmlElement> allTabs,
                                                                Validator<? extends DesktopMainMorda> validator) {
        List<ServicesTab> allTabsData = validator.getCleanvars().getServicesTabs().getList();
        allTabsData.remove(0);

        HierarchicalErrorCollector collector = collector();

        for (int i = 0; i != Math.min(allTabs.size(), allTabsData.size()); i++) {
            collector.check(validateSearchTab(allTabs.get(i), allTabsData.get(i), validator));
        }

        HierarchicalErrorCollector countCollector = collector().check(
                shouldSeeElementMatchingTo(allTabs, hasSize(allTabsData.size()))
        );
        collector.check(countCollector);

        return collector;
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopMainMorda> validator) {
        return collector()
                .check(
//                        validateBrowserPromo(browserPromoBlock, validator),
                        validateSearchForm(searchForm, validator),
                        validateSearchTabs(allTabs, validator),
                        validateMore(more, validator)
                );
    }

    @Override
    public TextInput getSearchInput() {
        return searchForm.searchInput;
    }

    @Override
    public HtmlElement getSearchButton() {
        return searchForm.searchButton;
    }

    @Override
    public HtmlElement getLr() {
        return searchForm.lr;
    }

    @Override
    public HtmlElement getVirtualKeyboardButton() {
        return virtualKeyboardButton;
    }

    @Override
    public VirtualKeyboardBlock getVirtualKeyboardBlock() {
        return virtualKeyboardBlock;
    }

    @Override
    public HtmlElement getSuggest() {
        return suggest;
    }

    @Override
    public List<HtmlElement> getSuggestItems() {
        return suggest.items;
    }

    @Name("Поисковая форма")
    @FindBy(xpath = ".//form[contains(@class, 'suggest2-form')]")
    public static class SearchForm extends HtmlElement {

        @Name("Поисковая строка")
        @FindBy(xpath = ".//input[@name='text']")
        public TextInput searchInput;

        @Name("Параметр lr")
        @FindBy(xpath = ".//input[@name='lr']")
        public HtmlElement lr;

        @Name("Кнопка \"Найти\"")
        @FindBy(xpath = ".//button[contains(@type, 'submit')]")
        public HtmlElement searchButton;

        public SearchSample searchSample;

        @Step("{0}")
        public static HierarchicalErrorCollector validateSearchInput(TextInput searchInput, Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldSeeElement(searchInput));
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateLr(HtmlElement lr, Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(shouldExistElement(lr))
                    .check(shouldSeeElementMatchingTo(lr,
                            hasAttribute(VALUE, equalTo(validator.getMorda().getRegion().getRegionId()))));
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateSearchButton(HtmlElement searchButton, Validator<? extends DesktopMainMorda> validator) {
            String searchButtonText = getTranslation(Dictionary.Home.Main.SEARCH, validator.getMorda().getLanguage());
            return collector()
                    .check(shouldSeeElement(searchButton))
                    .check(shouldSeeElementMatchingTo(searchButton, hasText(searchButtonText)));
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateSearchForm(SearchForm searchForm, Validator<? extends DesktopMainMorda> validator) {
            return collector()
                    .check(
                            validateSearchInput(searchForm.searchInput, validator),
                            validateLr(searchForm.lr, validator),
                            validateSearchButton(searchForm.searchButton, validator),
                            validateSearchSample(searchForm.searchSample, validator)
                    );
        }

        @Name("Поисковый пример")
        @FindBy(xpath = ".//div[contains(@class, 'input__samples')]")
        public static class SearchSample extends HtmlElement {

            @Name("Текст \"Например\"")
            @FindBy(xpath = ".//span[contains(@class, 'sample-what')]")
            private HtmlElement forexample;

            @Name("Пример запроса")
            @FindBy(xpath = ".//span[contains(@class, 'link_gray_yes')]")
            private HtmlElement sample;

            public HtmlElement getSample() {
                return sample;
            }

            @Step("{0}")
            public static HierarchicalErrorCollector validateSearchSample(SearchSample searchSample, Validator<? extends DesktopMainMorda> validator) {
                String searchSampleText =
                        getTranslation("home", "search_form", "Find_everything", validator.getMorda().getLanguage()) +
                                ". " +
                                getTranslation(Dictionary.Home.Main.EXAMPLE, validator.getMorda().getLanguage()) +
                                ", ";

                return collector()
                        .check(shouldSeeElement(searchSample))
                        .check(
                                shouldSeeElementMatchingTo(searchSample, hasText(startsWith(searchSampleText)))
                        );
            }
        }
    }

    @Name("Промо браузера")
    @FindBy(xpath = ".//div[contains(@class, 'yabrowser-promo')]")
    public static class BrowserPromoBlock extends HtmlElement {

        @Name("Иконка браузера")
        @FindBy(xpath = ".//a[contains(@class, 'yabrowser-promo__icon-link')]")
        public ImageLink browserIcon;

        @Name("Текст промо")
        @FindBy(xpath = ".//a[not(contains(@class, 'yabrowser-promo__icon-link'))]")
        public HtmlElement text;

        @Step("{0}")
        public static HierarchicalErrorCollector validateText(HtmlElement text, Validator<? extends DesktopMainMorda> validator) {
            String linkText;
            String url;

            BrowserPromo value = validator.getCleanvars().getBannerDebug().getBanners().getLinkBro();
            if (value == null) {
                Value value1 = validator.getCleanvars().getBannerUndersearch().getValue();
                linkText = value1.getText1();
                url = value1.getClickCounter();
            } else {
                linkText = value.getText1();
                url = value.getUrl();
            }

            return collector()
                    .check(shouldSeeElement(text))
                    .check(shouldSeeElementMatchingTo(text, allOfDetailed(
                            hasText(linkText),
                            hasAttribute(HREF, equalTo(url))
                    )));
        }

        @Step("{0}")
        public static HierarchicalErrorCollector validateBrowserIcon(ImageLink browserIcon, Validator<? extends DesktopMainMorda> validator) {
            String imgUrl;
            BrowserPromo value = validator.getCleanvars().getBannerDebug().getBanners().getLinkBro();

            if (value == null) {
                imgUrl = validator.getCleanvars().getBannerUndersearch().getValue().getImg().getUrl();
            } else {
                imgUrl =  value.getImg().getUrl();
            }
            return collector()
                    .check(shouldSeeElement(browserIcon))
                    .check(
                            shouldSeeElement(browserIcon.img),
                            shouldSeeElementMatchingTo(browserIcon.img, hasAttribute(SRC, equalTo(imgUrl)))
                    );
        }

        @Step("Check browser promo")
        public static HierarchicalErrorCollector validateBrowserPromo(BrowserPromoBlock browserPromoBlock,
                                                                      Validator<? extends DesktopMainMorda> validator) {

            return collector()
                    .check(shouldSeeElement(browserPromoBlock))
                    .check(
                            validateBrowserIcon(browserPromoBlock.browserIcon, validator),
                            validateText(browserPromoBlock.text, validator)
                    );
        }
    }
}
