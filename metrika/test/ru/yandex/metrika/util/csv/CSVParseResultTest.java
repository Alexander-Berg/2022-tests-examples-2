package ru.yandex.metrika.util.csv;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;

import com.google.common.collect.Lists;
import org.junit.Test;

import static org.hamcrest.Matchers.equalTo;
import static org.junit.Assert.assertThat;

/**
 * @author zgmnkv
 */
public class CSVParseResultTest {

    public static final String COLUMN = "Column";

    @Test
    public void testRowNumber() {
        CSVParseResult<Integer> parseResult = new CSVParser<>(record -> record.getInt(COLUMN), List.of(new CSVColumnDescriptor(COLUMN)))
                .parse(new ByteArrayInputStream((COLUMN + "\n1\n\n2").getBytes(StandardCharsets.UTF_8)));

        Lists.newArrayList(parseResult.iterator());

        assertThat(parseResult.getSourceRowNumber(), equalTo(2L));
        assertThat(parseResult.getRowNumber(), equalTo(2L));
    }

    @Test
    public void testRowNumberWithInvalid() {
        CSVParseResult<Integer> parseResult = new CSVParser<>(record -> record.getInt(COLUMN), List.of(new CSVColumnDescriptor(COLUMN)))
                .parse(new ByteArrayInputStream((COLUMN + "\n1\n\nNotValid\n2").getBytes(StandardCharsets.UTF_8)));

        Lists.newArrayList(parseResult.iterator());

        assertThat(parseResult.getSourceRowNumber(), equalTo(3L));
        assertThat(parseResult.getRowNumber(), equalTo(2L));
    }
}
