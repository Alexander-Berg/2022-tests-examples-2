package ru.yandex.autotests.morda.monitorings.cleanvars;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock;
import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.beans.cleanvars.weather.Weather;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.monitoring.golem.GolemEvent;
import ru.yandex.qatools.monitoring.golem.GolemObject;
import ru.yandex.qatools.monitoring.yasm.YasmSignal;

import java.util.*;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.junit.Assume.assumeTrue;
import static ru.yandex.autotests.morda.api.cleanvars.MordaCleanvarsBlock.WEATHER;
import static ru.yandex.autotests.morda.monitorings.MonitoringsData.WEATHER_REGIONS;
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
 * Date: 19.09.16
 */
@Aqua.Test(title = "Weather cleanvars monitoring")
@Features("Weather")
@RunWith(Parameterized.class)
@GolemObject("portal_yandex_weather")
public class WeatherCleanvarsMonitoring extends BaseCleanvarsMonitoring<Weather> {

    public WeatherCleanvarsMonitoring(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        String env = CONFIG.getEnvironment();

        for (GeobaseRegion region : WEATHER_REGIONS) {
            data.add(desktopMain(env).region(region));
            data.add(touchMain(env).region(region));
            data.add(pdaMain(env).region(region));
            data.add(tvSmart(env).region(region));
            data.add(desktopHwLg(env).region(region));
            data.add(desktopHwBmw(env).region(region));
            data.add(desktopFirefox(MordaDomain.RU, env).region(region));
            data.add(desktopFirefox(MordaDomain.UA, env).region(region));
        }

        data.add(desktopFirefox(MordaDomain.COM_TR, env).region(ISTANBUL_11508));
        data.add(desktopComTr(env).region(ISTANBUL_11508));
        data.add(desktopComTrFoot(BJK, env).region(ISTANBUL_11508));
        data.add(desktopComTrFoot(GS, env).region(ISTANBUL_11508));
        data.add(touchComTr(env).region(ISTANBUL_11508));
        data.add(pdaComTr(env).region(ISTANBUL_11508));

        return data;
    }

    @Override
    public MordaCleanvarsBlock getBlockName() {
        return WEATHER;
    }

    @Override
    public Weather getBlock() {
        return cleanvars.getWeather();
    }

    @Override
    public int getShow() {
        assertThat("Текущая погода отсутствует", cleanvars.getWeather().getT1(), not(isEmptyOrNullString()));
        return getBlock().getShow();
    }

    @Test
    @Override
    @GolemEvent("morda_exists")
    @YasmSignal(signal = "morda_weather_exists_%s_tttt")
    public void exists() {
        super.exists();
    }

    @Test
    @GolemEvent("morda_ping")
    @YasmSignal(signal = "morda_weather_ping_%s_tttt", statuses = {SKIPPED, BROKEN})
    public void pings() {
        super.pings("morda_weather_ping_%s_tttt");
    }

    @Test
    @GolemEvent("morda_temp")
    @YasmSignal(signal = "morda_weather_temp_%s_tttt")
    public void temp() {
        Weather weather = getBlock();
        assertThat(weather.getT1(), not(isEmptyOrNullString()));
        assertThat(weather.getT2(), not(isEmptyOrNullString()));
        assertThat(weather.getT3(), not(isEmptyOrNullString()));
    }

    @Override
    public Set<String> getUrlsToPing(MordaCleanvars cleanvars) {
        Weather weather = cleanvars.getWeather();
        assumeTrue("Нет блока погоды на Морде", weather != null && weather.getShow() == 1);

        Set<String> links = new HashSet<>();

        links.add(weather.getNoticeUrl());
        links.add(weather.getUrl());

        return links;
    }
}
