package ru.yandex.autotests.morda.monitorings;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.lang3.StringUtils;
import org.hamcrest.Matcher;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.RuleChain;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.rules.monitorings.BottleMessageAttachmentRule;
import ru.yandex.autotests.morda.steps.links.LinkUtils;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static junit.framework.TestCase.fail;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;

/**
 * User: asamar
 * Date: 05.10.16
 */
public abstract class BaseSearchApiMonitoring<Block> {
    protected static final MordaMonitoringsProperties CONFIG = new MordaMonitoringsProperties();
    private BottleMessageAttachmentRule bottleMessageAttachmentRule = new BottleMessageAttachmentRule();

    @Rule
    public RuleChain rules = RuleChain.outerRule(new AllureLoggingRule())
            .around(bottleMessageAttachmentRule);

//    {
//        if (CONFIG.toNotify()) {
//            rules.around(bottleMessageAttachmentRule);
//        }
//    }

    protected MainMorda<?> morda;
    protected Block block;

    public BaseSearchApiMonitoring(MainMorda<?> morda) {
        this.morda = morda;
    }

    protected abstract Block getSearchApiBlock();
    protected abstract SearchApiBlock getSearchApiBlockName();
    protected abstract List<String> getSearchApiNames();
    protected abstract List<String> getSearchApiUrls();


    @Before
    public void init() throws JsonProcessingException {
        block = getSearchApiBlock();
        bottleMessageAttachmentRule.addMeta(getSearchApiBlockName().getValue(),
                new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(block));
    }

    @Test
    public void names() {
        getSearchApiNames().forEach(name ->
                assertThat("Нет названия/данных", name, not(isEmptyOrNullString())));
    }

    @Test
    public void pings() {
        List<String> urls = getSearchApiUrls();
        List<LinkUtils.PingResult> pingResults = LinkUtils.ping(urls);
        List<LinkUtils.PingResult> failedRequests = LinkUtils.getFailedRequests(pingResults);

        bottleMessageAttachmentRule.addMeta("FailedRequests", StringUtils.join(failedRequests, ", "));

        List<String> badCodes = failedRequests.stream()
                .filter(e -> !e.isError())
                .map(LinkUtils.PingResult::toString)
                .collect(toList());

        check(StringUtils.join(badCodes, ", "), failedRequests, hasSize(0));
    }

    protected <V> void check(String error, V value, Matcher<? super V> matcher) {
        String packUrl = "https://aqua.yandex-team.ru/#/build-report/" + System.getProperty("aero.launch.uuid");
        try {
            Assert.assertThat(error + " " + packUrl, value, matcher);
        } catch (Throwable e) {
            fail(e.getMessage() + " " + packUrl);
        }
    }
}
