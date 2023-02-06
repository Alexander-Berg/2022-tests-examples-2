package ru.yandex.metrika.ui.webvisor.player2.visitinfo;

import java.util.List;

import org.joda.time.DateTime;

import ru.yandex.metrika.ui.webvisor.common.visit.VisitHitMeta;
import ru.yandex.metrika.wv2.parser.Package;
import ru.yandex.metrika.wv2.parser.PackageType;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.metrika.ui.webvisor.player2.visitinfo.TabChangeType.CLOSE;
import static ru.yandex.metrika.ui.webvisor.player2.visitinfo.TabChangeType.SELECT;

public class TabChangesSampleData {

    public static final int HID_1 = 1;
    public static final int HID_2 = 2;

    public static final long WATCHID_1 = 101L;
    public static final long WATCHID_2 = 102L;

    public static final String NO_TAB_ID = "null";
    public static final String TAB_1 = "001";
    public static final String TAB_2 = "002";

    public static final int STAMP_0 = 0;
    public static final int STAMP_1 = 1;
    public static final int STAMP_2 = 2;
    public static final int STAMP_3 = 3;
    public static final int STAMP_4 = 4;

    public static final int HIT_OFFSET_5 = 5;

    public static final DateTime START_TIME = DateTime.now();

    private static int index = 0;

    private static VisitHitMeta visitHits(int hid, long watchid, DateTime startTime) {
        return new VisitHitMeta(hid, watchid, startTime.getMillis(), null);
    }

    private static TabChange tabChange(int stamp, long watchId, String tabId, TabChangeType type) {
        return new TabChange(stamp, watchId, tabId, type);
    }

    private static Package page(String tabId, int hid, int time) {
        return pkg("{\"frameId\": 0, \"tabId\": \"" + tabId + "\"}", PackageType.page, hid, time);
    }

    private static Package focusEvent(int hid, int time) {
        return eventInternal("focus", hid, time);
    }

    private static Package nonFocusEvent(int hid, int time) {
        return eventInternal("blur", hid, time);
    }

    private static Package eventInternal(String type, int hid, int time) {
        return pkg("{\"time\": " + time + ", \"type\": \"" + type + "\", \"meta\": {}}", PackageType.event, hid, time);
    }

    private static Package pkg(String pkgData, PackageType type, int hid, int time) {
        return new Package(type, hid, pkgData.getBytes(), 1, index++, 1, time, true, 0);
    }

    public static class Case1 {

        public static List<Package> PACKAGES = of(
                page(TAB_1, HID_1, STAMP_0),
                focusEvent(HID_1, STAMP_1),
                nonFocusEvent(HID_1, STAMP_2)
        );

        public static List<VisitHitMeta> VISIT_HITS = List.of(
                visitHits(HID_1, WATCHID_1, START_TIME)
        );

        public static List<TabChange> TAB_CHANGES = of(
                tabChange(STAMP_0, WATCHID_1, TAB_1, SELECT),
                tabChange(STAMP_2, WATCHID_1, TAB_1, CLOSE)
        );
    }

    public static class Case2 {
        public static List<Package> PACKAGES = of(
                page(TAB_1, HID_1, STAMP_0),
                page(TAB_2, HID_2, STAMP_0),
                focusEvent(HID_1, STAMP_1),
                nonFocusEvent(HID_1, STAMP_2),
                focusEvent(HID_2, STAMP_3)
        );

        public static List<VisitHitMeta> VISIT_HITS = of(
                visitHits(HID_1, WATCHID_1, START_TIME),
                visitHits(HID_2, WATCHID_2, START_TIME.plus(HIT_OFFSET_5))
        );

        public static List<TabChange> TAB_CHANGES = of(
                tabChange(STAMP_0, WATCHID_1, TAB_1, SELECT),
                tabChange(STAMP_2, WATCHID_1, TAB_1, CLOSE),
                tabChange(STAMP_0 + HIT_OFFSET_5, WATCHID_2, TAB_2, SELECT),
                tabChange(STAMP_3 + HIT_OFFSET_5, WATCHID_2, TAB_2, CLOSE)
        );
    }

    public static class Case3 {
        public static List<Package> PACKAGES = of(
                page(NO_TAB_ID, HID_1, STAMP_0),
                focusEvent(HID_1, STAMP_1),
                nonFocusEvent(HID_1, STAMP_4),
                page(NO_TAB_ID, HID_2, STAMP_0),
                focusEvent(HID_2, STAMP_2),
                nonFocusEvent(HID_2, STAMP_3),
                nonFocusEvent(HID_2, STAMP_4)
        );

