package ru.yandex.metrika.mobmet.controller;

import java.util.List;

import javax.validation.Valid;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import ru.yandex.metrika.api.ObjectNotFoundException;
import ru.yandex.metrika.api.error.ConflictApiException;
import ru.yandex.metrika.auth.MetrikaUserDetails;
import ru.yandex.metrika.mobmet.dao.TestDevicesDao;
import ru.yandex.metrika.mobmet.model.TestDevice;
import ru.yandex.metrika.mobmet.model.TestDevicePurpose;
import ru.yandex.metrika.mobmet.model.TestDeviceType;
import ru.yandex.metrika.spring.TranslationHelper;
import ru.yandex.metrika.spring.auth.TargetUser;
import ru.yandex.metrika.spring.params.DeletedUtils;
import ru.yandex.metrika.spring.params.NotDeleted;
import ru.yandex.metrika.spring.quota.ApiType;
import ru.yandex.metrika.spring.quota.QuotaRule;
import ru.yandex.metrika.spring.response.CommonApiResponse;
import ru.yandex.metrika.spring.response.ResponseWrapper;
import ru.yandex.metrika.spring.response.SuccessResponse;

/**
 * Created by dlepex on 27.11.15.
 */
@Controller
public class TestDevicesController {

    private final TestDevicesDao testDevicesDao;
    private final TranslationHelper translationHelper;

    @Autowired
    public TestDevicesController(TestDevicesDao testDevicesDao, TranslationHelper translationHelper) {
        this.testDevicesDao = testDevicesDao;
        this.translationHelper = translationHelper;
    }

    @PreAuthorize("@appRbac.view(principal, #appId) or " +
            "@appRbac.agencyView(principal, #targetUser.getUid(), #appId)")
    @RequestMapping(value = "/management/v1/application/{apiKey}/testdevices", method = RequestMethod.GET)
    @QuotaRule(ApiType.client_read)
    @ResponseBody
    @NotDeleted(DeletedUtils.APPLICATION)
    public ResponseWrapper<DevicesResponse> getTestDevicesList(
            @TargetUser MetrikaUserDetails targetUser,
            @PathVariable("apiKey") int appId,
            @RequestParam(required = false) TestDevicePurpose purpose) {
        final List<TestDevice> devices = (purpose == null) ?
                testDevicesDao.selectAll(appId) : testDevicesDao.select(appId, purpose);
        return CommonApiResponse.build(new DevicesResponse(devices));
    }

    @PreAuthorize("@appRbac.save(principal, #appId) or " +
            "@appRbac.agencyEdit(principal, #targetUser.getUid(), #appId)")
    @RequestMapping(value = "/management/v1/application/{appId}/testdevices", method = RequestMethod.POST)
    @QuotaRule(ApiType.client_write)
    @ResponseBody
    @NotDeleted(DeletedUtils.APPLICATION)
    public ResponseWrapper<DeviceWrapper> createOrUpdateTestDevice(
            @PathVariable int appId,
            @RequestBody @Valid DeviceWrapper wrapper,
            @TargetUser MetrikaUserDetails targetUser) {
        final TestDevice device = wrapper.getDevice();
        device.setUid(targetUser.getUid());
        device.setApplicationId(appId);
        if (device.getPurpose() != TestDevicePurpose.push_notifications &&
                (device.getType() == TestDeviceType.huawei_oaid ||
                        device.getType() == TestDeviceType.ios_ifv ||
                        device.getType() == TestDeviceType.appmetrica_device_id)) {
            String localizedMessage = translationHelper.localizeMessage(
                    "%s может быть использован только для тестирования push-уведомлений");
            throw new ConflictApiException(String.format(localizedMessage, device.getType().getPublicName()));
        }
        if (device.getId() == null) {
            device.setId(testDevicesDao.insert(device));
        } else {
            boolean updated = testDevicesDao.update(device);
            if (!updated) {
                throw new ObjectNotFoundException(device.getId());
            }
        }

        return CommonApiResponse.build(new DeviceWrapper(device));
    }

    @PreAuthorize("@appRbac.save(principal, #appId) or @appRbac.agencyEdit(principal, #targetUser.getUid(), #appId)")
    @RequestMapping(value = "/management/v1/application/{appId}/testdevices/{deviceId}", method = RequestMethod.DELETE)
    @QuotaRule(ApiType.client_write)
    @ResponseBody
    @NotDeleted(DeletedUtils.APPLICATION)
    public ResponseWrapper<SuccessResponse> deleteTestDevice(
            @TargetUser MetrikaUserDetails targetUser,
            @PathVariable int appId,
            @PathVariable long deviceId) {
        if (!testDevicesDao.delete(deviceId)) {
            throw new ObjectNotFoundException();
        }

        return CommonApiResponse.build(SuccessResponse.SUCCESS);
    }

    public static class DeviceWrapper {

        @Valid
        private TestDevice device;

        @SuppressWarnings("unused")
        public DeviceWrapper() {
        }

        public DeviceWrapper(TestDevice device) {
            this.device = device;
        }

        public TestDevice getDevice() {
            return device;
        }

        public void setDevice(TestDevice device) {
            this.device = device;
        }
    }

    public static class DevicesResponse {

        private final List<TestDevice> devices;

        public DevicesResponse(List<TestDevice> devices) {
            this.devices = devices;
        }

        public List<TestDevice> getDevices() {
            return devices;
        }
    }
}
