package ru.yandex.metrika.counters;

import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.counters.serverstate.CountersServerExternalCidState;
import ru.yandex.metrika.counters.serverstate.CountersServerStateController;
import ru.yandex.metrika.counters.serverstate.CountersServerTimeZoneState;
import ru.yandex.metrika.counters.serverstate.CountersServerVisorEnabledState;

import static java.util.Arrays.asList;
import static org.assertj.core.api.Assertions.assertThat;


public class CountersServerStateControllerTest {

    private static CountersServerStateController countersServerStateController;
    private static CountersServerExternalCidState countersServerExternalCidState;
    private static CountersServerTimeZoneState countersServerTimeZoneState;
    private static CountersServerVisorEnabledState countersServerVisorEnabledState;

    @BeforeClass
    public static void init() {
        countersServerExternalCidState = new CountersServerExternalCidState();
        countersServerTimeZoneState = new CountersServerTimeZoneState();
        countersServerStateController = new CountersServerStateController();
        countersServerVisorEnabledState = new CountersServerVisorEnabledState();
        CountersServerClient client = new CountersServerClient(true, "counters");
        client.setHost("mtattr01t.yandex.ru");
        client.setPort(8097);
        countersServerStateController.setCountersServerClient(client);
        countersServerStateController.setStates(asList(countersServerExternalCidState, countersServerTimeZoneState, countersServerVisorEnabledState));
        countersServerStateController.init();
    }

    @Test
    @Ignore
    public void translateCounterId() {
        assertThat(countersServerExternalCidState.translateCounterId(1, 1)).isEqualTo(50074594);
    }

    @Test
    @Ignore
    public void visorDisabledForCounter() {
        assertThat(countersServerVisorEnabledState.isVisorEnabled(50074594)).isFalse();
    }

    @Test
    @Ignore
    public void visorEnabledForCounter() {
        assertThat(countersServerVisorEnabledState.isVisorEnabled(101024)).isTrue();
    }

    @Test
    @Ignore
    public void visorDisabledForCounter2() {
        assertThat(countersServerVisorEnabledState.isVisorEnabled(22)).isFalse();
    }

    @Test
    @Ignore
    public void visorEnabledCountersList() {
        int size = countersServerVisorEnabledState.getVisorEnabledCounters().size();
        assertThat(size).isGreaterThan(100);
    }

    @Test
    @Ignore
    public void getTimeZone() {
        assertThat(countersServerTimeZoneState.getTimeZoneId(50074594)).isEqualTo(1);
    }

    @Test
    @Ignore
    public void incrementalSync() {
        long start = System.currentTimeMillis();
        countersServerStateController.sync();
        assertThat(System.currentTimeMillis() - start).isLessThan(5000);
    }
}
