package ru.yandex.metrika.api.constructor.ga;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;

import ru.yandex.metrika.util.collections.StringMap;
import ru.yandex.metrika.util.io.UncheckedIOException;

/**
 * @author jkee
 */

public class GAAttrsGrabber {

    public static final String URL = "https://www.googleapis.com/analytics/v3/metadata/ga/columns";

    List<GAAttr> items;
    List<String> dims;
    List<String> metrics;

    List<String> allDims;
    List<String> allMetrics;

    public void grab() {
        items = getItems();
        dims = getGoodItemsOfType("DIMENSION", false);
        metrics = getGoodItemsOfType("METRIC", false);
        allDims = getGoodItemsOfType("DIMENSION", true);
        allMetrics = getGoodItemsOfType("METRIC", true);
        System.out.println(dims);
        System.out.println(metrics);
        System.out.println(dims.size());
        System.out.println(metrics.size());
    }

    public List<String> getDims() {
        return dims;
    }

    public List<String> getMetrics() {
        return metrics;
    }

    public List<String> getAllDims() {
        return allDims;
    }

    public List<String> getAllMetrics() {
        return allMetrics;
    }

    public static void main(String[] args) {
        new GAAttrsGrabber().grab();
    }

    public List<String> getGoodItemsOfType(final String type, final boolean includeDeprecated) {
        return items.stream()
        .filter(input -> !"DEPRECATED".equals(input.attributes.get("status"))
                && (includeDeprecated || type.equals(input.attributes.get("type"))))
        .map(GAAttr::getId).collect(Collectors.toList());
    }

    private List<GAAttr> getItems() {
        try {
            HttpGet request = new HttpGet(URL);
            HttpResponse response = new DefaultHttpClient().execute(request);
            ObjectMapper objectMapper = new ObjectMapper();
            objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
            GAResponse gaResponse = objectMapper.readValue(response.getEntity().getContent(), GAResponse.class);
            return gaResponse.getItems();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static class GAResponse {
        List<GAAttr> items;

        public List<GAAttr> getItems() {
            return items;
        }

        public void setItems(List<GAAttr> items) {
            this.items = items;
        }
    }

    public static class GAAttr {
        private String id;
        private StringMap attributes;

        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }

        public StringMap getAttributes() {
            return attributes;
        }

        public void setAttributes(StringMap attributes) {
            this.attributes = attributes;
        }
    }


}
