package helpers

import protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"

func WithScheme(scheme protoanswers.THttpRequest_EScheme) func(r *protoanswers.THttpRequest) {
	return func(r *protoanswers.THttpRequest) {
		r.Scheme = scheme
	}
}

func WithHeader(name, value string) func(r *protoanswers.THttpRequest) {
	return func(r *protoanswers.THttpRequest) {
		r.Headers = append(r.Headers, &protoanswers.THeader{
			Name:  name,
			Value: value,
		})
	}
}

func WithPath(path string) func(r *protoanswers.THttpRequest) {
	return func(r *protoanswers.THttpRequest) {
		r.Path = path
	}
}

func WithMethod(method protoanswers.THttpRequest_EMethod) func(r *protoanswers.THttpRequest) {
	return func(r *protoanswers.THttpRequest) {
		r.Method = method
	}
}

func NewTHttpRequest(opts ...func(r *protoanswers.THttpRequest)) *protoanswers.THttpRequest {
	req := &protoanswers.THttpRequest{
		Headers: []*protoanswers.THeader{},
	}
	for _, opt := range opts {
		opt(req)
	}
	return req
}
