package ru.yandex.metrika.visord.process;

import java.util.Collections;

import org.apache.commons.collections4.CollectionUtils;
import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Test;
import org.mockito.hamcrest.MockitoHamcrest;

import ru.yandex.metrika.counters.serverstate.CountersServerCounterIdExistsState;
import ru.yandex.metrika.filterd.process.EventLogCommon;
import ru.yandex.metrika.visord.chunks.EventMessageType;
import ru.yandex.metrika.visord.process.lb.consumer.EventLogBatchSerializer;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class TskvDeserializerTest {

    private final String tskvGoodDataMultiline = "tskv\ttskv_format=bs-watch-log\tunixtime=1596729841\trequestid=0005AC37A30876EC00030E8B850972DF\teventtime=1596729841\t" +
    "counterid=55275628\tuniqid=3828707081586720063\tcounterclass=0\tantivirusyes=0\t" +
    "browserinfo=ti:1:v:1916:z:180:i:20200806190203:rqnl:1:st:1596729842:u:1593253625414658347:pp:2347192675\t" +
    "url=https://sbermarket.ru/lenta/molochnyie-produkty/moloko/korovie?sid\\=353\tfuniqid=0\ttype=0\thit=851544224\tpart=1\t" +
    "checksum=10001\tdata=<long_binary_data>\tetag=0\tlayerid=1\n" +
    "tskv\ttskv_format=bs-watch-log\tunixtime=1596729842\trequestid=0005AC37A312687300030E8BBC4C5122\teventtime=1596729842\t" +
    "counterid=46483494\tuniqid=2417057451499663336\tcounterclass=0\tantivirusyes=0\t" +
    "browserinfo=ti:8:et:1596729839:w:360x524:v:1916:z:480:i:20200807000339:st:1596729841:u:1553669801453201790:pp:234432416\t" +
    "url=https://www.pharmeconom.ru/catalog/?q\\=%D0%9A%D0%B0%D0%BD%D0%B4%D0%B5%D1%81%D0%B0%D1%80%D0%B8%D0%B0%D0%BD&s\\=\tfuniqid=0\ttype=5\thit=183151828\tpart=7\t" +
    "checksum=0\tdata=<\\\"long_\\tbinary\\0_data>\tetag=0\tlayerid=1";

    private final String tskvGoodDataSinglelineWrongOrder = "tskv\ttskv_format=bs-watch-log\tunixtime=1596729841\trequestid=0005AC37A30876EC00030E8B850972DF\teventtime=1596729841\t" +
            "url=https://sbermarket.ru/lenta/molochnyie-produkty/moloko/korovie?sid\\=353\tfuniqid=0\ttype=0\thit=851544224\tpart=1\t" +
            "browserinfo=ti:1:v:1916:z:180:i:20200806190203:rqnl:1:st:1596729842:u:1593253625414658347:pp:2347192675\t" +
            "counterid=55275628\tuniqid=3828707081586720063\tcounterclass=0\tantivirusyes=0\t" +
            "checksum=10001\tdata=<long_binary_data>\tetag=0\tlayerid=1";

    private CountersServerCounterIdExistsState counterServerClient;
    private EventLogBatchSerializer serializer;

    @Before
    public void init() {
        counterServerClient = mock(CountersServerCounterIdExistsState.class);
        when(counterServerClient.exists(MockitoHamcrest.intThat(Matchers.greaterThan(0)))).thenReturn(true);

        serializer = new EventLogBatchSerializer(counterServerClient);
        serializer.setMaxPossibleDelay(Long.MAX_VALUE);
    }

    @Test
    public void negativeTests() {
        assertTrue(CollectionUtils.isEqualCollection(Collections.emptyList(), serializer.deserialize("".getBytes())));
        assertTrue(CollectionUtils.isEqualCollection(Collections.emptyList(), serializer.deserialize("\n\n".getBytes())));
        assertTrue(CollectionUtils.isEqualCollection(Collections.emptyList(), serializer.deserialize("\t\t\t".getBytes())));
        assertTrue(CollectionUtils.isEqualCollection(Collections.emptyList(), serializer.deserialize(null)));
        assertTrue(CollectionUtils.isEqualCollection(Collections.emptyList(), serializer.deserialize("tskv\ttskv_format=bs-watch-log\tcounterclass=gdsdfg".getBytes())));
        assertTrue(CollectionUtils.isEqualCollection(Collections.emptyList(), serializer.deserialize("tskv\ttskv_format=bs-watch-log\tcounterclass=gdsdfg\tcounterid=fggdf".getBytes())));
        assertTrue(CollectionUtils.isEqualCollection(Collections.emptyList(), serializer.deserialize("tskv\ttskv_format=bs-watch-log\tcounterid=-1".getBytes())));
    }

    @Test
    public void testSingleLineWrongOrder() {
        EventLogCommon[] result = serializer.deserialize(tskvGoodDataSinglelineWrongOrder.getBytes()).toArray(new EventLogCommon[0]);

        assertEquals(1, result.length);
        assertEquals(1596729841L * 1000, result[0].getMetadata().rawEventTime);
        assertEquals(55275628, result[0].getCounterId());
        assertEquals(3828707081586720063L, result[0].getVisitorId());
        assertEquals(0, result[0].getMetadata().counterClass);
        assertEquals("https://sbermarket.ru/lenta/molochnyie-produkty/moloko/korovie?sid=353", result[0].getMetadata().url);
        assertEquals(851544224, result[0].getMetadata().clientHitId);
        assertEquals(EventMessageType.EVENT, result[0].getMetadata().messageType);
        assertTrue(result[0].getMetadata().visorEnabled);
        assertArrayEquals("<long_binary_data>".getBytes(), result[0].getData());
    }

    @Test
    public void testMultiline() {
        EventLogCommon[] result = serializer.deserialize(tskvGoodDataMultiline.getBytes()).toArray(new EventLogCommon[0]);

        assertEquals(2, result.length);

        assertEquals(1596729841L * 1000, result[0].getMetadata().rawEventTime);
        assertEquals(1596729842L * 1000, result[1].getMetadata().rawEventTime);

        assertEquals(55275628, result[0].getCounterId());
        assertEquals(46483494, result[1].getCounterId());

        assertEquals(3828707081586720063L, result[0].getVisitorId());
        assertEquals(2417057451499663336L, result[1].getVisitorId());

        assertEquals(0, result[0].getMetadata().counterClass);
        assertEquals(0, result[1].getMetadata().counterClass);

        assertEquals("https://sbermarket.ru/lenta/molochnyie-produkty/moloko/korovie?sid=353", result[0].getMetadata().url);
        assertEquals("https://www.pharmeconom.ru/catalog/?q=%D0%9A%D0%B0%D0%BD%D0%B4%D0%B5%D1%81%D0%B0%D1%80%D0%B8%D0%B0%D0%BD&s=", result[1].getMetadata().url);

        assertEquals(851544224, result[0].getMetadata().clientHitId);
        assertEquals(183151828, result[1].getMetadata().clientHitId);

        assertEquals(EventMessageType.EVENT, result[0].getMetadata().messageType);
        assertEquals(EventMessageType.WV2_EVENT_PROTO, result[1].getMetadata().messageType);

        assertTrue(result[0].getMetadata().visorEnabled);
        assertTrue(result[1].getMetadata().visorEnabled);

        assertArrayEquals("<long_binary_data>".getBytes(), result[0].getData());
        assertArrayEquals("<\"long_\tbinary\0_data>".getBytes(), result[1].getData());
    }
}
