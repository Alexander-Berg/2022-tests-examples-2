package ru.yandex.autotests.morda.tests.htmlcontent;

import org.apache.commons.lang3.StringUtils;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.morda.MordaPagesProperties;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.attach.AttachmentUtils;
import ru.yandex.autotests.morda.steps.html.HtmlUtils;

import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasSize;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/07/16
 */
@RunWith(Parameterized.class)
public abstract class AbstractHtmlContentTest {
    protected static final MordaPagesProperties CONFIG = new MordaPagesProperties();

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    protected Supplier<String> htmlSupplier;
    protected String html;

    public AbstractHtmlContentTest(Supplier<String> htmlSupplier) {
        this.htmlSupplier = htmlSupplier;
    }

    @Before
    public void attachHtml() {
        this.html = htmlSupplier.get();

        AttachmentUtils.attachHtmlAsText("page_content.info", this.html);
    }

    @Test
    public void htmlIsGood() {
        Map<String, List<String>> badParts = HtmlUtils.getBadHtmlParts(html);

        badParts.entrySet().forEach(e -> AttachmentUtils.attachText(e.getKey(), e.getValue()));

        assertThat("Found bad substrings: " + StringUtils.join(badParts.keySet(), ", "), badParts.entrySet(), hasSize(0));
    }

}
