package ru.yandex.metrika.visor3d.steps;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;

public class BrowserInfo {

    private int bufferType;
    private long eventTimestamp;
    private long sendTimestamp;
    private long duid;
    private long codeVersion;
    private String codeFeatures;

    public BrowserInfo() {
    }

    public BrowserInfo(int bufferType, long eventTimestamp, long sendTimestamp, long duid, long codeVersion, String codeFeatures) {
        this.bufferType = bufferType;
        this.eventTimestamp = eventTimestamp;
        this.sendTimestamp = sendTimestamp;
        this.duid = duid;
        this.codeVersion = codeVersion;
        this.codeFeatures = codeFeatures;
    }

    public int getBufferType() {
        return bufferType;
    }

    public void setBufferType(int bufferType) {
        this.bufferType = bufferType;
    }

    public long getEventTimestamp() {
        return eventTimestamp;
    }

    public void setEventTimestamp(long eventTimestamp) {
        this.eventTimestamp = eventTimestamp;
    }

    public long getSendTimestamp() {
        return sendTimestamp;
    }

    public void setSendTimestamp(long sendTimestamp) {
        this.sendTimestamp = sendTimestamp;
    }

    public String toBrowserString() {
        return "ti:8:v:" + codeVersion + ":vf:" + codeFeatures + ":z:300:i:20180201181427:u:" + duid + ":et:" + eventTimestamp + ":st:" + sendTimestamp +
                ":bt:" + bufferType;
    }

    public static BrowserInfo fromBrowserString(String s) {
        BrowserInfo bi = new BrowserInfo();
        Map<String, String> values = new HashMap<>();
        String[] split = Pattern.compile(":").split(s);
        for (int ii = 0; ii < split.length - 1; ii += 2) {
            values.put(split[ii], split[ii + 1]);
        }

        if (values.containsKey("et")) {
            bi.setEventTimestamp(Long.parseLong(values.get("et")));
        }
        if (values.containsKey("st")) {
            bi.setSendTimestamp(Long.parseLong(values.get("st")));
        }
        if (values.containsKey("bt")) {
            bi.setBufferType(Integer.parseInt(values.get("bt")));
        }
        if (values.containsKey("u")) {
            bi.setDuid(Long.parseUnsignedLong(values.get("u")));
        }
        if (values.containsKey("v")) {
            bi.setCodeVersion(Long.parseLong(values.get("v")));
        }
        if (values.containsKey("vf")) {
            bi.setCodeFeatures(values.get("vf"));
        }
        return bi;
    }

    public int getDeltaTime() {
        if (getSendTimestamp() - getEventTimestamp() < TimeUnit.DAYS.toSeconds(1)) {
            return (int) (getSendTimestamp() - getEventTimestamp());
        } else return 0;
    }

    public static int getDeltaTime(String browserInfo) {
        return BrowserInfo.fromBrowserString(browserInfo).getDeltaTime();
    }

    public void setDuid(long duid) {
        this.duid = duid;
    }

    public long getDuid() {
        return duid;
    }

    public long getCodeVersion() {
        return codeVersion;
    }

    public void setCodeVersion(long codeVersion) {
        this.codeVersion = codeVersion;
    }

    public String getCodeFeatures() {
        return codeFeatures;
    }

    public void setCodeFeatures(String codeFeatures) {
        this.codeFeatures = codeFeatures;
    }
}
