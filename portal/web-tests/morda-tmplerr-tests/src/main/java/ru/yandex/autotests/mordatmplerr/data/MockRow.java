package ru.yandex.autotests.mordatmplerr.data;

import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.testlab.wiki.annotations.WikiColumn;
import ru.yandex.testlab.wiki.annotations.WikiRow;

import java.util.ArrayList;
import java.util.List;

import static ru.yandex.autotests.mordatmplerr.data.MockType.getMockType;
import static ru.yandex.autotests.utils.morda.url.Domain.getDomain;

@WikiRow(pageUrl = "Users/eoff/morda-mocks/")
public class MockRow {

    @WikiColumn(name = "mock")
    private String mock;

    @WikiColumn(name = "types", delimiter = " ")
    private List<String> types;

    @WikiColumn(name = "domains", delimiter = " ")
    private List<String> domains;

    @WikiColumn(name = "geoId")
    private String geoId;

    public String getMock() {
        return mock;
    }

    public void setMock(String mock) {
        this.mock = mock;
    }

    public List<String> getTypes() {
        return types;
    }

    public List<Domain> getMockDomains() {
        List<Domain> result = new ArrayList<>();
        for (String type : getDomains()) {
            result.add(getDomain(type));
        }
        return result;
    }

    public List<MockType> getMockTypes() {
        List<MockType> result = new ArrayList<>();
        for (String type : getTypes()) {
            result.add(getMockType(type));
        }
        return result;
    }

    public void setTypes(List<String> types) {
        this.types = types;
    }

    public String getGeoId() {
        return geoId;
    }

    public void setGeoId(String geoId) {
        this.geoId = geoId;
    }

    @Override
    public String toString() {
        return mock;
    }

    public void setDomains(List<String> domains) {
        this.domains = domains;
    }

    public List<String> getDomains() {
        return domains;
    }
}