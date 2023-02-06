package ru.yandex.metrika.api.constructor.ga;

/**
* @author jkee
*/
class Result {

    final String target;
    String reason;
    boolean gaFail;
    boolean ourFail;
    boolean isMetric;
    boolean isStub;
    long leftTime;
    long rightTime;

    String leftUrl;
    String rightUrl;

    Result(String target) {
        this.target = target;
    }

    Result(String target, String reason, boolean isMetric) {
        this.target = target;
        this.reason = reason;
        this.isMetric = isMetric;
    }

    Result(String target, String reason, boolean gaFail, boolean ourFail, boolean isMetric) {
        this.target = target;
        this.reason = reason;
        this.gaFail = gaFail;
        this.ourFail = ourFail;
        this.isMetric = isMetric;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public void setGaFail(boolean gaFail) {
        this.gaFail = gaFail;
    }

    public void setOurFail(boolean ourFail) {
        this.ourFail = ourFail;
    }

    public boolean isMetric() {
        return isMetric;
    }

    public void setMetric(boolean isMetric) {
        this.isMetric = isMetric;
    }

    @Override
    public String toString() {
        return "Result{" +
                "target='" + target + '\'' +
                ", reason='" + reason + '\'' +
                '}';
    }

    public void setStub(boolean isStub) {
        this.isStub = isStub;
    }

    public void setLeftUrl(String leftUrl) {
        this.leftUrl = leftUrl;
    }

    public void setRightUrl(String rightUrl) {
        this.rightUrl = rightUrl;
    }

    public long getLeftTime() {
        return leftTime;
    }

    public void setLeftTime(long leftTime) {
        this.leftTime = leftTime;
    }

    public long getRightTime() {
        return rightTime;
    }

    public void setRightTime(long rightTime) {
        this.rightTime = rightTime;
    }
}
