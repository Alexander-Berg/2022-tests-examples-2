package ru.yandex.metrika.visor3d.steps;

import org.springframework.stereotype.Component;

import static java.lang.String.format;

@Component
public class Visor3dSettings {

    private String queuesRoot = "/metrika-testing";

    private String inputQueuesSuffix = "/Visor3d_RecountRequests";

    private String inputQueuesPath = format("%s/layer01%s", queuesRoot, inputQueuesSuffix);

    private String outputQueuesSuffix = "/WVEvents2_RecountRequests";

    private String outputQueuesPath = format("%s/layer01%s", queuesRoot, outputQueuesSuffix);

    private String inputDataBase = "webvisor2_001";

    private String outputDataBase = "wv2_visit_log_001";

    private String outputScrollsDataBase = "wv";

    private String ytPathPrefix = "//home";

    private String outputYtPath = format("%s/webvisor2_events", ytPathPrefix);

    private String logbrokerEventsTopic = "events";

    private String logbrokerStaticTopic = "static";

    private String logbrokerCryptaTopic = "crypta";

    private String logbrokerScrollsTopic = "scrolls";

    private String logbrokerFormsTopic = "forms";

    private String logbrokerSourceWvLogTopic = "webvisorlog";

    private String logbrokerWvSasAppendLogTopic = "wv-append-to-sas-log";

    private String logbrokerSourceWvVlaAppendLogTopic = "wv-append-to-vla-log";

    public String getQueuesRoot() {
        return queuesRoot;
    }

    public Visor3dSettings withQueuesRoot(String queuesRoot) {
        this.queuesRoot = queuesRoot;
        return this;
    }

    public void setQueuesRoot(String queuesRoot) {
        this.queuesRoot = queuesRoot;
    }

    public String getInputQueuesSuffix() {
        return inputQueuesSuffix;
    }

    public void setInputQueuesSuffix(String inputQueuesSuffix) {
        this.inputQueuesSuffix = inputQueuesSuffix;
    }

    public Visor3dSettings withInputQueuesSuffix(String inputQueuesSuffix) {
        this.inputQueuesSuffix = inputQueuesSuffix;
        return this;
    }

    public String getInputQueuesPath() {
        return inputQueuesPath;
    }

    public void setInputQueuesPath(String inputQueuesPath) {
        this.inputQueuesPath = inputQueuesPath;
    }

    public Visor3dSettings withInputQueuesPath(String inputQueuesPath) {
        this.inputQueuesPath = inputQueuesPath;
        return this;
    }

    public String getOutputQueuesSuffix() {
        return outputQueuesSuffix;
    }

    public void setOutputQueuesSuffix(String outputQueuesSuffix) {
        this.outputQueuesSuffix = outputQueuesSuffix;
    }

    public Visor3dSettings withOutputQueuesSuffix(String outputQueuesSuffix) {
        this.outputQueuesSuffix = outputQueuesSuffix;
        return this;
    }

    public String getOutputQueuesPath() {
        return outputQueuesPath;
    }

    public void setOutputQueuesPath(String outputQueuesPath) {
        this.outputQueuesPath = outputQueuesPath;
    }

    public Visor3dSettings withOutputQueuesPath(String outputQueuesPath) {
        this.outputQueuesPath = outputQueuesPath;
        return this;
    }

    public String getInputDataBase() {
        return inputDataBase;
    }

    public void setInputDataBase(String inputDataBase) {
        this.inputDataBase = inputDataBase;
    }

    public Visor3dSettings withInputDataBase(String inputDataBase) {
        this.inputDataBase = inputDataBase;
        return this;
    }

    public String getOutputDataBase() {
        return outputDataBase;
    }

    public void setOutputDataBase(String outputDataBase) {
        this.outputDataBase = outputDataBase;
    }

    public Visor3dSettings withOutputDataBase(String outputDataBase) {
        this.outputDataBase = outputDataBase;
        return this;
    }

    public String getOutputScrollsDataBase() {
        return outputScrollsDataBase;
    }

    public void setOutputScrollsDataBase(String outputScrollsDataBase) {
        this.outputScrollsDataBase = outputScrollsDataBase;
    }

    public Visor3dSettings withOutputScrollsDataBase(String outputScrollsDataBase) {
        this.outputScrollsDataBase = outputScrollsDataBase;
        return this;
    }

    public String getYtPathPrefix() {
        return ytPathPrefix;
    }

    public void setYtPathPrefix(String ytPathPrefix) {
        this.ytPathPrefix = ytPathPrefix;
    }

    public Visor3dSettings withYtPathPrefix(String ytPathPrefix) {
        this.ytPathPrefix = ytPathPrefix;
        return this;
    }

    public String getOutputYtPath() {
        return outputYtPath;
    }

    public void setOutputYtPath(String outputYtPath) {
        this.outputYtPath = outputYtPath;
    }

    public Visor3dSettings withOutputYtPath(String outputYtPath) {
        this.outputYtPath = outputYtPath;
        return this;
    }

    public String getLogbrokerEventsTopic() {
        return logbrokerEventsTopic;
    }

    public void setLogbrokerEventsTopic(String logbrokerEventsTopic) {
        this.logbrokerEventsTopic = logbrokerEventsTopic;
    }

    public Visor3dSettings withLogbrokerEventsTopic(String logbrokerEventsTopic) {
        this.logbrokerEventsTopic = logbrokerEventsTopic;
        return this;
    }

    public String getLogbrokerStaticTopic() {
        return logbrokerStaticTopic;
    }

    public void setLogbrokerStaticTopic(String logbrokerStaticTopic) {
        this.logbrokerStaticTopic = logbrokerStaticTopic;
    }

    public Visor3dSettings withLogbrokerStaticTopic(String logbrokerStaticTopic) {
        this.logbrokerStaticTopic = logbrokerStaticTopic;
        return this;
    }

    public String getLogbrokerCryptaTopic() {
        return logbrokerCryptaTopic;
    }

    public void setLogbrokerCryptaTopic(String logbrokerCryptaTopic) {
        this.logbrokerCryptaTopic = logbrokerCryptaTopic;
    }

    public Visor3dSettings withLogbrokerCryptaTopic(String logbrokerCryptaTopic) {
        this.logbrokerCryptaTopic = logbrokerCryptaTopic;
        return this;
    }

    public String getLogbrokerScrollsTopic() {
        return logbrokerScrollsTopic;
    }

    public void setLogbrokerScrollsTopic(String logbrokerScrollsTopic) {
        this.logbrokerScrollsTopic = logbrokerScrollsTopic;
    }

    public Visor3dSettings withLogbrokerScrollsTopic(String logbrokerScrollsTopic) {
        this.logbrokerScrollsTopic = logbrokerScrollsTopic;
        return this;
    }

    public String getLogbrokerFormsTopic() {
        return logbrokerFormsTopic;
    }

    public void setLogbrokerFormsTopic(String logbrokerFormsTopic) {
        this.logbrokerFormsTopic = logbrokerFormsTopic;
    }

    public Visor3dSettings withLogbrokerFormsTopic(String logbrokerFormsTopic) {
        this.logbrokerFormsTopic = logbrokerFormsTopic;
        return this;
    }

    public String getLogbrokerSourceWvLogTopic() {
        return logbrokerSourceWvLogTopic;
    }

    public String getLogbrokerWvSasAppendLogTopic() {
        return logbrokerWvSasAppendLogTopic;
    }

    public String getLogbrokerSourceWvVlaAppendLogTopic() {
        return logbrokerSourceWvVlaAppendLogTopic;
    }
}
