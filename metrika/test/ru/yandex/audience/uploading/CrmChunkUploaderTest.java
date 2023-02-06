package ru.yandex.audience.uploading;

import java.util.Arrays;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.stream.Collectors;

import com.amazonaws.util.StringInputStream;
import com.netflix.servo.util.Iterables;
import com.netflix.servo.util.Strings;
import org.assertj.core.util.Lists;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.mockito.ArgumentMatchers;
import org.mockito.Mockito;

import ru.yandex.audience.SegmentStorageRow;
import ru.yandex.audience.uploading.crm.CrmSegmentParser;
import ru.yandex.audience.uploading.crm.HeaderValidationException;
import ru.yandex.metrika.util.chunk.ChunkContext;
import ru.yandex.metrika.util.chunk.clickhouse.haze.CreateHazeChunkException;
import ru.yandex.metrika.util.chunk.clickhouse.haze.ReliableChunkStorage;
import ru.yandex.metrika.util.collections.F;

@RunWith(Parameterized.class)
public class CrmChunkUploaderTest {
    private final List<String> header = List.of("email", "phone", "ext_id", "key1");
    private final List<String>  invalidHeader = List.of("header", "without", "expected", "fields");

    private final List<List<String>> csvRows = Arrays.stream(new String[][] {
            {"some", "test", "data", "row"},
            {"another", "test", "data", "row"},
            {"\ttest", "row\t", "wi\tth", "tabs"}
    }).map(Arrays::asList).toList();

    @Parameterized.Parameter
    public List<Integer> originalChunkHeaderColumnIds;

    private ReliableChunkStorage<SegmentStorageRow> chunkStorage;
    private String uploadingResult;

    @Parameterized.Parameters
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {List.of(0, 1, 2, 3)},
                {List.of(0, 1, 2)},
                {List.of(0, 2, 3)},
                {List.of(1, 3)},
                {List.of(3, 2, 1, 0)},
                {List.of(3, 1, 0)}
        });
    }

    @Before
    public void setup() throws CreateHazeChunkException {
        chunkStorage = Mockito.mock(ReliableChunkStorage.class);

        Mockito.when(chunkStorage.createChunkStream(ArgumentMatchers.any(Iterator.class))).thenAnswer(args -> {
            uploadingResult = Strings.join("\n",
                    F.map(args.getArgument(0, Iterator.class), key -> ((SegmentStorageRow) key).getKey()));
            return ChunkContext.NOT_CHUNK;
        });
    }

    private String getCsv(List<Integer> columns, boolean isInvalid) {
        return Lists.newArrayList(Iterables.concat(List.of(isInvalid ? invalidHeader : header), csvRows)).stream()
                .map(row -> extractColumns(row, columns))
                .collect(Collectors.joining("\n"));
    }

    private String extractColumns(List<String> row, List<Integer> columns) {
        return columns.stream().map(row::get).collect(Collectors.joining(","));
    }

    @Test
    public void testUpload() throws Exception {
        String uploadCsv = getCsv(List.of(0, 1, 2, 3), false);

        CrmChunkUploader chunkUploader = new CrmChunkUploader(
                chunkStorage,
                true,
                new CrmSegmentParser(extractColumns(header, originalChunkHeaderColumnIds))
        );

        chunkUploader.upload(new StringInputStream(uploadCsv));

        String expectedCsv = getCsv(originalChunkHeaderColumnIds, false);

        Assert.assertEquals(expectedCsv, uploadingResult);
    }


    @Test(expected = HeaderValidationException.class)
    public void testInvalidCrmHeader() throws Exception {
        String uploadCsv = getCsv(List.of(0, 1, 2, 3), true);

        CrmChunkUploader chunkUploader = new CrmChunkUploader(
                chunkStorage,
                true,
                new CrmSegmentParser(extractColumns(header, originalChunkHeaderColumnIds))
        );

        chunkUploader.upload(new StringInputStream(uploadCsv));
    }
}
