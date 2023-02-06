package ru.yandex.autotests.morda.rules.proxy.actions;

import net.lightbody.bmp.core.har.Har;
import net.lightbody.bmp.proxy.ProxyServer;
import net.lightbody.bmp.proxy.http.BrowserMobHttpRequest;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.ProxyAction;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Predicate;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24/08/15
 */
public class RequestValidationAction implements ProxyAction {
    private ProxyServer proxyServer;
    private List<RequestValidation> validations;

    private RequestValidationAction(List<RequestValidation> validations) {
        this.validations = new ArrayList<>();
        this.validations.addAll(validations);
    }

    private RequestValidationAction(RequestValidation... validations) {
        this(asList(validations));
    }

    public static RequestValidationAction requestValidationAction(RequestValidation... validations) {
        return new RequestValidationAction(validations);
    }

    public static RequestValidationAction requestValidationAction(List<RequestValidation> validations) {
        return new RequestValidationAction(validations);
    }

    @Override
    public boolean isNeeded() {
        return true;
    }

    public void add(RequestValidation... validations) {
        add(asList(validations));
    }

    public void add(List<RequestValidation> validations) {
        this.validations.addAll(validations);
        if (proxyServer != null) {
            validations.forEach(this::addRequestValidation);
        }
    }

    private void addRequestValidation(RequestValidation validation) {
        proxyServer.addRequestInterceptor((BrowserMobHttpRequest request, Har har) -> {
            if (validation.requestFilter.test(request)) {
                validation.requestsFiltered++;
                validation.requestValidator.accept(request);
            }
        });
    }

    @Override
    public void perform(ProxyServer proxyServer) {
        this.proxyServer = proxyServer;
        validations.forEach(this::addRequestValidation);
    }

    public static class RequestValidation {
        private int requestsFiltered;
        private Predicate<BrowserMobHttpRequest> requestFilter;
        private Consumer<BrowserMobHttpRequest> requestValidator;

        public RequestValidation(Predicate<BrowserMobHttpRequest> requestFilter,
                                 Consumer<BrowserMobHttpRequest> requestValidator) {
            this.requestsFiltered = 0;
            this.requestFilter = requestFilter;
            this.requestValidator = requestValidator;
        }

        public static RequestValidation request(Predicate<BrowserMobHttpRequest> requestFilter,
                                                Consumer<BrowserMobHttpRequest> requestValidator) {
            return new RequestValidation(requestFilter, requestValidator);
        }

        public Predicate<BrowserMobHttpRequest> getRequestFilter() {
            return requestFilter;
        }

        public void setRequestFilter(Predicate<BrowserMobHttpRequest> requestFilter) {
            this.requestFilter = requestFilter;
        }

        public Consumer<BrowserMobHttpRequest> getRequestValidator() {
            return requestValidator;
        }

        public void setRequestValidator(Consumer<BrowserMobHttpRequest> requestValidator) {
            this.requestValidator = requestValidator;
        }

        public int getRequestsFiltered() {
            return requestsFiltered;
        }

        public void setRequestsFiltered(int requestsFiltered) {
            this.requestsFiltered = requestsFiltered;
        }
    }
}
