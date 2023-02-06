package ru.yandex.metrika.radar.address;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.google.common.collect.Lists;
import org.junit.Test;
import org.mockito.Mockito;

import ru.yandex.metrika.radar.segments.DimensionId;
import ru.yandex.metrika.util.PrimitiveBytes;

import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertTrue;

/**
 * @author jkee
 */

public class FullAddressTest {

    @Test
    public void testRhombus() throws Exception {
        List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"));
        List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(2, "a1"),
                new StringEdge(2, "a2"),
                new StringEdge(2, "a3"));
        FullAddress address = FullAddress.builder()
                .append(DimensionId.TRAFFIC_SOURCE, new Address(edges1))
                .append(DimensionId.START_PAGE, new Address(edges2))
                .get();
        List<Set<FullAddress>> rhombus = address.generateKeysRhombus();
        assertEquals(6, rhombus.size());
        for (int i = 0; i < rhombus.size(); i++) {
            Set<FullAddress> line = rhombus.get(i);
            System.out.println(line);
            switch(i) {
                case 0:
                    assertTrue(line.size() == 1);
                    break;
                case 1:
                    assertTrue(line.size() == 2);
                    break;
                case 2:
                    assertTrue(line.size() == 3);
                    break;
                case 3:
                    assertTrue(line.size() == 3);
                    break;
                case 4:
                    assertTrue(line.size() == 2);
                    break;
                case 5:
                    assertTrue(line.size() == 1);
                    break;
            }
        }
    }

    @Test
    public void testRhombusFlatten() throws Exception {
        List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"));
        List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(2, "a1"),
                new StringEdge(2, "a2"),
                new StringEdge(2, "a3"));
        FullAddress address = FullAddress.builder()
                .append(DimensionId.TRAFFIC_SOURCE, new Address(edges1))
                .append(DimensionId.START_PAGE, new Address(edges2))
                .get();
        Set<FullAddress> flatten = address.generateKeysRhombusFlatten();
        assertEquals(1 + 2 + 3 + 3 + 2 + 1, flatten.size());
        List<Set<FullAddress>> rhombus = address.generateKeysRhombus();
        Set<FullAddress> flattenFromRhombus = new HashSet<>();
        for (Set<FullAddress> rhombu : rhombus) {
            flattenFromRhombus.addAll(rhombu);
        }
        assertEquals(flatten, flattenFromRhombus);
    }

    @Test
    public void testRhombusFlattenFiltered() throws Exception {
        List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"));
        List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(2, "a1"),
                new StringEdge(2, "a2"),
                new StringEdge(2, "a3"));
        FullAddress address = FullAddress.builder()
                .append(DimensionId.TRAFFIC_SOURCE, new Address(edges1))
                .append(DimensionId.START_PAGE, new Address(edges2))
                .get();
        //noinspection unchecked
        Set<FullAddress> noFilter = Mockito.mock(Set.class);
        Mockito.when(noFilter.contains(Mockito.<FullAddress>anyObject())).thenReturn(true);
        Set<FullAddress> flatten = address.generateKeysRhombusFlattenFiltered(noFilter);
        assertEquals(1 + 2 + 3 + 3 + 2 + 1, flatten.size());
        List<Set<FullAddress>> rhombus = address.generateKeysRhombus();
        Set<FullAddress> flattenFromRhombus = new HashSet<>();
        for (Set<FullAddress> rhombu : rhombus) {
            flattenFromRhombus.addAll(rhombu);
        }
        assertEquals(flatten, flattenFromRhombus);
    }

    @Test
    public void testRhombusFlattenFilteredWFilter() throws Exception {
        List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"));
        List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(2, "a1"),
                new StringEdge(2, "a2"),
                new StringEdge(2, "a3"));
        FullAddress address = FullAddress.builder()
                .append(DimensionId.TRAFFIC_SOURCE, new Address(edges1))
                .append(DimensionId.START_PAGE, new Address(edges2))
                .get();
        Set<FullAddress> filterRhombus = address.generateKeysRhombusFlatten();
        filterRhombus.remove(address);
        Set<FullAddress> flatten = address.generateKeysRhombusFlattenFiltered(filterRhombus);
        assertEquals(1 + 2 + 3 + 3 + 2, flatten.size());
        List<Set<FullAddress>> rhombus = address.generateKeysRhombus();
        Set<FullAddress> flattenFromRhombus = new HashSet<>();
        for (Set<FullAddress> rhombu : rhombus) {
            flattenFromRhombus.addAll(rhombu);
        }
        flattenFromRhombus.remove(address);
        assertEquals(flatten, flattenFromRhombus);
    }

    @Test
    public void testHash() throws Exception {
        List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"));
        List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(2, "a1"),
                new StringEdge(2, "a2"),
                new StringEdge(2, "a3"));
        FullAddress address = FullAddress.builder()
                .append(DimensionId.TRAFFIC_SOURCE, new Address(edges1))
                .append(DimensionId.START_PAGE, new Address(edges2))
                .get();
        FullAddress address2 = FullAddress.builder()
                .append(DimensionId.TRAFFIC_SOURCE, new Address(edges1))
                .append(DimensionId.START_PAGE, new Address(edges2))
                .append(DimensionId.REGION, Address.EMPTY)
                .get();

        assertTrue(Arrays.equals(address.hash128(), address2.hash128()));

        String json = "{\"TRAFFIC_SOURCE\":[{\"t\":10,\"i\":2}]}";
        FullAddress fullAddress = FullAddress.jsonDeserialize(json);

        byte[] bytes = fullAddress.hash128();
        long hash1 = PrimitiveBytes.getLong(bytes);
        long hash2 = PrimitiveBytes.getLong(bytes, 8);

        System.out.println(hash1);
        System.out.println(hash2);
        System.out.println(fullAddress.getDimensions());

    }

    @Test
    public void testSort() throws Exception {
        FullAddress.Builder builder = FullAddress.builder();
        List<Integer> range = IntStream.range(0, 100).boxed().collect(Collectors.toList());
        Collections.shuffle(range, new Random(3));
        for (Integer integer : range) {
            appendToBuilder(builder, integer);
        }
        FullAddress address = builder.get();
        for (int i = 1; i < address.getDimensionIds().length; i++) {
            assertTrue(address.getDimensionIds()[i - 1] < address.getDimensionIds()[i]);
            assertTrue(address.getAddresses()[i - 1].getLast().getType() <  address.getAddresses()[i].getLast().getType());
        }
    }

    @Test
    public void testChild() throws Exception {
        FullAddress root = FullAddress.EMPTY;
        FullAddress child = FullAddress.builder().append(1, new Address(new IntEdge(1, 1))).get();
        FullAddress deeper = FullAddress.builder(child).append(2, new Address(new StringEdge(2, "ololo"))).get();
        assertTrue(root.isParentOf(child));
        assertTrue(root.isParentOf(deeper));
        assertTrue(child.isParentOf(deeper));


    }

    @Test
    public void testCompare() throws Exception {
        {
            List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"));
            List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"), new StringEdge(1, "o3"));
            testCompare0(edges1, edges2);
        }
        {
            List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new IntEdge(1, 3));
            List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"));
            testCompare0(edges1, edges2);
        }
        {
            List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"));
            List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(2, "o1"));
            testCompare0(edges1, edges2);
        }
        {
            List<Edge> edges1 = Arrays.<Edge>asList();
            List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(2, "o1"));
            testCompare0(edges1, edges2);
        }

        {
            List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(2, "o1"));
            List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(2, "o2"));
            testCompare0(edges1, edges2, DimensionId.values()[1], DimensionId.values()[0]);
        }
    }

    private static void testCompare0(List<Edge> edges1, List<Edge> edges2) {
        testCompare0(edges1, edges2, DimensionId.TRAFFIC_SOURCE, DimensionId.TRAFFIC_SOURCE);
    }

    private static void testCompare0(List<Edge> edges1, List<Edge> edges2, DimensionId d1, DimensionId d2) {
        FullAddress address = FullAddress.builder()
                .append(d1, new Address(edges1))
                .get();
        FullAddress address2 = FullAddress.builder()
                .append(d2, new Address(edges2))
                .get();
        List<FullAddress> addresses = Lists.newArrayList(address2, address);
        Collections.sort(addresses);
        assertEquals(address, addresses.get(0));
        List<FullAddress> addresses2 = Lists.newArrayList(address, address2);
        Collections.sort(addresses2);
        assertEquals(address, addresses2.get(0));
    }

    @Test
    public void testSerDes() throws Exception {
        FullAddress address = FullAddress.builder()
                .append(1, new Address(new IntEdge(1, 1), new StringEdge(2, "szzx")))
                .append(2, new Address(new IntEdge(2, 3), new StringEdge(2, "szzx")))
                .get();
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        DataOutputStream dataOutputStream = new DataOutputStream(stream);
        address.serialize(dataOutputStream);
        dataOutputStream.close();
        byte[] bytes = stream.toByteArray();
        DataInputStream dataInputStream = new DataInputStream(new ByteArrayInputStream(bytes));
        FullAddress deser = FullAddress.deserialize(dataInputStream);
        assertEquals(address, deser);

    }

    @Test
    public void testSuffix() throws Exception {
        FullAddress address = FullAddress.builder()
                .append(1, new Address(new IntEdge(1, 1), new StringEdge(2, "szzx")))
                .append(2, new Address(new IntEdge(2, 3), new StringEdge(2, "szzx")))
                .get();
        FullAddress parent = FullAddress.builder()
                .append(1, new Address(new IntEdge(1, 1)))
                .get();
        FullAddress realSuffix = FullAddress.builder()
                .append(1, new Address(new StringEdge(2, "szzx")))
                .append(2, new Address(new IntEdge(2, 3), new StringEdge(2, "szzx")))
                .get();
        assertEquals(realSuffix, address.buildSuffix(parent));
    }

    private static void appendToBuilder(FullAddress.Builder builder, int key) {
        builder.append(key, new Address(Arrays.<Edge>asList(new IntEdge(key, 1))));
    }
}
