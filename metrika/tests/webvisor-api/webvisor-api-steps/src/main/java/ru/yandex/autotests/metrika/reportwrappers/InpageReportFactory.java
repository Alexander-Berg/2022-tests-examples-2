package ru.yandex.autotests.metrika.reportwrappers;

import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataClickGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataFormGETPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkMapGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataScrollGETSchema;
import ru.yandex.autotests.metrika.exceptions.MetrikaApiException;

/**
 * Created by sonick on 19.12.16.
 */
public class InpageReportFactory {

    public static InpageReport create(Object report) {
        if (report instanceof MapsV1DataLinkMapGETSchema) {
            return new InpageLinkDataReport((MapsV1DataLinkMapGETSchema) report);
        } else if (report instanceof MapsV1DataClickGETSchema) {
            return new InpageClickDataReport((MapsV1DataClickGETSchema) report);
        } else if (report instanceof MapsV1DataScrollGETSchema) {
            return new InpageScrollDataReport((MapsV1DataScrollGETSchema) report);
        } else if (report instanceof MapsV1DataFormGETPOSTSchema) {
            return new InpageFormDataReport((MapsV1DataFormGETPOSTSchema) report);
        }
        throw new MetrikaApiException("Не удалось создать обёртку для бина: неизвестный тип бина");
    }
}
