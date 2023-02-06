package ru.yandex.metrika.ui.webvisor.player2.visitinfo;


import java.util.List;

import org.assertj.core.api.Assertions;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.ui.webvisor.common.visit.VisitHitMeta;
import ru.yandex.metrika.util.serialization.Event2PacketYtSerializer;
import ru.yandex.metrika.wv2.parser.EventParser;
import ru.yandex.metrika.wv2.parser.Package;
import ru.yandex.metrika.wv2.parser.parser2.EventParser2;

import static java.util.Arrays.asList;
import static ru.yandex.metrika.ui.webvisor.player2.visitinfo.TabChangesSampleData.Case1;
import static ru.yandex.metrika.ui.webvisor.player2.visitinfo.TabChangesSampleData.Case2;
import static ru.yandex.metrika.ui.webvisor.player2.visitinfo.TabChangesSampleData.Case3;
import static ru.yandex.metrika.ui.webvisor.player2.visitinfo.TabChangesSampleData.DuplicatedFocusEvents;
import static ru.yandex.metrika.ui.webvisor.player2.visitinfo.TabChangesSampleData.FirstHitStamp;
import static ru.yandex.metrika.ui.webvisor.player2.visitinfo.TabChangesSampleData.NoFocusForSecondHit;
import static ru.yandex.metrika.ui.webvisor.player2.visitinfo.TabChangesSampleData.Tab121;

@RunWith(Parameterized.class)
public class TabChangesBuilderTest {

    @Parameterized.Parameter
    public String desc;

    @Parameterized.Parameter(1)
    public List<Package> packages;

    @Parameterized.Parameter(2)
    public List<VisitHitMeta> visitHits;

    @Parameterized.Parameter(3)
    public List<TabChange> expectedChanges;

    private EventParser eventParser;

    @Parameterized.Parameters(name = "case: {0}")
    public static List<Object> createParameters() {
        return asList(
                params("2 events in 1 hit on 1 page", Case1.PACKAGES, Case1.VISIT_HITS, Case1.TAB_CHANGES),
                params("2 hits 2 pages", Case2.PACKAGES, Case2.VISIT_HITS, Case2.TAB_CHANGES),
                params("2 hits with focus events on one tab", Case3.PACKAGES, Case3.VISIT_HITS, Case3.TAB_CHANGES),
                params("duplicated focus events in 1 hit", DuplicatedFocusEvents.PACKAGES, DuplicatedFocusEvents.VISIT_HITS, DuplicatedFocusEvents.TAB_CHANGES),
                params("2 hits without focus event for second HIT on one tab", NoFocusForSecondHit.PACKAGES, NoFocusForSecondHit.VISIT_HITS, NoFocusForSecondHit.TAB_CHANGES),
                params("tab1->tab2->tab1", Tab121.PACKAGES, Tab121.VISIT_HITS, Tab121.TAB_CHANGES),
                params("1st select in hit always has stamp=0", FirstHitStamp.PACKAGES, FirstHitStamp.VISIT_HITS, FirstHitStamp.TAB_CHANGES)
        );
    }

    private static Object[] params(Object... params) {
        return params;
    }

    @Before
    public void setUp() {
        eventParser = createEventParser2();
    }

    @Test
    public void tabChangesForPackagesAndVisitHits() {
        List<PageMetaWithHid> pages = new PageExtractor(packages, eventParser).pages();
        TabChangesBuilder tabChangesBuilder = new TabChangesBuilder(
                packages,
                eventParser,
                new HitOffsetResolver(visitHits, pages),
                new TabChangesBuilder.HitWatchIdResolver(visitHits));
        List<TabChange> tabChanges = tabChangesBuilder.getTabChanges();
        Assertions.assertThat(tabChanges)
                .containsExactlyElementsOf(expectedChanges);
    }

    private EventParser2 createEventParser2() {
        EventParser2 ep2 = new EventParser2();
        Event2PacketYtSerializer serializer = new Event2PacketYtSerializer();
        serializer.afterPropertiesSet();
        ep2.setSerializer(serializer);
        return ep2;
    }

}
