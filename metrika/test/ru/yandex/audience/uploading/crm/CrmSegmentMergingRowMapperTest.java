package ru.yandex.audience.uploading.crm;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.ArrayUtils;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class CrmSegmentMergingRowMapperTest {

    private static final CrmSegmentMergingRowMapper mapper = new CrmSegmentMergingRowMapper(Map.of(
            0, 0,
            2, 1,
            5, 3
    ), 6);

    @Test
    public void changesSchemaCorrectlyTest() {
        String[] row = new String[]{"first", "second", "third", "fourth"};

        var bytes = String.join(",", row).getBytes(StandardCharsets.UTF_8);

        List<Byte> buffer = new ArrayList<>();

        mapper.writeWithOriginalSchema(Arrays.asList(ArrayUtils.toObject(bytes)), buffer);

        var newRow = new String(ArrayUtils.toPrimitive(buffer.toArray(Byte[]::new)), StandardCharsets.UTF_8);

        assertEquals("first,,second,,,fourth", newRow);

    }
}
