package ru.yandex.taxi.ququmber;

import java.io.IOException;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

@Component
public class CheckoutDeepCopyUtil {

    private final ObjectMapper checkouterAnnotationObjectMapper;

    @Autowired
    public CheckoutDeepCopyUtil(
            @Qualifier("checkouterAnnotationObjectMapper") ObjectMapper checkouterAnnotationObjectMapper
    ) {
        this.checkouterAnnotationObjectMapper = checkouterAnnotationObjectMapper;
    }

    public <T> T deepCopy(T object) {
        return deepCopy(object, (Class<T>) object.getClass());
    }

    public <T> T deepCopy(T object, Class<T> class_) {
        try {
            byte[] bytes = checkouterAnnotationObjectMapper.writeValueAsBytes(object);
            return checkouterAnnotationObjectMapper.readValue(bytes, class_);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
