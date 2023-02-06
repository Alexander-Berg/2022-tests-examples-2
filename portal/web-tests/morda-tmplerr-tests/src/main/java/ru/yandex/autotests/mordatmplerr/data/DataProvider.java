package ru.yandex.autotests.mordatmplerr.data;

import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.autotests.mordatmplerr.mordatypes.Browser;
import ru.yandex.autotests.mordatmplerr.mordatypes.TouchType;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.testlab.wiki.Wiki;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static ru.yandex.autotests.mordatmplerr.data.MockType.BIG;
import static ru.yandex.autotests.mordatmplerr.data.MockType.TOUCH;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda.comTrMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.ANDROID_CHROME;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.IPHONE_SAFARI;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.PDA;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.TIZEN;
import static ru.yandex.autotests.mordatmplerr.mordatypes.TouchType.WP;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.03.14
 */
public class DataProvider {
    private static final Properties CONFIG = new Properties();
    private static final List<TouchType> TOUCH_TYPES = Arrays.asList(IPHONE_SAFARI, ANDROID_CHROME, WP, TIZEN);


    private static List<MockRow> getMocks() {
        return Wiki.CLIENT.populate(MockRow.class);
    }

    public static List<Object[]> getTestData() {
        List<Object[]> data = new ArrayList<>();
        List<MockRow> mockRows = DataProvider.getMocks();
        for (MockRow mockRow : mockRows) {
            data.addAll(getMockRowData(mockRow));
        }
        return data;
    }

    private static List<Object[]> getMockRowData(MockRow row) {
        List<Object[]> result = new ArrayList<>();
        for (MockType type : row.getMockTypes()) {
            if (type.equals(TOUCH)) {
                result.addAll(getTouchTestData(row));
            } else if (type.equals(BIG)) {
                result.addAll(getBigTestData(row));
            } else if (type.equals(MockType.PDA)) {
                result.addAll(getPdaTestData(row));
            }
        }
        return result;
    }

    private static List<Object[]> getTouchTestData(MockRow mockRow) {
        List<Object[]> data = new ArrayList<>();
        for (Domain domain : mockRow.getMockDomains()) {
            if (domain.equals(COM_TR)) {
                for (TouchType touchType : TOUCH_TYPES) {
                    data.add(new Object[]{mockRow.getMock(), comTrMorda().withTouchType(touchType)});
                }
            } else {
                for (TouchType touchType : TOUCH_TYPES) {
                    data.add(new Object[]{mockRow.getMock(), mainMorda(domain).withTouchType(touchType)});
                }
            }
        }
        return data;
    }

    private static List<Object[]> getBigTestData(MockRow mockRow) {
        List<Object[]> data = new ArrayList<>();
        for (Domain domain : mockRow.getMockDomains()) {
            if (domain.equals(COM_TR)) {
                for (Browser browser : Browser.values()) {
                    data.add(new Object[]{mockRow.getMock(), comTrMorda().withBrowser(browser)});
                }
            } else {
                for (Browser browser : Browser.values()) {
                    data.add(new Object[]{mockRow.getMock(), mainMorda(domain).withBrowser(browser)});
                }
            }
        }
        return data;
    }

    private static List<Object[]> getPdaTestData(MockRow mockRow) {
        List<Object[]> data = new ArrayList<>();
        for (Domain domain : mockRow.getMockDomains()) {
            if (domain.equals(COM_TR)) {
                data.add(new Object[]{mockRow.getMock(), comTrMorda().withTouchType(PDA)});
            } else {
                data.add(new Object[]{mockRow.getMock(), mainMorda(domain).withTouchType(PDA)});
            }
        }
        return data;
    }
}
