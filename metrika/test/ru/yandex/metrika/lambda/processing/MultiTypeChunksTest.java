package ru.yandex.metrika.lambda.processing;

import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.lambda.YtChunks;
import ru.yandex.metrika.lambda.YtChunks.TableInfo;
import ru.yandex.metrika.lambda.task.MetrikaLogType;
import ru.yandex.metrika.lambda.util.MultiTypeChunks;
import ru.yandex.metrika.util.collections.Lists2;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyInt;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static ru.yandex.metrika.lambda.task.MetrikaChunkStatus.absorbed;
import static ru.yandex.metrika.lambda.task.MetrikaChunkStatus.joined;
import static ru.yandex.metrika.lambda.task.MetrikaChunkStatus.mapped;

public class MultiTypeChunksTest {

    private MultiTypeChunks multiTypeChunks;

    private YtChunks mock1;
    private YtChunks mock2;
    private YtChunks mock3;

    private List<TableInfo> aChunks;
    private List<TableInfo> ayChunks;
    private List<TableInfo> adChunks;

    private List<TableInfo> allchunks;

    @SuppressWarnings("ResultOfMethodCallIgnored")
    @Before
    public void setUp() {
        mock1 = mock(YtChunks.class);
        mock2 = mock(YtChunks.class);
        mock3 = mock(YtChunks.class);

        doReturn(MetrikaLogType.a).when(mock1).getLogType();
        doReturn(MetrikaLogType.a_y).when(mock2).getLogType();
        doReturn(MetrikaLogType.a_d).when(mock3).getLogType();

        aChunks = ImmutableList.of(
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a, false),
                new TableInfo("2019-03-15T00:01:00", "", 0,0, mapped, MetrikaLogType.a, false),
                new TableInfo("2019-03-15T00:02:00", "", 0,0, mapped, MetrikaLogType.a, false)
        );

