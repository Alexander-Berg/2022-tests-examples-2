package ru.yandex.metrika.visor3d.steps;

public class Package {

    private PackageType type;
    private int stamp;
    private String data;

    private int partNum = 1;
    private boolean end = true;

    public Package withType(PackageType type) {
        this.type = type;
        return this;
    }

    public Package withStamp(int stamp) {
        this.stamp = stamp;
        return this;
    }


    public Package withData(String data) {
        this.data = data;
        return this;
    }

    public void setType(PackageType type) {
        this.type = type;
    }

    public void setStamp(int stamp) {
        this.stamp = stamp;
    }

    public void setData(String data) {
        this.data = data;
    }

    public PackageType getType() {
        return type;
    }

    public int getStamp() {
        return stamp;
    }

    public String getData() {
        return data;
    }

    public int getPartNum() {
        return partNum;
    }

    public void setPartNum(int partNum) {
        this.partNum = partNum;
    }

    public Package withPartNum(int partNum) {
        this.partNum = partNum;
        return this;
    }

    public boolean isEnd() {
        return end;
    }

    public void setEnd(boolean end) {
        this.end = end;
    }

    public Package withEnd(boolean end) {
        this.end = end;
        return this;
    }

}
