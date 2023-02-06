package ru.yandex.metrika.mobmet.dao.cluster;

import org.junit.Test;

import static java.util.concurrent.TimeUnit.SECONDS;
import static org.awaitility.Awaitility.await;

public class AvailabilityRuleTest {

    private static final int checkPeriod = 1;

    @Test
    public void testWorkingCluster() {
        final AvailabilityRule rule = new AvailabilityRule(PingDummy.OK, checkPeriod);
        rule.init();
        await().atMost(checkPeriod * 3, SECONDS).until(() -> rule.isOkay(null));
    }

    @Test
    public void testFailedCluster() {
        final AvailabilityRule rule = new AvailabilityRule(PingDummy.NOT_OK, checkPeriod);
        rule.init();
        await().atMost(checkPeriod * 3, SECONDS).until(() -> !rule.isOkay(null));
    }

    private enum PingDummy implements ClusterPing {
        OK(true),
        NOT_OK(false);

        private final boolean pingResponse;

        PingDummy(boolean pingResponse) {
            this.pingResponse = pingResponse;
        }

        @Override
        public boolean ping() {
            return pingResponse;
        }
    }
}
