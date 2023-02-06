package ru.yandex.autotests.morda.monitorings;

import org.apache.commons.lang3.StringUtils;
import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.com.DesktopCom404Morda;
import ru.yandex.autotests.morda.pages.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.com.PdaComMorda;
import ru.yandex.autotests.morda.pages.com.TouchComMorda;
import ru.yandex.autotests.morda.pages.comtr.DesktopComTrAllMorda;
import ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda;
import ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.DesktopFamilyComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.PdaComTrAllMorda;
import ru.yandex.autotests.morda.pages.comtr.PdaComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.TouchComTrAllMorda;
import ru.yandex.autotests.morda.pages.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.pages.comtr.TouchComTrWpMorda;
import ru.yandex.autotests.morda.pages.hw.DesktopHwBmwMorda;
import ru.yandex.autotests.morda.pages.hw.DesktopHwLgMorda;
import ru.yandex.autotests.morda.pages.hw.DesktopHwLgV2Morda;
import ru.yandex.autotests.morda.pages.main.DesktopFamilyMainMorda;
import ru.yandex.autotests.morda.pages.main.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.main.DesktopMain404Morda;
import ru.yandex.autotests.morda.pages.main.DesktopMainAllMorda;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.PdaMainAllMorda;
import ru.yandex.autotests.morda.pages.main.PdaMainMorda;
import ru.yandex.autotests.morda.pages.main.TelMainMorda;
import ru.yandex.autotests.morda.pages.main.TouchMainAllMorda;
import ru.yandex.autotests.morda.pages.main.TouchMainMorda;
import ru.yandex.autotests.morda.pages.main.TouchMainWpMorda;
import ru.yandex.autotests.morda.pages.spok.SpokMorda;
import ru.yandex.autotests.morda.pages.tv.TvSmartMorda;
import ru.yandex.autotests.morda.pages.yaru.DesktopYaruMorda;
import ru.yandex.autotests.morda.pages.yaru.PdaYaruMorda;
import ru.yandex.autotests.morda.pages.yaru.TouchYaruMorda;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.monitoring.MonitoringNotifierRule;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.ListIterator;
import java.util.Set;

import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toSet;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static ru.yandex.autotests.morda.steps.html.HtmlUtils.getAllLinksFromHtml;
import static ru.yandex.qatools.monitoring.MonitoringNotifierRule.notifierRule;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 19/07/16
 */
@Aqua.Test(title = "Пинги ссылок с морды")
@Features("Ping Morda Links")
@RunWith(Parameterized.class)
//@GolemObject("portal_yandex_pings")
public class PingLinksMonitoring {
    private static final MordaMonitoringsProperties CONFIG = new MordaMonitoringsProperties();

    @Rule
    @ClassRule
    public static MonitoringNotifierRule notifierRule = notifierRule()
            .around(new AllureLoggingRule());

    protected Morda<?> morda;
    protected Set<String> urls;

