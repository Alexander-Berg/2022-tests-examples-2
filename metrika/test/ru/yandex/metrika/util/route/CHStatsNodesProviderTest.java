package ru.yandex.metrika.util.route;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.apache.curator.shaded.com.google.common.collect.Sets;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.util.route.nodes.CHStatsNodesProvider;

import static org.assertj.core.api.Assertions.assertThat;

public class CHStatsNodesProviderTest {

    private CHStatsNodesProvider<Integer> nodesProvider;
    private List<Integer> nodes;

    @Before
    public void setup() {
        this.nodes = IntStream.range(0, 10).boxed().collect(Collectors.toList());
        this.nodesProvider = new CHStatsNodesProvider<>(nodes, TimeUnit.SECONDS.toMillis(1), 4, 0.1);
    }

    @Test
    public void allNodes() {
        assertThat(nodesProvider.all()).isEqualTo(nodes);
    }

    @Test
    public void chooseSize() {
        assertThat(nodesProvider.choose(3).size()).isEqualTo(3);
    }

    @Test
    public void chooseDistinct() {
        for (int i = 0; i < 10; i++) {
            List<Integer> choose = nodesProvider.choose(3);
            assertThat(Sets.newHashSet(choose).size()).isEqualTo(3);
        }
    }

    @Test
    public void chooseWithNeededOrder() {
        List<HttpTemplate> templates = Arrays.asList(withDatacenter("1"), withDatacenter("2"), withDatacenter("2"), withDatacenter("1"), withDatacenter(null));
        CHStatsNodesProvider<HttpTemplate> provider = new CHStatsNodesProvider<>(templates, TimeUnit.SECONDS.toMillis(1), 4, 0.1);
        List<HttpTemplate> choose = provider.choose(3);
        checkDatacenterChanges(choose);
        choose = provider.choose(5);
        assertThat(choose.get(4).getDb().getDatacenter()).isNull();
    }

    private void checkDatacenterChanges(List<HttpTemplate> choose) {
        for (int i = 1; i < choose.size(); i++) {
            assertThat(choose.get(i).getDb().getDatacenter().equals(choose.get(i-1).getDb().getDatacenter())).isFalse();
        }
    }

    private HttpTemplate withDatacenter(String datacenter) {
        HttpTemplate template = Mockito.mock(HttpTemplate.class);
        ClickHouseSource clickHouseDataSource = Mockito.mock(ClickHouseSource.class);
        Mockito.when(clickHouseDataSource.getDatacenter()).thenReturn(datacenter);
        Mockito.when(template.getDb()).thenReturn(clickHouseDataSource);
        return template;
    }

    @Test
    public void chooseRandomized() {
        boolean seenDifferent = false;
        List<Integer> first = nodesProvider.choose(3);
        for (int i = 0; i < 10; i++) {
            List<Integer> choose = nodesProvider.choose(3);
            if (!choose.equals(first)) {
                seenDifferent = true;
            }
        }
        assertThat(seenDifferent).isTrue();
    }

    @Test
    public void healthyFirst() {
        for (int i = 0; i < 5; i++) {
            nodesProvider.doTrackEvent(i, true);
        }

        final List<Integer> choose = nodesProvider.choose(8);
        for (int i = 0; i < 5; i++) {
            if (choose.get(i) < 5) {
                System.out.println("here");
            }
            assertThat(choose.get(i)).isGreaterThanOrEqualTo(5);
        }

        for (int i = 5; i < 8; i++) {
            assertThat(choose.get(i)).isLessThan(5);
        }
    }

    @Test
    public void returnsToHealthy() {
        nodesProvider.doTrackEvent(0, true);
        assertThat(nodesProvider.choose(9)).doesNotContain(0);
        for (int i = 0; i < 10; i++) {
            nodesProvider.doTrackEvent(0, false);
        }

        boolean seenReturned = false;
        for (int i = 0; i < 10; i++) {
            if (nodesProvider.choose(9).contains(0)) {
                seenReturned = true;
            }
        }
        assertThat(seenReturned).isTrue();
    }

    @Test
    public void returnsToHealthyByTimeout() throws InterruptedException {
        nodesProvider.doTrackEvent(0, true);
        assertThat(nodesProvider.choose(9)).doesNotContain(0);

        Thread.sleep(TimeUnit.MILLISECONDS.toMillis(1500));

        boolean seenReturned = false;
        for (int i = 0; i < 10; i++) {
            if (nodesProvider.choose(9).contains(0)) {
                seenReturned = true;
            }
        }
        assertThat(seenReturned).isTrue();
    }
}
