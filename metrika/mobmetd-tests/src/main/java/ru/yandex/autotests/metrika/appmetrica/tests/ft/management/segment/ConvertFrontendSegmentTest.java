package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.segment;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(Requirements.Feature.Management.SEGMENT)
@Stories(Requirements.Story.Segments.CONVERT)
@Title("Преобразование сегментов")
@RunWith(Parameterized.class)
public class ConvertFrontendSegmentTest {

    private final static UserSteps user = UserSteps.onTesting(Users.SIMPLE_USER);

    @Parameterized.Parameter
    public String namespace;

    @Parameterized.Parameter(1)
    public String table;

    @Parameterized.Parameter(2)
    public String frontend;

    @Parameterized.Parameter(3)
    public String expected;

    @Parameterized.Parameters(name = "Namespace {0}. Таблица {1}. Сегмент {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param("ym:u:", "users", TestData.defaultSegmentParams(), "exists ym:d:device with (appID=='ru.yandex.metro')"),
                param("ym:ge:", "generic_events", TestData.defaultSegmentParams(), "exists ym:d:device with (appID=='ru.yandex.metro')")
        );
    }

    @Test
    public void checkSimpleSegmentByNs() {
        String actual = user.onSegmentSteps().convertFrontendSegmentByNsForReport(namespace, frontend);
        assertThat("сегмент правильно сконвертирован", actual, equalTo(expected));
    }

    @Test
    public void checkSimpleSegmentByTable() {
        String actual = user.onSegmentSteps().convertFrontendSegmentByTable(table, frontend);
        assertThat("сегмент правильно сконвертирован", actual, equalTo(expected));
    }

    @Test
    public void checkFilterValuesByNs() {
        String actual = user.onSegmentSteps().convertFrontendSegmentByNsForFilterValues(namespace, namespace, frontend);
        assertThat("сегмент правильно сконвертирован", actual, equalTo(expected));
    }

    private static Object[] param(String namespace, String table, String frontend, String expected) {
        return new Object[]{namespace, table, frontend, expected};
    }
}
