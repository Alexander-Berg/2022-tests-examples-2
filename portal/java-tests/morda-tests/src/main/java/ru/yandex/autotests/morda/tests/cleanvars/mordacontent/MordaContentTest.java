package ru.yandex.autotests.morda.tests.cleanvars.mordacontent;

import org.apache.commons.lang3.RandomStringUtils;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.pages.com.DesktopComMorda.desktopCom;
import static ru.yandex.autotests.morda.pages.com.PdaComMorda.pdaCom;
import static ru.yandex.autotests.morda.pages.com.TouchComMorda.touchCom;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrAllMorda.desktopComTrAll;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda.FootballClub;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrFootballMorda.desktopComTrFoot;
import static ru.yandex.autotests.morda.pages.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.comtr.PdaComTrAllMorda.pdaComTrAll;
import static ru.yandex.autotests.morda.pages.comtr.TouchComTrAllMorda.touchComTrAll;
import static ru.yandex.autotests.morda.pages.comtr.TouchComTrWpMorda.touchComTrWp;
import static ru.yandex.autotests.morda.pages.hw.DesktopHwBmwMorda.desktopHwBmw;
import static ru.yandex.autotests.morda.pages.hw.DesktopHwLgMorda.desktopHwLg;
import static ru.yandex.autotests.morda.pages.main.DesktopFirefoxMorda.desktopFirefox;
import static ru.yandex.autotests.morda.pages.main.DesktopMainAllMorda.desktopMainAll;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.pages.main.PdaMainAllMorda.pdaMainAll;
import static ru.yandex.autotests.morda.pages.main.PdaMainMorda.pdaMain;
import static ru.yandex.autotests.morda.pages.main.TelMainMorda.telMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainAllMorda.touchMainAll;
import static ru.yandex.autotests.morda.pages.main.TouchMainMorda.touchMain;
import static ru.yandex.autotests.morda.pages.main.TouchMainWpMorda.touchMainWp;
import static ru.yandex.autotests.morda.pages.tv.TvSmartMorda.tvSmart;
import static ru.yandex.autotests.morda.pages.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.morda.pages.yaru.PdaYaruMorda.pdaYaru;
import static ru.yandex.autotests.morda.pages.yaru.TouchYaruMorda.touchYaru;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/07/16
 */
@Aqua.Test(title = "MordaContent value")
@Features({"Cleanvars", "MordaContent"})
@RunWith(Parameterized.class)
public class MordaContentTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    private Morda<?> morda;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();

        data.add(desktopMain(CONFIG.pages().getEnvironment()));
        data.add(desktopMainAll(CONFIG.pages().getEnvironment()));
        data.add(desktopFirefox(MordaDomain.RU, CONFIG.pages().getEnvironment()));
        data.add(desktopFirefox(MordaDomain.UA, CONFIG.pages().getEnvironment()));
        data.add(desktopFirefox(MordaDomain.COM_TR, CONFIG.pages().getEnvironment()));
        data.add(pdaMain(CONFIG.pages().getEnvironment()));
        data.add(pdaMainAll(CONFIG.pages().getEnvironment()));
//        data.add(tabletMain(CONFIG.pages().getEnvironment()));
        data.add(telMain(CONFIG.pages().getEnvironment()));
        data.add(touchMain(CONFIG.pages().getEnvironment()));
        data.add(touchMainAll(CONFIG.pages().getEnvironment()));
        data.add(touchMainWp(CONFIG.pages().getEnvironment()));

        data.add(desktopCom(CONFIG.pages().getEnvironment()));
        data.add(pdaCom(CONFIG.pages().getEnvironment()));
        data.add(touchCom(CONFIG.pages().getEnvironment()));

        data.add(desktopComTr(CONFIG.pages().getEnvironment()));
        data.add(desktopComTrAll(CONFIG.pages().getEnvironment()));
        data.add(desktopComTrFoot(FootballClub.BJK, CONFIG.pages().getEnvironment()));

        data.add(pdaComTrAll(CONFIG.pages().getEnvironment()));
        data.add(touchComTrAll(CONFIG.pages().getEnvironment()));
        data.add(touchComTrWp(CONFIG.pages().getEnvironment()));

        data.add(desktopHwLg(CONFIG.pages().getEnvironment()));
        data.add(desktopHwBmw(CONFIG.pages().getEnvironment()));

        data.add(tvSmart(CONFIG.pages().getEnvironment()));

        data.add(desktopYaru(CONFIG.pages().getEnvironment()));
        data.add(pdaYaru(CONFIG.pages().getEnvironment()));
        data.add(touchYaru(CONFIG.pages().getEnvironment()));

        return data;
    }

    public MordaContentTest(Morda<?> morda) {
        this.morda = morda;
    }

    @Test
    public void checkMordaContent() {
        MordaClient mordaClient = new MordaClient();
        morda.cookie("yandexuid", RandomStringUtils.random(20, false, true));
        String mordaContent = mordaClient.cleanvars(morda).read().getMordaContent();
        assertThat(mordaContent, equalTo(morda.getMordaType().getContent().getValue()));
    }

}
