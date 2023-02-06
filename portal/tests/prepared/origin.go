package prepared

import protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"

var (
	TestHTTPRequestVer1 = &protoanswers.THttpRequest{
		Method:  protoanswers.THttpRequest_Get,
		Scheme:  protoanswers.THttpRequest_Https,
		Path:    "/test",
		Headers: []*protoanswers.THeader{{Name: "test", Value: "ooo"}, {Name: "cookie", Value: "some=cookie;"}},
		Content: []byte(`smth that can not affect tests`),
	}
)
