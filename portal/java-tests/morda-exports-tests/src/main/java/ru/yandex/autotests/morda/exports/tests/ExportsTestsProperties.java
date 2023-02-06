package ru.yandex.autotests.morda.exports.tests;

import org.apache.commons.beanutils.ConvertUtils;
import org.apache.commons.beanutils.Converter;
import ru.yandex.autotests.morda.MordaPagesProperties;
import ru.yandex.autotests.morda.exports.tests.checks.ExportChecks;
import ru.yandex.qatools.properties.PropertyLoader;
import ru.yandex.qatools.properties.annotations.Property;
import ru.yandex.qatools.properties.annotations.Resource;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

/**
 * User: eroshenkoam
 * Date: 11/8/13, 1:57 PM
 */
@Resource.Classpath("morda-exports-tests.properties")
public class ExportsTestsProperties {

    private MordaPagesProperties mordaPagesProperties = new MordaPagesProperties();

    public ExportsTestsProperties() {
        ConvertUtils.register(new ListConverter(", "), List.class);
        PropertyLoader.populate(this);
        ConvertUtils.deregister(List.class);
    }

    @Property("exports.to.check")
    private List<String> exportsToCheck;

    @Property("exports.ping.links")
    private boolean exportPingLinks;

    public String getEnvironment() {
        return mordaPagesProperties.getEnvironment();
    }

    public List<String> getExportsToCheck() {
        return exportsToCheck != null
                ? exportsToCheck
                : new ArrayList<>();
    }

    public List<ExportChecks> filter(List<ExportChecks> exportChecks) {
        return exportChecks.stream()
                .filter(this::needCheck)
                .collect(Collectors.toList());
    }

    public boolean needCheck(ExportChecks<?, ?> checks) {
        return getExportsToCheck().contains(checks.getExport().getName());
    }

    public boolean isExportPingLinks() {
        return exportPingLinks;
    }

    private static class ListConverter implements Converter {
        private String delimiter;

        public ListConverter(String delimiter) {
            this.delimiter = delimiter;
        }

        public Object convert(Class aClass, Object o) {
            if(!(o instanceof String)) {
                return new ArrayList();
            } else {
                String str = (String)o;
                return Arrays.asList(str.split(this.delimiter));
            }
        }
    }

}
