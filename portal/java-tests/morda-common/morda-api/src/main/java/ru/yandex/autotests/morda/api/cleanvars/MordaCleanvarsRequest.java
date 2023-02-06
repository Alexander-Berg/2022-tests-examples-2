package ru.yandex.autotests.morda.api.cleanvars;

import ru.yandex.autotests.morda.beans.cleanvars.MordaCleanvars;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.restassured.requests.GetRequest;
import ru.yandex.autotests.morda.restassured.requests.TypifiedRestAssuredRequest;

import java.net.URI;
import java.util.List;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.morda.api.MordaRequestActions.prepareRequest;

public class MordaCleanvarsRequest
        extends TypifiedRestAssuredRequest<MordaCleanvarsRequest, MordaCleanvars>
        implements GetRequest<MordaCleanvarsRequest> {

    private Morda<?> morda;

    public MordaCleanvarsRequest(URI url) {
        super(MordaCleanvars.class, url);
        step("Get cleanvars");
        queryParam("cleanvars", 1);
    }

    public MordaCleanvarsRequest(Morda<?> morda) {
        super(MordaCleanvars.class, morda.getUrl());
        this.morda = morda;
        prepareRequest(this, morda);
        queryParam("cleanvars", 1);
        step("Get cleanvars");
    }

    public MordaCleanvarsRequest(Morda<?> morda, String... blocks) {
        this(morda, asList(blocks));
    }

    public MordaCleanvarsRequest(Morda<?> morda, MordaCleanvarsBlock... blocks) {
        this(morda, asList(blocks).stream().map(MordaCleanvarsBlock::getBlockName).collect(toList()));
    }

    public MordaCleanvarsRequest(Morda<?> morda, List<String> blocks) {
        this(morda);
        String cleanvarsQuery = blocks.stream()
                .map(e -> "^" + e + "$")
                .collect(joining("|"));
        queryParams.remove("cleanvars");
        queryParam("cleanvars", cleanvarsQuery);
    }

    public Morda<?> getMorda() {
        return morda;
    }

    @Override
    public MordaCleanvarsRequest me() {
        return this;
    }
}