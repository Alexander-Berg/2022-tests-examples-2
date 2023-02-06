package ru.yandex.autotests.morda.monitorings.cleanvars;

import com.fasterxml.jackson.core.JsonProcessingException;
import org.apache.commons.lang3.StringUtils;
import org.junit.Assume;
import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Rule;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.monitorings.MordaMonitoringsProperties;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.monitoring.MonitoringNotifierRule;

import javax.ws.rs.core.UriBuilder;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.RandomStringUtils.random;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.qatools.monitoring.MonitoringNotifierRule.notifierRule;

/**
 * User: asamar
 * Date: 19.09.16
 */
public abstract class BaseCleanvarsMonitoring<T> {
    public static final MordaMonitoringsProperties CONFIG = new MordaMonitoringsProperties();

    @Rule
    @ClassRule
    public static MonitoringNotifierRule notifierRule = notifierRule()
            .around(new AllureLoggingRule());
    protected MordaCleanvars cleanvars;
    protected Morda<?> morda;

    public BaseCleanvarsMonitoring(Morda<?> morda) {
        this.morda = morda;
    }

    private static String addRandomHashToUrl(String url) {
        return UriBuilder.fromUri(url).queryParam(
                "test_request_id", random(10, true, true) + "." + System.currentTimeMillis())
                .build()
                .toASCIIString();
    }

    public boolean addRandomHash() {
        return true;
    }

    public abstract MordaCleanvarsBlock getBlockName();

    public abstract T getBlock();

    public abstract int getShow();

    public abstract Set<String> getUrlsToPing(MordaCleanvars cleanvars);

    @Before
    public void init() throws JsonProcessingException {
        this.cleanvars = new MordaClient().cleanvars(morda, getBlockName()).read();
    }

    @Stories("block")
    public void exists() {
        assertThat("Блок " + this.getBlockName() + " отсутствует", this.getBlock(), notNullValue());
        assertThat("Блок " + this.getBlockName() + " отсутствует", this.getShow(), equalTo(1));
    }

    @Stories("pings")
    public void pings(String signal) {
        Assume.assumeTrue("Блок отсутствует", this.getShow() == 1);

        Set<String> urls = getUrlsToPing(cleanvars);

        urls.remove(null);

        if (addRandomHash()) {
            urls = urls.stream()
                    .map(e -> !e.contains("yandex.net") && !e.contains("/clck/") ? addRandomHashToUrl(e) : e)
                    .collect(Collectors.toSet());
        }

        List<LinkUtils.PingResult> pingResults = LinkUtils.ping(urls, morda);
        List<LinkUtils.PingResult> failedRequests = LinkUtils.getFailedRequests(pingResults);

        List<String> badCodes = failedRequests.stream()
                .filter(e -> !e.isError())
                .map(LinkUtils.PingResult::toString)
                .collect(toList());


        notifierRule.yasm().addToSignal(String.format(signal, "total"), pingResults.size());
        notifierRule.yasm().addToSignal(String.format(signal, "failed"), failedRequests.size());

        assertThat(StringUtils.join(badCodes, ", "), failedRequests, hasSize(0));
    }
}
