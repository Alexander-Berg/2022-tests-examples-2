package ru.yandex.metrika.mobmet.crash.decoder.steps;

import org.springframework.stereotype.Component;

import static java.lang.String.format;

@Component
public class MobmetCrashDecoderSettings {

    private String inputQueuesRoot = "/metrika-queues-misc/crash_decoder/layers";

    private String inputQueuesPath = format("%s/layer01/crash_decoder_events", inputQueuesRoot);

    private String outputQueuesRoot = "/metrika-queues-misc/decoded_crashes_import/layers";

    private String inputDataBase = "input_crash_decoder_events";

    private String outputDataBase = "output_crash_decoder_events";

    public String getInputQueuesRoot() {
        return inputQueuesRoot;
    }

    public void setInputQueuesRoot(String inputQueuesRoot) {
        this.inputQueuesRoot = inputQueuesRoot;
    }

    public MobmetCrashDecoderSettings withInputQueuesRoot(String inputQueuesRoot) {
        this.inputQueuesRoot = inputQueuesRoot;
        return this;
    }

    public String getInputQueuesPath() {
        return inputQueuesPath;
    }

    public void setInputQueuesPath(String inputQueuesPath) {
        this.inputQueuesPath = inputQueuesPath;
    }

    public MobmetCrashDecoderSettings withInputQueuesPath(String inputQueuesPath) {
        this.inputQueuesPath = inputQueuesPath;
        return this;
    }

    public String getOutputQueuesRoot() {
        return outputQueuesRoot;
    }

    public void setOutputQueuesRoot(String outputQueuesRoot) {
        this.outputQueuesRoot = outputQueuesRoot;
    }

    public MobmetCrashDecoderSettings withOutputQueuesRoot(String outputQueuesRoot) {
        this.outputQueuesRoot = outputQueuesRoot;
        return this;
    }

    public String getInputDataBase() {
        return inputDataBase;
    }

    public void setInputDataBase(String inputDataBase) {
        this.inputDataBase = inputDataBase;
    }

    public MobmetCrashDecoderSettings withInputDataBase(String inputDataBase) {
        this.inputDataBase = inputDataBase;
        return this;
    }

    public String getOutputDataBase() {
        return outputDataBase;
    }

    public void setOutputDataBase(String outputDataBase) {
        this.outputDataBase = outputDataBase;
    }

    public MobmetCrashDecoderSettings withOutputDataBase(String outputDataBase) {
        this.outputDataBase = outputDataBase;
        return this;
    }

}
