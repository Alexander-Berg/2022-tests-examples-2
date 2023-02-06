package helpers

import (
	"io/ioutil"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
)

func THttpResponseParser(pathToFile string) (*protoanswers.THttpResponse, error) {
	content, err := ioutil.ReadFile(pathToFile)
	if err != nil {
		return nil, err
	}

	return &protoanswers.THttpResponse{
		Content: content,
	}, nil
}
