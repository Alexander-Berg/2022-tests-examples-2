package ru.yandex.metrika.api.management.client.connectors;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import com.google.ads.googleads.v9.services.GoogleAdsRow;
import com.google.protobuf.TextFormat;
import org.apache.commons.compress.utils.Lists;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.connectors.google.GoogleAdsReportApiWrapper;
import ru.yandex.metrika.api.management.client.connectors.google.GoogleReportIterator;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;

public class GoogleReportIteratorTest {

    private GoogleReportIterator googleReportIterator;

    @BeforeClass
    public static void initClass() {
        Log4jSetup.basicSetup();
    }

    @Before
    public void init() throws Exception {
        GoogleAdsReportApiWrapper reportApiWrapperMock = mock(GoogleAdsReportApiWrapper.class);
        doNothing().when(reportApiWrapperMock).makeCall();
        doNothing().when(reportApiWrapperMock).close();
        doReturn(true).doReturn(true).doReturn(true).doReturn(true).doReturn(true).doReturn(false).when(reportApiWrapperMock).hasRemaining();
        doReturn(loadData("report_chunk_1"))
                .doReturn(loadData("report_chunk_2"))
                .doReturn(loadData("report_chunk_3"))
                .doReturn(loadData("report_chunk_4"))
                .doReturn(loadData("report_chunk_5"))
                .when(reportApiWrapperMock).getNextChunk();

        googleReportIterator = new GoogleReportIterator(reportApiWrapperMock);
    }

    @Test
    public void testChunkedResponse() {
        List<GoogleAdsRow> result = Lists.newArrayList(googleReportIterator);
        assertEquals(20, result.size());
    }

    @Test
    public void testContent() {
        List<GoogleAdsRow> result = Lists.newArrayList(googleReportIterator);

        assertEquals(677L, result.stream().map(row -> row.getMetrics().getImpressions()).reduce(Long::sum).orElseThrow().longValue());
        assertEquals(102L, result.stream().map(row -> row.getMetrics().getClicks()).reduce(Long::sum).orElseThrow().longValue());
        assertEquals(2228310000L, result.stream().map(row -> row.getMetrics().getCostMicros()).reduce(Long::sum).orElseThrow().longValue());

        assertTrue(
                result.stream()
                        .map(row -> row.getAdGroup().getResourceName())
                        .allMatch(rn -> rn.startsWith("customers/2265901308/"))
        );
    }

    public List<GoogleAdsRow> loadData(String fileName) {
        List<GoogleAdsRow> result = new ArrayList<>();

        try (BufferedReader reader =
                     new BufferedReader(new InputStreamReader(this.getClass().getResourceAsStream("test_data/" + fileName)))
        ) {
            String line;
            while ((line = reader.readLine()) != null) {
                GoogleAdsRow.Builder builder = GoogleAdsRow.newBuilder();
                TextFormat.merge(line, builder);
                result.add(builder.build());
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        return result;
    }
}
