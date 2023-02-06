package ru.yandex.metrika.mobmet.model;

import java.util.List;

import org.apache.commons.lang3.StringUtils;
import org.junit.Test;

import ru.yandex.metrika.mobmet.exception.InvalidColumnFormatException;
import ru.yandex.metrika.mobmet.model.redirect.PostbackHeader;

import static org.assertj.core.api.Assertions.assertThat;

public class PostbackHeadersTest {

    private static final String ONE_LINE_STR = "Authorization: Token token=REPLACE_THIS";
    private static final List<PostbackHeader> ONE_LINE_HEADERS = List.of(
            new PostbackHeader("Authorization", "Token token=REPLACE_THIS"));

    private static final String TWO_LINE_STR = "Authorization: Token token=REPLACE_THIS\n" +
            "User-Agent: Mozilla/5.0 (compatible; YandexMetrika/2.0; +http://yandex.com/bots)";
    private static final List<PostbackHeader> TWO_LINE_HEADERS = List.of(
            new PostbackHeader("Authorization", "Token token=REPLACE_THIS"),
            new PostbackHeader("User-Agent", "Mozilla/5.0 (compatible; YandexMetrika/2.0; +http://yandex.com/bots)"));

    @Test
    public void emptyParse() {
        List<PostbackHeader> actual = PostbackHeader.parse(StringUtils.EMPTY);
        assertThat(actual).isEmpty();
    }

    @Test
    public void oneLineParse() {
        List<PostbackHeader> actual = PostbackHeader.parse(ONE_LINE_STR);
        assertThat(actual).isEqualTo(ONE_LINE_HEADERS);
    }

    @Test
    public void manyLinesParse() {
        List<PostbackHeader> actual = PostbackHeader.parse(TWO_LINE_STR);
        assertThat(actual).isEqualTo(TWO_LINE_HEADERS);
    }

    @Test(expected = InvalidColumnFormatException.class)
    public void missingColon() {
        PostbackHeader.parse("Authorization Token token=REPLACE_THIS");
    }

    @Test(expected = InvalidColumnFormatException.class)
    public void extraNewLine() {
        PostbackHeader.parse("Authorization Token token=REPLACE_THIS\n");
    }

    @Test
    public void emptyToDbValue() {
        String actual = PostbackHeader.toDbValue(List.of());
        assertThat(actual).isEqualTo(StringUtils.EMPTY);
    }

    @Test
    public void oneLineToDbValue() {
        String actual = PostbackHeader.toDbValue(ONE_LINE_HEADERS);
        assertThat(actual).isEqualTo(ONE_LINE_STR);
    }

    @Test
    public void manyLinesToDbValue() {
        String actual = PostbackHeader.toDbValue(TWO_LINE_HEADERS);
        assertThat(actual).isEqualTo(TWO_LINE_STR);
    }
}
