package ru.yandex.metrika.mobmet.model;

import javax.validation.constraints.NotNull;

import com.fasterxml.jackson.annotation.JsonRootName;
import org.hibernate.validator.constraints.NotBlank;

import ru.yandex.metrika.spring.params.MysqlUtf8Charset;

import static ru.yandex.metrika.mobmet.model.TestDevicePurpose.reattribution;

/**
 * Created by dlepex on 27.11.15.
 */
@JsonRootName("device")
public class TestDevice {

    private Long id;

    private Long uid;

    @MysqlUtf8Charset
    @NotBlank
    private String deviceId;

    private int applicationId;

    @MysqlUtf8Charset
    @NotBlank
    private String name;

    @NotNull
    private TestDeviceType type;

    /**
     * Назначение тестового устройства.
     */
    @NotNull
    private TestDevicePurpose purpose = reattribution;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getUid() {
        return uid;
    }

    public void setUid(Long uid) {
        this.uid = uid;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public int getApplicationId() {
        return applicationId;
    }

    public void setApplicationId(int applicationId) {
        this.applicationId = applicationId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public TestDeviceType getType() {
        return type;
    }

    public void setType(TestDeviceType type) {
        this.type = type;
    }

    public TestDevicePurpose getPurpose() {
        return purpose;
    }

    public void setPurpose(TestDevicePurpose purpose) {
        this.purpose = purpose;
    }
}
