package ru.yandex.metrika.mobmet.push.common.service.crud;

import java.util.List;
import java.util.stream.Collectors;

import ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaign;
import ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignMessage;
import ru.yandex.metrika.mobmet.push.common.campaigns.model.TestPushStatus;
import ru.yandex.metrika.mobmet.push.common.campaigns.validation.ValidationError;
import ru.yandex.metrika.mobmet.push.common.service.crud.validators.PushMessageValidator;

/**
 * Валидировать сообщение перед тем, как мы туда отправим тестовый пуш
 * <p>
 * Created by graev on 06/10/16.
 */
public final class TestPushValidationFacade {
    private List<PushMessageValidator> messageValidators;

    public TestPushStatus validate(PushCampaign campaign, PushCampaignMessage message) {
        final List<ValidationError> errors = messageValidators.stream()
                .flatMap(v -> v.validate(campaign, message).stream())
                .collect(Collectors.toList());

        if (errors.isEmpty()) {
            return TestPushStatus.ok();
        } else {
            return TestPushStatus.notOk(errors);
        }
    }

    public void setMessageValidators(List<PushMessageValidator> messageValidators) {
        this.messageValidators = messageValidators;
    }
}
