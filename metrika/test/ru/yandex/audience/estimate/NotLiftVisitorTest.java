package ru.yandex.audience.estimate;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Stream;

import com.google.common.collect.Lists;
import com.google.common.collect.Streams;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.Test;

import ru.yandex.audience.estimate.filter.AndNode;
import ru.yandex.audience.estimate.filter.AudienceNode;
import ru.yandex.audience.estimate.filter.CdpSegmentNode;
import ru.yandex.audience.estimate.filter.CounterNode;
import ru.yandex.audience.estimate.filter.EcommerceNode;
import ru.yandex.audience.estimate.filter.FilterNode;
import ru.yandex.audience.estimate.filter.FilterNodeVisitor;
import ru.yandex.audience.estimate.filter.GoalNode;
import ru.yandex.audience.estimate.filter.NotNode;
import ru.yandex.audience.estimate.filter.OrNode;
import ru.yandex.audience.estimate.filter.SegmentNode;
import ru.yandex.metrika.util.collections.F;

import static org.junit.Assert.assertEquals;
import static ru.yandex.audience.estimate.filter.FilterNode.and;
import static ru.yandex.audience.estimate.filter.FilterNode.minus;
import static ru.yandex.audience.estimate.filter.FilterNode.not;
import static ru.yandex.audience.estimate.filter.FilterNode.or;

public class NotLiftVisitorTest {
    private static final LocalDate today = LocalDate.now();
    private static final CounterNode x = new CounterNode(Set.of(1), today, today);
    private static final CounterNode y = new CounterNode(Set.of(2), today, today);
    private static final CounterNode z = new CounterNode(Set.of(3), today, today);

    @Test
    public void testNoRewrite1() {
        testNoRewrite(
                minus(x, y)
        );
    }

    @Test
    public void testNoRewrite2() {
        testNoRewrite(
                minus(x, minus(y, z))
        );
    }

    @Test
    public void testNoRewrite3() {
        testNoRewrite(
                and(x, or(y, z))
        );
    }

    @Test
    public void testNoRewrite4() {
        testNoRewrite(
                or(x, and(y, z))
        );
    }

    @Test
    public void testNoRewrite5() {
        testNoRewrite(
                minus(x, and(y, z))
        );
    }

    @Test
    public void testNoRewrite6() {
        testNoRewrite(
                or(x, minus(y, z))
        );
    }

    @Test
    public void testRewrite1() {
        // x or not y === not(y and not x) === not(y \ x)
        testRewrite(
                or(x, not(y)),
                not(minus(y, x))
        );
    }

    @Test
    public void testRewrite2() {
        // not x and not y === not(x or y) === not(x ∪ y)
        testRewrite(
                and(not(x), not(y)),
                not(or(x, y))
        );
    }

    @Test
    public void testRewrite3() {
        // x or (y or not z) === not((z and not y) and not x) === not((z \ y) \ x)
        testRewrite(
                or(x, or(y, not(z))),
                not(minus(minus(z, y), x))
        );
    }

    @Test
    public void testRewrite4() {
        // x and (y or not z) === x and not (z and not y) === x \ (z \ y)
        testRewrite(
                and(x, or(y, not(z))),
                minus(x, minus(z, y))
        );
    }

    @Test
    public void testRewrite5() {
        // x and (not y or not z) === x and not (y and z) === x \ (y ∩ z)
        testRewrite(
                and(x, or(not(y), not(z))),
                minus(x, and(y, z))
        );
    }

    @Test
    public void testRewrite6() {
        // x or (not y and not z) === not((y or z) and not x) === not((y ∪ z) \ x)
        testRewrite(
                or(x, and(not(y), not(z))),
                not(minus(or(y, z), x))
        );
    }

    private void testNoRewrite(FilterNode src) {
        var rewritten = src.visit(NotLiftVisitor.INSTANCE);
        assertEquals(src, rewritten);
    }

    private void testRewrite(FilterNode src, FilterNode expected) {
        var rewritten = src.visit(NotLiftVisitor.INSTANCE);
        assertEquals(expected, rewritten);
        assertEquivalent(src, rewritten);
    }

    private static void assertEquivalent(FilterNode src, FilterNode result) {
        class SubstEvalVisitor implements FilterNodeVisitor<Boolean> {
            private final Map<CounterNode, Boolean> srcValues;

            SubstEvalVisitor(Map<CounterNode, Boolean> srcValues) {
                this.srcValues = srcValues;
            }

            @Override
            public Boolean visit(AndNode node) {
                return node.left.visit(this) && node.right.visit(this);
            }

            @Override
            public Boolean visit(OrNode node) {
                return node.left.visit(this) || node.right.visit(this);
            }

            @Override
            public Boolean visit(NotNode node) {
                return !node.child.visit(this);
            }

            @Override
            public Boolean visit(SegmentNode node) {
                throw new IllegalArgumentException(node.toString());
            }

            @Override
            public Boolean visit(CounterNode node) {
                return srcValues.get(node);
            }

            @Override
            public Boolean visit(EcommerceNode node) {
                throw new IllegalArgumentException(node.toString());
            }

            @Override
            public Boolean visit(GoalNode node) {
                throw new IllegalArgumentException(node.toString());
            }

            @Override
            public Boolean visit(AudienceNode node) {
                throw new IllegalArgumentException(node.toString());
            }

            @Override
            public Boolean visit(CdpSegmentNode node) {
                throw new IllegalArgumentException(node.toString());
            }
        }


        Lists.cartesianProduct(
                List.of(false, true),
                List.of(false, true),
                List.of(false, true)
        ).forEach(values -> {
            //noinspection UnstableApiUsage
            var valuesMap = Streams.zip(Stream.of(x, y, z), values.stream(), Pair::of).collect(F.pairToMapCollector());
            var assertVisitor = new SubstEvalVisitor(valuesMap);
            var srcVal = src.visit(assertVisitor);
            var resVal = result.visit(assertVisitor);
            assertEquals(
                    "Failed equivalence check. Values map: " + values + ". " +
                            "Src: " + src + ". Src val: " + src  + ". " +
                            "Result: " + result + ". Res val: " + resVal + ".",
                    srcVal, resVal
            );
        });
    }
}