        public static List<VisitHitMeta> VISIT_HITS = of(
                visitHits(HID_1, WATCHID_1, START_TIME),
                visitHits(HID_2, WATCHID_2, START_TIME.plus(HIT_OFFSET_5))
        );

        public static List<TabChange> TAB_CHANGES = of(
                tabChange(STAMP_0, WATCHID_1, NO_TAB_ID, SELECT),
                tabChange(STAMP_0 + HIT_OFFSET_5, WATCHID_2, NO_TAB_ID, SELECT),
                tabChange(STAMP_4 + HIT_OFFSET_5, WATCHID_2, NO_TAB_ID, CLOSE)
        );
    }

    public static class DuplicatedFocusEvents {
        public static List<Package> PACKAGES = of(
                page(TAB_1, HID_1, STAMP_0),
                focusEvent(HID_1, STAMP_2),
                focusEvent(HID_1, STAMP_3),
                nonFocusEvent(HID_1, STAMP_4)
        );

        public static List<VisitHitMeta> VISIT_HITS = List.of(
                visitHits(HID_1, WATCHID_1, START_TIME)
        );

        public static List<TabChange> TAB_CHANGES = of(
                tabChange(STAMP_0, WATCHID_1, TAB_1, SELECT),
                tabChange(STAMP_4, WATCHID_1, TAB_1, CLOSE)
        );
    }


    public static class NoFocusForSecondHit {
        public static List<Package> PACKAGES = of(
                page(NO_TAB_ID, HID_1, STAMP_0),
                focusEvent(HID_1, STAMP_1),
                nonFocusEvent(HID_1, STAMP_4),
                page(NO_TAB_ID, HID_2, STAMP_0),
                nonFocusEvent(HID_2, STAMP_2),
                nonFocusEvent(HID_2, STAMP_3)
        );

        public static List<VisitHitMeta> VISIT_HITS = of(
                visitHits(HID_1, WATCHID_1, START_TIME),
                visitHits(HID_2, WATCHID_2, START_TIME.plus(HIT_OFFSET_5))
        );

        public static List<TabChange> TAB_CHANGES = of(
                tabChange(STAMP_0, WATCHID_1, NO_TAB_ID, SELECT),
                tabChange(STAMP_0 + HIT_OFFSET_5, WATCHID_2, NO_TAB_ID, SELECT),
                tabChange(STAMP_3 + HIT_OFFSET_5, WATCHID_2, NO_TAB_ID, CLOSE)
        );
    }

    public static class Tab121 {
        public static List<Package> PACKAGES = of(
                page(TAB_1, HID_1, STAMP_0),
                focusEvent(HID_1, STAMP_1),
                page(TAB_2, HID_2, STAMP_0),
                focusEvent(HID_2, STAMP_1),
                focusEvent(HID_1, STAMP_4 + HIT_OFFSET_5)
        );

        public static List<VisitHitMeta> VISIT_HITS = of(
                visitHits(HID_1, WATCHID_1, START_TIME),
                visitHits(HID_2, WATCHID_2, START_TIME.plus(HIT_OFFSET_5))
        );

        public static List<TabChange> TAB_CHANGES = of(
                tabChange(STAMP_0, WATCHID_1, TAB_1, SELECT),
                tabChange(STAMP_0 + HIT_OFFSET_5, WATCHID_2, TAB_2, SELECT),
                tabChange(STAMP_1 + HIT_OFFSET_5, WATCHID_2, TAB_2, CLOSE),
                tabChange(STAMP_4 + HIT_OFFSET_5, WATCHID_1, TAB_1, SELECT),
                tabChange(STAMP_4 + HIT_OFFSET_5, WATCHID_1, TAB_1, CLOSE)
        );
    }

    public static class FirstHitStamp {
        public static List<Package> PACKAGES = of(
                page(NO_TAB_ID, HID_1, STAMP_1),
                focusEvent(HID_1, STAMP_4),
                page(NO_TAB_ID, HID_2, STAMP_2),
                nonFocusEvent(HID_2, STAMP_4)
        );

        public static List<VisitHitMeta> VISIT_HITS = of(
                visitHits(HID_1, WATCHID_1, START_TIME),
                visitHits(HID_2, WATCHID_2, START_TIME.plus(HIT_OFFSET_5))
        );

        public static List<TabChange> TAB_CHANGES = of(
                tabChange(STAMP_0, WATCHID_1, NO_TAB_ID, SELECT),
                tabChange(STAMP_0 + HIT_OFFSET_5, WATCHID_2, NO_TAB_ID, SELECT),
                tabChange(STAMP_4 + HIT_OFFSET_5, WATCHID_2, NO_TAB_ID, CLOSE)
        );
    }

}
