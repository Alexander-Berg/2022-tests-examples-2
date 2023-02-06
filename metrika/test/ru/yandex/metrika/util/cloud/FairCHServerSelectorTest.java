package ru.yandex.metrika.util.cloud;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import com.google.common.collect.Lists;
import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.util.CHNode;
import ru.yandex.metrika.util.CalcCloudSettings;

import static org.junit.Assert.assertTrue;

/**
 * @author serebrserg
 * @since 22.01.15
 */
public class FairCHServerSelectorTest {

    private static final String DC_NAME = "SAS";

    @Test
    public void testOneDC(){
        FairCHServerSelector fairCHServerSelector = new FairCHServerSelector();
        CalcCloudSettings calcCloudSettings = new CalcCloudSettings();
        calcCloudSettings.setReplication_factor(1);
        fairCHServerSelector.setCalcCloudSettings(calcCloudSettings);
        fairCHServerSelector.setDatacenters(Lists.newArrayList(new CHDatacenter(DC_NAME, Lists.newArrayList(createCHCloudNode("1", 1, 2)))));
        List<CHNode> chNodes = fairCHServerSelector.selectCHCloudNodesGroup();
        Assert.assertEquals(chNodes.size(), 1);
    }

    @Test
    public void testOK() {
        FairCHServerSelector fairCHServerSelector = new FairCHServerSelector();
        fairCHServerSelector.setCalcCloudSettings(new CalcCloudSettings());
        fairCHServerSelector.setDatacenters(Lists.newArrayList(
                new CHDatacenter(DC_NAME, Lists.newArrayList(createCHCloudNode("1", 1, 2), createCHCloudNode("1", 2, 2))),
                new CHDatacenter(DC_NAME, Lists.newArrayList(createCHCloudNode("2", 1, 2))),
                new CHDatacenter(DC_NAME, Lists.newArrayList(createCHCloudNode("3", 1, 2))),
                new CHDatacenter(DC_NAME, Lists.newArrayList(createCHCloudNode("4", 1, 2)))
        ));
        List<CHNode> nodes = fairCHServerSelector.selectCHCloudNodesGroup();
        Assert.assertEquals(3, nodes.size());

        Set<String> uniqueNodes = nodes.stream().map(CHNode::getHost).collect(Collectors.toSet()); // здесь считаем вообще по датацентру
        Assert.assertEquals(3, uniqueNodes.size());
        assertTrue(uniqueNodes.contains("1"));

    }

    private static CHNode createCHCloudNode(String host, int port, int httpPort){
        CHNode node = new CHNode();
        node.setHost(host);
        node.setPort(port);
        node.setHttp_port(httpPort);
        return node;
    }


}
