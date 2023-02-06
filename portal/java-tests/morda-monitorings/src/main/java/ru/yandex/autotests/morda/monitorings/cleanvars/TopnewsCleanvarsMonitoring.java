package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.topnews.Topnews;
import ru.yandex.autotests.morda.beans.cleanvars.topnews.TopnewsTabItem;
import ru.yandex.autotests.morda.monitorings.MonitoringsData;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.junit.Assert.assertThat;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.TOPNEWS;
import static ru.yandex.autotests.morda.pages.hw.DesktopHwBmwMorda.desktopHwBmw;
import static ru.yandex.autotests.morda.pages.hw.DesktopHwLgMorda.desktopHwLg;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.main.PdaMainMorda.pdaMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.autotests.morda.pages.tv.TvSmartMorda.tvSmart;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 16.09.16
 */
@Aqua.Test(title = "Topnews cleanvars monitoring")
@Features("Topnews")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_topnews")
public class TopnewsCleanvarsMonitoring extends BaseCleanvarsMonitoring<Topnews> {
    public TopnewsCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        for (GeobaseRegion region : MonitoringsData.NEWS_REGIONS) {
            for (MordaLanguage language : MordaLanguage.getKUBRLanguages()) {
                data.add(desktopMain(env).region(region).language(language));
                data.add(touchMain(env).region(region).language(language));
                data.add(pdaMain(env).region(region).language(language));

            }

            if (!region.getKubrDomain().equals(".ua")) {
                data.add(desktopHwBmw(env).region(region));
                data.add(desktopHwLg(env).region(region));
            }

            data.add(tvSmart(env).region(region));
        }

        return data;
    }

    @Override
    public Topnews getBlock() {
        return cleanvars.getTopnews();
    }

    @Override
    public int getShow() {
        return getBlock().getShow();
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return TOPNEWS;
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_topnews_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_topnews_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_topnews_ping_%s_tttt");
    }

    @Test
    @GolemEvent("morda_tabs_size")
    @YasmSignal(signal = "morda_topnews_tabs_size_%s_tttt")
    public void eventsCount() {
        assumeThat(getShow(), equalTo(1));
        Topnews topnews = cleanvars.getTopnews();
        List<Integer> tabSizes = topnews.getTabs().stream()
                .filter(e -> e.getDelayedContent() != 1)
                .map(e -> e.getNews().size()).collect(toList());

        assertThat(tabSizes, everyItem(equalTo(5)));
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> urls = new HashSet<>();
        Topnews topnews = cleanvars.getTopnews();

        urls.add(topnews.getHref());

        topnews.getTabs().forEach(tab -> {
            urls.add(tab.getHref());
            urls.addAll(tab.getNews().stream().map(TopnewsTabItem::getHref).collect(toList()));

        });

        return urls;
    }
}
