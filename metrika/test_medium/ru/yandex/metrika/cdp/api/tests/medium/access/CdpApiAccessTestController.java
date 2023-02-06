package ru.yandex.metrika.cdp.api.tests.medium.access;

import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import ru.yandex.metrika.cdp.api.common.annotations.CdpPublicApiSaveAccess;
import ru.yandex.metrika.cdp.api.common.annotations.CdpPublicApiViewAccess;
import ru.yandex.metrika.cdp.frontend.CdpPublicApiV1RestController;
import ru.yandex.metrika.spring.response.CommonApiResponse;
import ru.yandex.metrika.spring.response.ResponseWrapper;
import ru.yandex.metrika.spring.response.SuccessResponse;

@CdpPublicApiV1RestController
public class CdpApiAccessTestController {

    @RequestMapping(value = "/test/counter/{counterId}/access/view", method = RequestMethod.GET)
    @CdpPublicApiViewAccess
    public ResponseWrapper<SuccessResponse> view(@PathVariable int counterId) {
        return CommonApiResponse.build(SuccessResponse.SUCCESS);
    }

    @RequestMapping(value = "/test/counter/{counterId}/access/save", method = RequestMethod.GET)
    @CdpPublicApiSaveAccess
    public ResponseWrapper<SuccessResponse> save(@PathVariable int counterId) {
        return CommonApiResponse.build(SuccessResponse.SUCCESS);
    }

}
