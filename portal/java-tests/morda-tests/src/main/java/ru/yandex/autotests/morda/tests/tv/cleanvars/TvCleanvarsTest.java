package ru.yandex.autotests.morda.tests.tv.cleanvars;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.beans.cleanvars.tv.Tv;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.tests.BaseCleanvarsTest;
import ru.yandex.autotests.morda.tests.MordaTestTags;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;

/**
 * Created by wwax on 09.09.16.
 */

@Aqua.Test(title = MordaTestTags.TV)
@RunWith(Parameterized.class)
public class TvCleanvarsTest extends BaseCleanvarsTest<Tv> {
    public TvCleanvarsTest(Morda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Morda<?>> data() {
        List<Morda<?>> data = new ArrayList<>();
        data.add(desktopMain(CONFIG.pages().getEnvironment()));
        return data;
    }

    public Tv getBlock() {
        return this.cleanvars.getTv();
    }

    public int getShow() {
        return this.getBlock().getShow();
    }
}
