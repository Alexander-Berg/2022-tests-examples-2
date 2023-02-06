package server

import (
	"context"
	"io"
	"io/ioutil"

	"a.yandex-team.ru/security/yadi/yadi/pkg/analyze"
)

func (s *Server) DoOko(ctx context.Context, body io.Reader) (analyze.IssueList, error) {
	data, err := ioutil.ReadAll(body)
	if err != nil {
		return nil, err
	}

	return s.doOko(ctx, data)
}
