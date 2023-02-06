package ru.yandex.metrika.util.route;

import java.util.function.Function;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import static java.util.Arrays.asList;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.util.route.AllNodesMethod.FailPolicy.CASCADE;
import static ru.yandex.metrika.util.route.AllNodesMethod.FailPolicy.IGNORE;
import static ru.yandex.metrika.util.route.AllNodesMethod.FailPolicy.IGNORE_IF_ANY_OK;
import static ru.yandex.metrika.util.route.AllNodesMethod.FailPolicy.IGNORE_IF_QUORUM_OK;

@RunWith(MockitoJUnitRunner.class)
public class LoadBalanceInvokeForAllNodesTest {

    @Mock private Function<Object, Object> node;
    @Mock private Function<Object, Object> brokenNode;

    public static final String ERROR_MESSAGE = "method should fail";

    @Before
    public void setUp() throws Exception {
        when(brokenNode.apply(any())).thenThrow(new RuntimeException(ERROR_MESSAGE));
    }

    @Test
    public void stopsOnAllClickhouseExceptionWhenStopIsSetAndOneNodeIsBroken() throws Throwable {
        assertThatThrownBy(() ->
                invoke(createLoadBalancerWithStopOnAllClickhouseException(brokenNode, node), IGNORE_IF_ANY_OK)
        ).hasMessage(ERROR_MESSAGE);
    }

    @Test
    public void succeedsWhenIgnoreIfAnyOkFailPolicyAndOneOfTwoNodesIsBroken() throws Throwable {
        invoke(createLoadBalancer(brokenNode, node), IGNORE_IF_ANY_OK);
    }

    @Test
    public void failsWhenIgnoreIfAnyOkFailPolicyAndAllNodesAreBroken() throws Throwable {
        assertThatThrownBy(() ->
                invoke(createLoadBalancer(brokenNode, brokenNode), IGNORE_IF_ANY_OK)
        ).hasMessage(ERROR_MESSAGE);
    }

    @Test
    public void succeedsWhenIgnoreIfAnyOkFailPolicyAndAllNodesAreWorking() throws Throwable {
        invoke(createLoadBalancer(node, node), IGNORE_IF_ANY_OK);
    }

    @Test
    public void failsWhenIgnoreIfQuorumOkFailPolicyAndTwoOfThreeNodesAreBroken() throws Throwable {
        assertThatThrownBy(() ->
                invoke(createLoadBalancer(brokenNode, node, brokenNode), IGNORE_IF_QUORUM_OK)
        ).hasMessage(ERROR_MESSAGE);
    }

    @Test
    public void succeedsWhenIgnoreIfQuorumOkFailPolicyAndOneOfThreeNodeIsBroken() throws Throwable {
        invoke(createLoadBalancer(brokenNode, node, node), IGNORE_IF_QUORUM_OK);
    }

    @Test
    public void succeedsWhenIgnoreIfQuorumOkFailPolicyAndAllNodesAreWorking() throws Throwable {
        invoke(createLoadBalancer(node, node, node), IGNORE_IF_QUORUM_OK);
    }

    @Test
    public void failsWhenIgnoreIfQuorumOkFailPolicyAndAllNodesAreBroken() throws Throwable {
        assertThatThrownBy(() ->
                invoke(createLoadBalancer(brokenNode, brokenNode, brokenNode), IGNORE_IF_QUORUM_OK)
        ).hasMessage(ERROR_MESSAGE);
    }

    @Test
    public void failsWhenCascadeFailPolicyAndOneOfThreeNodeIsBroken() throws Throwable {
        assertThatThrownBy(() ->
                invoke(createLoadBalancer(brokenNode, node, node), CASCADE)
        ).hasMessage(ERROR_MESSAGE);
    }

    @Test
    public void failsWhenCascadeFailPolicyAndAllNodesAreBroken() throws Throwable {
        assertThatThrownBy(() ->
                invoke(createLoadBalancer(brokenNode, brokenNode, brokenNode), CASCADE)
        ).hasMessage(ERROR_MESSAGE);
    }

    @Test
    public void succeedsWhenCascadeFailPolicyAndAllNodeAreWorking() throws Throwable {
        invoke(createLoadBalancer(node, node, node), CASCADE);
    }

    @Test
    public void succeedsWhenIgnoreFailPolicyAndAllNodeAreWorking() throws Throwable {
        invoke(createLoadBalancer(node, node), IGNORE);
    }

    @Test
    public void succeedsWhenIgnoreFailPolicyAndAllNodesAreBroken() throws Throwable {
        invoke(createLoadBalancer(brokenNode, brokenNode), IGNORE);
    }

    @Test
    public void succeedsWhenIgnoreFailPolicyAndOneOfTwoNodeIsBroken() throws Throwable {
        invoke(createLoadBalancer(node, brokenNode), IGNORE);
    }

    private void invoke(LoadBalance<Function> lb, AllNodesMethod.FailPolicy failPolicy) throws Throwable {
        lb.invokeForAllNodes(Function.class.getMethod("apply", Object.class),
                new Object[]{new Object()},
                failPolicy);
    }

    private LoadBalance<Function> createLoadBalancer(Function... nodes) {
        return new LoadBalance<>(Function.class, asList(nodes), LoadBalance.UNIFORM_FIRST_NODE);
    }

    private LoadBalance<Function> createLoadBalancerWithStopOnAllClickhouseException(Function... nodes) {
        LoadBalance<Function> lb = createLoadBalancer(nodes);
        lb.setStopOnAllClickhouseException(true);
        return lb;
    }

}
