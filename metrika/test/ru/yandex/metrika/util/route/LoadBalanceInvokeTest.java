package ru.yandex.metrika.util.route;

import java.util.Collections;
import java.util.List;
import java.util.function.Function;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import static java.util.Arrays.asList;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.fail;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@RunWith(MockitoJUnitRunner.class)
public class LoadBalanceInvokeTest {

    @Mock
    private Function<Object, Object> node;
    @Mock
    private Function<Object, Object> brokenNode;

    public static final String ERROR_MESSAGE = "method should fail";

    @Before
    public void setUp() throws Exception {
        when(brokenNode.apply(any())).thenThrow(new RuntimeException(ERROR_MESSAGE));
    }

    @Test
    public void throwsExceptionIfAllBroken() {
        assertThatThrownBy(() ->
                invoke(createLoadBalancer(3, brokenNode))
        ).hasMessage(ERROR_MESSAGE);
    }

    @Test
    public void executesMaxTryCountTimes() {
        final int maxTryCount = 5;

        try {
            invoke(createLoadBalancer(maxTryCount, brokenNode));
        } catch (Throwable ignored) {
            //ignored
        }
        verify(brokenNode, times(maxTryCount)).apply(any());
    }

    @Test
    public void executesMaxTryCountTimesForManyNodes() {
        final int maxTryCount = 5;

        try {
            invoke(createLoadBalancer(maxTryCount, Collections.nCopies(200, brokenNode)));
        } catch (Throwable ignored) {
            //ignored
        }
        verify(brokenNode, times(maxTryCount)).apply(any());
    }

    @Test
    public void findsAliveNode() {
        try {
            invoke(createLoadBalancer(3, brokenNode, node));
        } catch (Throwable t) {
            fail("must have found alive node");
        }
    }

    private void invoke(LoadBalance<Function> lb) throws Throwable {
        lb.invoke(null, Function.class.getMethod("apply", Object.class),
                new Object[]{new Object()});
    }

    private LoadBalance<Function> createLoadBalancer(int maxTryCount, Function... nodes) {
        return createLoadBalancer(maxTryCount, asList(nodes));
    }

    private LoadBalance<Function> createLoadBalancer(int maxTryCount, List<Function> nodes) {
        final LoadBalance<Function> loadBalance = new LoadBalance<>(Function.class, nodes, LoadBalance.UNIFORM_FIRST_NODE);
        loadBalance.setMaxTryCount(maxTryCount);
        return loadBalance;
    }
}
