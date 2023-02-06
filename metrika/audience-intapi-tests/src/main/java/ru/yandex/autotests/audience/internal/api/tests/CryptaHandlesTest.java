package ru.yandex.autotests.audience.internal.api.tests;

import org.apache.commons.csv.CSVRecord;
import org.junit.Test;
import ru.yandex.autotests.audience.internal.api.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.audience.internal.api.IntapiFeatures.CRYPTA;
import static ru.yandex.autotests.audience.internal.api.errors.IntapiError.INVALID_ID;
import static ru.yandex.autotests.audience.internal.api.errors.IntapiError.WRONG_SEGMENT_TYPE;
import static ru.yandex.autotests.audience.internal.api.parameters.CryptaParameters.segmentUid;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.COMPOSITION_SEGMENT_ID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.UPLOADING_SEGMENT_ID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.CRYPTA_SEGMENT_ID;
import static ru.yandex.autotests.audience.internal.api.tests.IntapiTestData.NON_EXISTING_SEGMENT_ID;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 * Created by apuzikov on 12.07.17.
 */
@Features(CRYPTA)
@Title("Проверка ручки для крипты")
public class CryptaHandlesTest {
    public final UserSteps user = new UserSteps();

    @Test
    @Title("Тест ручки /crypta/users")
    public void getUsersTest() {
        List<CSVRecord> users = user.onCryptaSteps().getUsers(segmentUid(CRYPTA_SEGMENT_ID));
        assertThat("получен не пустой список", users, iterableWithSize(greaterThan(0)));
    }

    @Test
    @Title("Тест ручки /crypta/users негативный. Не существующий segment_id")
    public void getUsersNegativeTest() {
        user.onCryptaSteps()
                .getUsersAndExpectError(INVALID_ID, segmentUid(NON_EXISTING_SEGMENT_ID));
    }

    @Test
    @Title("Тест ручки /crypta/crypta_segment_data")
    public void getOriginalDataTest() {
        List<CSVRecord> originalData = user.onCryptaSteps().getCryptaSegmentData(segmentUid(UPLOADING_SEGMENT_ID));
        assertThat("получен не пустой список", originalData, iterableWithSize(greaterThan(0)));
    }

    @Test
    @Title("Тест ручки /crypta/crypta_segment_data негативный. Не существующий segment_id")
    public void getOriginalDataNegativeTest() {
        user.onCryptaSteps()
                .getCryptaSegmentDataAndExpectError(INVALID_ID, segmentUid(NON_EXISTING_SEGMENT_ID));
    }

    @Test
    @Title("Тест ручки /crypta/crypta_segment_data негативный. Поставить segment_id сегмента типа composition")
    public void getOriginalDataByPuttingDmpSegmentIdNegativeTest() {
        user.onCryptaSteps()
                .getCryptaSegmentDataAndExpectError(WRONG_SEGMENT_TYPE, segmentUid(COMPOSITION_SEGMENT_ID));
    }

    @Test
    @Title("Тест ручки /crypta/uploading_segment_data")
    public void getUploadingSegmentData() {
        List<CSVRecord> uploadingSegmentData = user.onCryptaSteps().getUploadingSegmentData(segmentUid(UPLOADING_SEGMENT_ID));
        assertThat("получен не пустой список", uploadingSegmentData, iterableWithSize(greaterThan(0)));
    }

    @Test
    @Title("Тест ручки /crypta/uploading_segment_data негативный. Не существующий segment_id")
    public void getUploadingSegmentDataNegativeTest() {
        user.onCryptaSteps()
                .getCryptaSegmentDataAndExpectError(INVALID_ID, segmentUid(NON_EXISTING_SEGMENT_ID));
    }

    @Test
    @Title("Тест ручки /crypta/uploading_segment_data негативный. Поставить segment_id сегмента типа composition")
    public void getUploadingSegmentDataByPuttingCompositionSegmentIdNegativeTest() {
        user.onCryptaSteps()
                .getUploadingSegmentDataAndExpectError(WRONG_SEGMENT_TYPE, segmentUid(COMPOSITION_SEGMENT_ID));
    }
}
