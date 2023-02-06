package ru.yandex.autotests.morda.tests.htmlcontent;

import org.junit.Rule;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.com.ComMorda;
import ru.yandex.autotests.morda.pages.comtr.ComTrMorda;
import ru.yandex.autotests.morda.pages.hw.HwMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.autotests.morda.pages.tv.TvSmartMorda;
import ru.yandex.autotests.morda.pages.yaru.YaruMorda;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static ru.yandex.autotests.morda.pages.hw.DesktopHwLgV2Morda.desktopHwLgV2;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20/07/16
 */
@Aqua.Test(title = "Morda page content")
@Features({"Consistency", "Morda html page content"})
@RunWith(Parameterized.class)
public class MordaPageContentTest extends AbstractHtmlContentTest {

    @Rule
    public AllureFeatureRule feature;

    public MordaPageContentTest(String counters, Morda<?> morda) {
        super(() -> new MordaClient().morda(morda).readAsResponse().getBody().asString());
        this.feature = new AllureFeatureRule(morda.getMordaType().name());
    }

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();

        data.addAll(getMordas().stream().map(e -> {
            e.blockCounters();
            return new Object[]{"no_counters", e};
        }).collect(Collectors.toList()));

        data.addAll(getMordas().stream().map(e -> {
            e.forceCounters();
            return new Object[]{"force_counters", e};
        }).collect(Collectors.toList()));

        return data;
    }

    private static List<Morda<?>> getMordas() {
        List<Morda<?>> mordas = new ArrayList<>();

        mordas.addAll(ComMorda.getDefaultComList(CONFIG.getEnvironment()));
        mordas.addAll(ComTrMorda.getDefaultComTrList(CONFIG.getEnvironment()));
        mordas.addAll(YaruMorda.getDefaultYaruList(CONFIG.getEnvironment()));
        mordas.addAll(HwMorda.getDefaultHwList(CONFIG.getEnvironment()));
        mordas.addAll(MainMorda.getDefaultMainList(CONFIG.getEnvironment()));
        mordas.addAll(TvSmartMorda.getDefaultList(CONFIG.getEnvironment()));

        mordas.add(desktopHwLgV2(CONFIG.getEnvironment()).path("cityselect.html").queryParam("page", "index.html"));
        mordas.add(desktopMain(CONFIG.getEnvironment()).path("themes"));
        mordas.add(desktopMain(CONFIG.getEnvironment()).path("themes/yoda"));
        mordas.add(desktopMain(CONFIG.getEnvironment()).queryParam("edit", "1"));
        mordas.add(desktopMain(CONFIG.getEnvironment()).queryParam("content", "yaua"));
        mordas.add(desktopMain(CONFIG.getEnvironment()).queryParam("content", "chromenewtab"));

        return mordas;
    }
}
