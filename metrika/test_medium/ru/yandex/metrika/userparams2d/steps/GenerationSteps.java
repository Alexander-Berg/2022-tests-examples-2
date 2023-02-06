package ru.yandex.metrika.userparams2d.steps;

import java.util.List;
import java.util.Random;
import java.util.stream.IntStream;

import org.springframework.stereotype.Component;

import ru.yandex.metrika.api.management.client.external.userparams.UserParamAction;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.userparams.ListParamWrapper;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwnerKey;
import ru.yandex.qatools.allure.annotations.Step;

import static java.util.stream.Collectors.toList;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomString;
import static ru.yandex.metrika.common.test.medium.RandomUtils.getRandomUInt32;

@Component
public class GenerationSteps {
    private static final int RANDOM_STRING_LENGTH = 7;

    private static final Random random = new Random(0);

    private String generatePath(int length) {
        var path = IntStream.range(0, length)
                .mapToObj(i -> getRandomString(random, RANDOM_STRING_LENGTH))
                .collect(toList());
        return String.join(".", path);
    }

    private String generateRandomLengthPath() {
        int length = (int) (getRandomUInt32(random) % 9 + 1);
        return generatePath(length);
    }

    @Step("Сгенерировать апдейт, содержащий параметры пользователей")
    public UserParamUpdate generateUpdateWithParams(List<Param> params) {
        return new UserParamUpdate(params, UserParamAction.UPDATE);
    }

    @Step("Сгенерировать апдейт удаляющий параметры пользователей")
    public UserParamUpdate generateDeletingUpdateWithParams(List<Param> params) {
        return new UserParamUpdate(params, UserParamAction.DELETE_KEYS);
    }

    @Step("Сгенеровать апдейт с clientUserId")
    public UserParamUpdate generateUpdateWithClientUserId(List<Param> params, int counterId, long userId, String clientUserId) {
        return new UserParamUpdate(
                new ListParamWrapper(params, userId, counterId, clientUserId),
                UserParamAction.UPDATE
        );
    }

    @Step("Сгенерировать строковый параметр пользователя")
    public Param generateStringParameter() {
        return new ParamBuilder()
                .withPath(generateRandomLengthPath())
                .withValueString(getRandomString(random, RANDOM_STRING_LENGTH))
                .build();
    }

    @Step("Сгенерировать числовой параметр пользователя")
    public Param generateDoubleParameter() {
        double value = random.nextDouble();
        return new ParamBuilder()
                .withPath(generateRandomLengthPath())
                .withValueDouble(value)
                .withValueString(Double.toString(value))
                .build();
    }

    @Step("Сгенерировать максимально допустимый параметр пользователя")
    public Param generateFullStringParameter() {
        return new ParamBuilder()
                .withPath(generatePath(9))
                .withValueString(getRandomString(random, RANDOM_STRING_LENGTH))
                .build();
    }

    @Step("Сгенерировать максимально допустимый числовой параметр пользователя")
    public Param generateFullDoubleParameter() {
        double value = random.nextDouble();
        return new ParamBuilder()
                .withPath(generatePath(9))
                .withValueDouble(value)
                .withValueString(Double.toString(value))
                .build();
    }

    @Step("Сгенерировать параметр пользователя, содержащий UserID")
    public Param generateUserIdParameter() {
        return new ParamBuilder()
                .withPath("userID")
                .withValueString(getRandomString(random, RANDOM_STRING_LENGTH))
                .build();
    }

    @Step("Обновить строковые значения параметров пользователя")
    public List<Param> updateParamsStringValues(List<Param> originalParams) {
        return originalParams.stream()
                .map(param -> {
                    double value = random.nextDouble();
                    return new ParamBuilder()
                            .fromParam(param)
                            .withValueDouble(value)
                            .withValueString(Double.toString(value))
                            .build();

                })
                .collect(toList());
    }

    @Step("Обновить числовые значения параметров пользователя")
    public List<Param> updateParamsDoubleValues(List<Param> originalParams) {
        return originalParams.stream()
                .map(param -> new ParamBuilder()
                        .fromParam(param)
                        .withValueString(getRandomString(random, RANDOM_STRING_LENGTH))
                        .build())
                .collect(toList());
    }

    @Step("Обновить ключи параметров пользователя")
    public List<Param> updateParamsKeys(List<Param> originalParams) {
        return originalParams.stream()
                .map(param -> new Param(
                        param.getOwnerKey(),
                        getRandomString(random, RANDOM_STRING_LENGTH),
                        param.getValueString(),
                        param.getValueDouble()))
                .collect(toList());
    }

    @Step("Сгенерировать параметр с таким же владельцем")
    public Param generateParamWithSameOwner(Param param) {
        return new ParamBuilder()
                .fromParam(generateStringParameter())
                .withCounterId(param.getOwnerKey().getCounterId())
                .withUserId(param.getOwnerKey().getUserId())
                .build();
    }


    @Step("Сгенерировать параметр пользователя для большого счетчика")
    public Param generateParamWithBigCounter(int bigCounterId) {
        return new ParamBuilder()
                .fromParam(generateStringParameter())
                .withCounterId(bigCounterId)
                .build();
    }

    @Step("Сгенерировать параметры пользователей для большого счетчика")
    public List<Param> generateParamsWithBigCounter(int count) {
        int bigCounterId = TestCountersProvider.getRandomBigCounter();
        return IntStream.range(0, count)
                .mapToObj(i -> generateParamWithBigCounter(bigCounterId))
                .collect(toList());
    }


    @Step("Сгенерировать параметр пользователя для небольшого счетчика")
    public Param generateParamForNanoCounter(int nanoCounterId) {
        return new ParamBuilder()
                .fromParam(generateStringParameter())
                .withCounterId(nanoCounterId)
                .build();
    }

    @Step("Сгенерировать параметры пользователей для небольшого счетчика")
    public List<Param> generateParamsWithNanoCounter(int count) {
        int nanoCounterId = TestCountersProvider.getRandomSmallCounter();
        return IntStream.range(0, count)
                .mapToObj(i -> generateParamForNanoCounter(nanoCounterId))
                .collect(toList());
    }

    private static class ParamBuilder {
        private int counterId = 1;
        private long userId = 1L;
        private String path;
        private String valueString;
        private Double valueDouble = 0.;
        private Long version = 1L;

        public ParamBuilder fromParam(Param param) {
            this.counterId = param.getOwnerKey().getCounterId();
            this.userId = param.getOwnerKey().getUserId();
            this.path = param.getPath();
            this.valueString = param.getValueString();
            this.valueDouble = param.getValueDouble();
            this.version = param.getVersion();
            return this;
        }

        public ParamBuilder withCounterId(int counterId) {
            this.counterId = counterId;
            return this;
        }

        public ParamBuilder withUserId(long userId) {
            this.userId = userId;
            return this;
        }

        public ParamBuilder withPath(String path) {
            this.path = path;
            return this;
        }

        public ParamBuilder withValueString(String valueString) {
            this.valueString = valueString;
            return this;
        }

        public ParamBuilder withValueDouble(double valueDouble) {
            this.valueDouble = valueDouble;
            return this;
        }

        public ParamBuilder withVersion(long version) {
            this.version = version;
            return this;
        }

        public Param build() {
            return new Param(new ParamOwnerKey(counterId, userId), path, valueString, valueDouble, version);
        }
    }

}
