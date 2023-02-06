package ru.yandex.metrika.common.test.medium;

import java.util.Random;

import org.springframework.stereotype.Component;

import static com.google.common.math.IntMath.pow;
import static java.lang.String.valueOf;
import static org.apache.commons.lang3.StringUtils.leftPad;
import static org.joda.time.DateTime.now;
import static org.joda.time.format.DateTimeFormat.forPattern;

@Component
public class RandomSteps {

    public Random random;

    public RandomSteps() {
        this.random = new Random(0L);
    }

    /**
     * @return имя чанка в формате 20180625143852_20180625145416_8180294795209850757_001
     */
    public String generateChunkName() {
        StringBuilder value = new StringBuilder();
        value.append(forPattern("yyyyMMddHHmmss").print(now()));
        value.append("_").append(forPattern("yyyyMMddHHmmss").print(now().plus(100)));
        value.append("_").append(leftPad(valueOf(random.nextInt(Integer.MAX_VALUE)), 19, "0"));
        value.append("_").append(leftPad(valueOf(random.nextInt(pow(10, 3))), 3, "0"));
        return value.toString();
    }

}