        ayChunks = ImmutableList.of(
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a_y, false),
                new TableInfo("2019-03-15T00:01:00", "", 0,0, mapped, MetrikaLogType.a_y, false),
                new TableInfo("2019-03-15T00:02:00", "", 0,0, mapped, MetrikaLogType.a_y, false)
        );

        adChunks = ImmutableList.of(
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a_d, false),
                new TableInfo("2019-03-15T00:01:00", "", 0,0, mapped, MetrikaLogType.a_d, false),
                new TableInfo("2019-03-15T00:02:00", "", 0,0, mapped, MetrikaLogType.a_d, false)
        );

        allchunks = ImmutableList.<TableInfo>builder().addAll(aChunks).addAll(ayChunks).addAll(adChunks).build();

        doReturn(aChunks.stream()).when(mock1).streamTopByStatuses(any(), anyInt(), eq(mapped));

        doReturn(Stream.empty()).when(mock1).streamTopByStatuses(any(), anyInt(), eq(joined));

        doReturn(ayChunks.stream()).when(mock2).streamTopByStatuses(any(), anyInt(), eq(mapped));

        doReturn(adChunks.stream()).when(mock3).streamTopByStatuses(any(), anyInt(), eq(mapped));

        multiTypeChunks = new MultiTypeChunks(ImmutableList.of(mock1, mock2, mock3), absorbed);
    }

    @Test
    public void getAllTopByStatuses3() {
        List<TableInfo> allTopByStatuses = multiTypeChunks.getAllTopByStatuses(TableInfo.comparingByName, 3, mapped);
        assertEquals(allTopByStatuses.size(),3);
        assertEquals(allTopByStatuses, ImmutableList.of(
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a, false),
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a_y, false),
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a_d, false)
        ));
    }

    @Test
    public void getAllTopByStatuses5() {
        List<TableInfo> allTopByStatuses = multiTypeChunks.getAllTopByStatuses(TableInfo.comparingByName, 5, mapped);
        assertEquals(allTopByStatuses.size(),5);
        assertEquals(allTopByStatuses, ImmutableList.of(
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a, false),
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a_y, false),
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a_d, false),
                new TableInfo("2019-03-15T00:01:00", "", 0,0, mapped, MetrikaLogType.a, false),
                new TableInfo("2019-03-15T00:01:00", "", 0,0, mapped, MetrikaLogType.a_y, false)
        ));
    }

    @Test
    public void getAllTopByStatusesFunc() {
        List<TableInfo> allTopByStatuses = multiTypeChunks.getAllTopByStatuses(TableInfo.comparingByName, 100, logType -> logType == MetrikaLogType.a ? joined : mapped);
        assertEquals(allTopByStatuses.size(),6);
        assertEquals(allTopByStatuses, ImmutableList.of(
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a_y, false),
                new TableInfo("2019-03-15T00:00:00", "", 0,0, mapped, MetrikaLogType.a_d, false),
                new TableInfo("2019-03-15T00:01:00", "", 0,0, mapped, MetrikaLogType.a_y, false),
                new TableInfo("2019-03-15T00:01:00", "", 0,0, mapped, MetrikaLogType.a_d, false),
                new TableInfo("2019-03-15T00:02:00", "", 0,0, mapped, MetrikaLogType.a_y, false),
                new TableInfo("2019-03-15T00:02:00", "", 0,0, mapped, MetrikaLogType.a_d, false)
        ));
    }

    @Test
    public void extractA() {
        List<TableInfo> extract = multiTypeChunks.extract(allchunks, MetrikaLogType.a);
        assertEquals(extract, aChunks);
    }

    @Test
    public void extractAY() {
        List<TableInfo> extract = multiTypeChunks.extract(allchunks, MetrikaLogType.a_y);
        assertEquals(extract, ayChunks);
    }

    @Test
    public void extractAD() {
        List<TableInfo> extract = multiTypeChunks.extract(allchunks, MetrikaLogType.a_d);
        assertEquals(extract, adChunks);
    }

    @Test
    public void extractFirstA() {
        Optional<TableInfo> tableInfo = multiTypeChunks.extractFirst(allchunks);
        assertTrue(tableInfo.isPresent());
        assertEquals(aChunks.get(0), tableInfo.get());
    }

    @Test
    public void extractFirstAY() {
        Optional<TableInfo> tableInfo = multiTypeChunks.extractFirst(Lists2.concat(ayChunks, adChunks));
        assertTrue(tableInfo.isPresent());
        assertEquals(ayChunks.get(0), tableInfo.get());
    }

    @Test
    public void extractFirstAD() {
        Optional<TableInfo> tableInfo = multiTypeChunks.extractFirst(adChunks);
        assertTrue(tableInfo.isPresent());
        assertEquals(adChunks.get(0), tableInfo.get());
    }

    @Test
    public void setStatusForAll() {
        multiTypeChunks.setStatusForAll(allchunks, joined, mapped);
        for (TableInfo aChunk : aChunks) {
            verify(mock1, times(1)).setStatus(aChunk.name, joined, mapped);
        }
        for (TableInfo ayChunk : ayChunks) {
            verify(mock2, times(1)).setStatus(ayChunk.name, joined, mapped);
        }
        for (TableInfo adChunk : aChunks) {
            verify(mock3, times(1)).setStatus(adChunk.name, joined, mapped);
        }
    }

    @Test
    public void absorbAndMerge() {
        multiTypeChunks.absorbAndMerge(allchunks, joined, mapped, "path");
        verify(mock1, times(1)).absorb(aChunks, aChunks.get(0), joined, mapped, absorbed, "path");
        verify(mock2, times(1)).absorb(ayChunks, aChunks.get(0), joined, mapped, absorbed, "path");
        verify(mock3, times(1)).absorb(adChunks, aChunks.get(0), joined, mapped, absorbed, "path");
    }

    @Test
    public void absorbAndMerge1() {
        multiTypeChunks.absorbAndMerge(Lists2.concat(ayChunks, adChunks), joined, mapped, "path");
        verify(mock2, times(1)).absorb(ayChunks, ayChunks.get(0), joined, mapped, absorbed, "path");
        verify(mock3, times(1)).absorb(adChunks, ayChunks.get(0), joined, mapped, absorbed, "path");
    }

    @Test
    public void absorbAndMerge2() {
        multiTypeChunks.absorbAndMerge(Lists2.concat(aChunks, adChunks), joined, mapped, "path");
        verify(mock1, times(1)).absorb(aChunks, aChunks.get(0), joined, mapped, absorbed, "path");
        verify(mock3, times(1)).absorb(adChunks, aChunks.get(0), joined, mapped, absorbed, "path");
    }

    @Test
    public void absorbAndMerge3() {
        multiTypeChunks.absorbAndMerge(adChunks, joined, mapped, "path");
        verify(mock3, times(1)).absorb(adChunks, adChunks.get(0), joined, mapped, absorbed, "path");
    }
}