    public PingLinksMonitoring(Morda<?> morda, Set<String> urls) {
        this.morda = morda;
        this.urls = urls;
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        MordaClient mordaClient = new MordaClient();
        List<Object[]> data = new ArrayList<>();
        List<Morda<?>> mordas = new ArrayList<>();
        
        //main
        mordas.addAll(DesktopFamilyMainMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopFirefoxMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopMain404Morda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopMainAllMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopMainMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(PdaMainMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(PdaMainAllMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(TelMainMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(TouchMainMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(TouchMainAllMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(TouchMainWpMorda.getDefaultList(CONFIG.getEnvironment()));

        //com
        mordas.addAll(DesktopComMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopCom404Morda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(PdaComMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(TouchComMorda.getDefaultList(CONFIG.getEnvironment()));

        //comtr
        mordas.addAll(DesktopComTrAllMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopComTrFootballMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopComTrMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopFamilyComTrMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(PdaComTrMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(PdaComTrAllMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(TouchComTrMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(TouchComTrAllMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(TouchComTrWpMorda.getDefaultList(CONFIG.getEnvironment()));

        //hw
        mordas.addAll(DesktopHwLgMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopHwBmwMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(DesktopHwLgV2Morda.getDefaultList(CONFIG.getEnvironment()));

        //tv
        mordas.addAll(TvSmartMorda.getDefaultList(CONFIG.getEnvironment()));

        //yaru
        mordas.addAll(DesktopYaruMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(PdaYaruMorda.getDefaultList(CONFIG.getEnvironment()));
        mordas.addAll(TouchYaruMorda.getDefaultList(CONFIG.getEnvironment()));

        //spok
        mordas.addAll(SpokMorda.getDefaultSpokList(CONFIG.getEnvironment()));

        for (Morda<?> morda : mordas) {
            data.add(new Object[]{morda, getLinks(mordaClient, morda)});
        }

        return data;
    }

    public static Set<String> getLinks(MordaClient mordaClient, Morda<?> morda) {
        String html = mordaClient.morda(morda).readAsResponse().getBody().asString();
        Set<String> links = getAllLinksFromHtml(html).stream()
                .filter(e -> !e.contains("/clck/"))
                .filter(e -> !e.contains("yabs.yandex."))
                .filter(e -> !e.contains("tv.yandex"))
                .collect(toSet());

        links = normalizeIfLg(morda, links);
        links = normalizeIfBmw(morda, links);
        links = normalizeOther(morda, links);
        return links;
    }

    @Test
    @YasmSignal(signal = "morda_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void ping() {
        List<LinkUtils.PingResult> pingResults = LinkUtils.ping(urls, morda);
        List<LinkUtils.PingResult> failedRequests = LinkUtils.getFailedRequests(pingResults);

        List<String> badCodes = failedRequests.stream()
                .filter(e -> !e.isError())
                .map(LinkUtils.PingResult::toString)
                .collect(toList());

        notifierRule.yasm().addToSignal("morda_ping_total_tttt", urls.size());
        notifierRule.yasm().addToSignal("morda_ping_failed_tttt", failedRequests.size());

        assertThat(StringUtils.join(badCodes, ", "), failedRequests, hasSize(0));
    }

    private static Set<String> normalizeIfBmw(Morda<?> morda, Set<String> urls) {
        if (morda.getMordaType() == MordaType.DESKTOP_HW_BMW) {

            List<String> list = new ArrayList<>(urls);
            ListIterator<String> litr = list.listIterator();

            while (litr.hasNext()) {
                String next = litr.next();
                if (next.startsWith("/bmw")) {
                    litr.add(morda.getScheme() + "://" + morda.getUrl().getHost() + next);
                }
            }
            list.removeIf(e -> e.startsWith("/bmw"));
            return new HashSet<>(list);
        }

        return urls;
    }

    private static Set<String> normalizeIfLg(Morda<?> morda, Set<String> urls) {
        if (morda.getMordaType() == MordaType.DESKTOP_HW_LG_2) {
            List<String> paths = urls.stream()
                    .filter(e -> e.startsWith("js/") || e.startsWith("css/") || e.startsWith("img/") || e.startsWith("city"))
                    .collect(toList());
            paths.forEach(e -> urls.add(morda.getUrl() + "/" + e));
            urls.removeIf(e -> e.startsWith("img/"));
            urls.removeIf(e -> e.startsWith("css/"));
            urls.removeIf(e -> e.startsWith("js/"));
            urls.removeIf(e -> e.startsWith("city/"));
        }
        return urls;
    }

    private static String encode(String url) {
        return url.replace("|", "%7c").replaceAll("\\*", "%2A");
    }

    private static Set<String> normalizeOther(Morda<?> morda, Set<String> urls) {
        Set<String> newUrls = urls.stream()
                .map(PingLinksMonitoring::encode)
                .collect(toSet());

        newUrls.removeIf(""::equals);
        newUrls.removeIf("#"::equals);

        //написал на yaca-bug(yaca-2907)
        newUrls.removeIf(e -> e.contains("pda.yaca.yandex."));

        //падает из-за якоря
//        newUrls.removeIf(e -> e.contains("/clck/redir/dtype"));

        return newUrls;
    }

}
