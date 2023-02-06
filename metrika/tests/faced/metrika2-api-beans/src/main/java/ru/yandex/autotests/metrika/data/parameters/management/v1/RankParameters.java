package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by sonick on 25.12.15.
 */
public class RankParameters extends AbstractFormParameters {

    @FormParameter("counter_id")
    private Long counterId;

    @FormParameter("rank")
    private Long rank;

    public void setCounterId(Long counterId) {
        this.counterId = counterId;
    }

    public void setRank(Long rank) {
        this.rank = rank;
    }

    public Long getCounterId() {
        return counterId;
    }

    public Long getRank() {
        return rank;
    }

    public RankParameters withCounterId(Long counterId) {
        this.counterId = counterId;
        return this;
    }

    public RankParameters withRank(Long rank) {
        this.rank = rank;
        return this;
    }
}
