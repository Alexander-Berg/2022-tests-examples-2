package ru.yandex.metrika.cdp.api.tests.medium.deleted;

import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import ru.yandex.metrika.cdp.frontend.CdpPublicApiV1RestController;
import ru.yandex.metrika.cdp.frontend.constructor.params.CdpConstructorParams;
import ru.yandex.metrika.spring.params.DeletedUtils;
import ru.yandex.metrika.spring.params.NotDeleted;
import ru.yandex.metrika.spring.response.CommonApiResponse;
import ru.yandex.metrika.spring.response.ResponseWrapper;
import ru.yandex.metrika.spring.response.SuccessResponse;

@CdpPublicApiV1RestController
public class CdpApiDeletedCounterTestController {

    @RequestMapping(value = "/test/counter/{counterId}/noop", method = RequestMethod.GET)
    @NotDeleted(DeletedUtils.COUNTER)
    public ResponseWrapper<SuccessResponse> view(@PathVariable int counterId) {
        return CommonApiResponse.build(SuccessResponse.SUCCESS);
    }

    @RequestMapping(value = "/test/stat/noop", method = RequestMethod.GET)
    @NotDeleted(DeletedUtils.COUNTER_STAT)
    public ResponseWrapper<SuccessResponse> view(CdpConstructorParams params) {
        return CommonApiResponse.build(SuccessResponse.SUCCESS);
    }
}
