package ru.yandex.autotests.morda.monitorings.cleanvars;

import com.fasterxml.jackson.core.JsonProcessingException;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.stocks.Lite;
import ru.yandex.autotests.morda.beans.cleanvars.stocks.Stocks;
import ru.yandex.autotests.morda.beans.cleanvars.stocks.StocksBlock;
import ru.yandex.autotests.morda.beans.cleanvars.stocks.StocksRow;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.STOCKS;
import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.TOPNEWS;
import static ru.yandex.autotests.morda.monitorings.MonitoringsData.STOCKS_REGIONS;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda.FootballClub.BJK;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda.FootballClub.GS;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda.desktopComTrFoot;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.comtr.PdaComTrMorda.pdaComTr;
import static ru.yandex.autotests.morda.pages.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.morda.pages.hw.DesktopHwBmwMorda.desktopHwBmw;
import static ru.yandex.autotests.morda.pages.hw.DesktopHwLgMorda.desktopHwLg;
import static ru.yandex.autotests.morda.pages.main.DesktopFirefoxMorda.desktopFirefox;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.main.PdaMainMorda.pdaMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.autotests.morda.pages.tv.TvSmartMorda.tvSmart;
import static ru.yandex.geobase.regions.Turkey.ISTANBUL_11508;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.BROKEN;
import static ru.yandex.qatools.monitoring.TestCaseResult.Status.SKIPPED;

/**
 * User: asamar
 * Date: 16.09.16
 */
@Aqua.Test(title = "Stocks cleanvars monitoring")
@Features("Stocks")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_stocks")
public class StocksCleanvarsMonitoring extends BaseCleanvarsMonitoring<MordaCleanvars> {
    public StocksCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        STOCKS_REGIONS.forEach(region -> {
            data.add(desktopMain(env).region(region));
            data.add(touchMain(env).region(region));
            data.add(pdaMain(env).region(region));
            data.add(tvSmart(env).region(region));
            data.add(desktopFirefox(MordaDomain.RU, env).region(region));
            if (region.getKubrDomain().equals(".ua")) {
                data.add(desktopFirefox(MordaDomain.UA, env).region(region));
            }
            data.add(desktopHwLg(env).region(region));
            data.add(desktopHwBmw(env).region(region));
        });

        data.add(desktopComTr(env).region(ISTANBUL_11508));
        data.add(desktopFirefox(MordaDomain.COM_TR, env).region(ISTANBUL_11508));
        data.add(touchComTr(env).region(ISTANBUL_11508));
        data.add(pdaComTr(env).region(ISTANBUL_11508));
        data.add(desktopComTrFoot(GS, env).region(ISTANBUL_11508));
        data.add(desktopComTrFoot(BJK, env).region(ISTANBUL_11508));

        return data;
    }

    @Override
    @Before
    public void init() throws JsonProcessingException {
        this.cleanvars = new MordaClient().cleanvars(morda, STOCKS, TOPNEWS).read();
    }

    @Override
    public MordaCleanvars getBlock() {
        return cleanvars;
    }

    @Override
    public int getShow() {
        if (morda.getMordaType().equals(MordaType.DESKTOP_MAIN)) {
            if (cleanvars.getTopnews().getShow() == 1 && cleanvars.getTopnews().getTopnewsStocks().size() > 0) {
                return 1;
            }
            return 0;
        }
        return cleanvars.getStocks().getShow();
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return null;
    }


    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_stocks_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_stocks_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_stocks_ping_%s_tttt");
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Set<String> links = new HashSet<>();

        if (morda.getMordaType() == MordaType.DESKTOP_MAIN) {
            cleanvars.getTopnews().getTopnewsStocks().forEach(e -> {
                links.add(e.getHref());
            });
            return links;
        }

        Stocks stocks = cleanvars.getStocks();
        for (StocksBlock block : stocks.getBlocks()) {
            for (StocksRow row : block.getRows()) {
                links.add(row.getHref());
            }
        }
        for (Lite lite : stocks.getLite()) {
            links.add(lite.getHref());
        }

        return links;
    }
}
