package ru.yandex.autotests.widgets.search;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.widgets.Properties;
import ru.yandex.autotests.widgets.pages.WidgetPage;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Arrays;
import java.util.Collection;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.autotests.widgets.data.AllWidgetsData.WIDGETS_PATTERN;
import static ru.yandex.autotests.widgets.data.SearchData.Category;

/**
 * User: leonsabr
 * Date: 08.11.11
 * Корректное число тегов в каталоге.
 */
@Aqua.Test(title = "Число рубрик и тегов в каталоге")
@Features("Search")
@RunWith(Parameterized.class)
public class RubricsNumberTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private WidgetPage widgetPage = new WidgetPage(driver);

    @Parameterized.Parameters
    public static Collection<Object[]> testData() {
        return convert(Arrays.asList(RU, UA, BY, KZ));
    }

    private Domain domain;

    public RubricsNumberTest(Domain domain) {
        this.domain = domain;
    }

    @Before
    public void setUp() {
        String url = String.format(WIDGETS_PATTERN, CONFIG.getMordaEnv(), domain);
        user.opensPage(url, startsWith(url));
    }

    @Test
    public void categoriesNumber() {
        user.shouldSeeListWithSize(widgetPage.commonCategories,
                equalTo(Category.values().length));
    }

    @Test
    public void tagsNumber() {
        user.shouldSeeListWithSize(widgetPage.allTags,
                equalTo(CONFIG.getTagsNumber()));
    }
}
