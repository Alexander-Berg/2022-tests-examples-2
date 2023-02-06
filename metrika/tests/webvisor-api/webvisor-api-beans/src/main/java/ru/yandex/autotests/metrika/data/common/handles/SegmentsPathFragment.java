package ru.yandex.autotests.metrika.data.common.handles;

public enum SegmentsPathFragment {
    API("apisegment/"),
    INTERFACE("");

    private final String fragment;

    SegmentsPathFragment(String fragment) {
        this.fragment = fragment;
    }

    public String getFragment() {
        return fragment;
    }
}
