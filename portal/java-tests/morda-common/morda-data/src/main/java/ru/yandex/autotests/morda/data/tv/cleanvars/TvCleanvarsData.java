package ru.yandex.autotests.morda.data.tv.cleanvars;

import ru.yandex.autotests.morda.data.AbstractCleanvarsData;
import ru.yandex.autotests.morda.data.tv.TvData;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaContent;
import ru.yandex.autotests.morda.pages.MordaWithRegion;
import ru.yandex.geobase.regions.GeobaseRegion;

import java.util.HashSet;
import java.util.Set;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.MordaContent.MOB;
import static ru.yandex.autotests.morda.pages.MordaContent.TEL;
import static ru.yandex.autotests.morda.pages.MordaContent.TOUCH;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/09/16
 */
public abstract class TvCleanvarsData extends AbstractCleanvarsData implements TvData {

    public static final Set<MordaContent> TOUCH_CONTENTS = new HashSet<>(asList(MOB, TEL, TOUCH));

    public TvCleanvarsData(Morda<?> morda) {
        super(morda);
    }

    static TvData getTvData(Morda<?> morda) {
        if (TOUCH_CONTENTS.contains(morda.getMordaType().getContent())) {
            return new TvCleanvarsTouchData(morda);
        }
        return new TvCleanvarsBigData(morda);
    }

    @Override
    public GeobaseRegion getRegion() {
        if (!(getMorda() instanceof MordaWithRegion)) {
            throw new IllegalArgumentException("Need MordaWithRegion");
        }
        MordaWithRegion mordaWithRegion = (MordaWithRegion) getMorda();
        return mordaWithRegion.getRegion();
    }
}
