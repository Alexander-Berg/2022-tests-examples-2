package ck

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/noc/nalivkin/internal/resource"
)

func TestDeployPatch(t *testing.T) {
	var body []byte
	objectID := 666
	hostname := "hhhhhhhhh"
	expectedBody, _ := json.Marshal(map[string]interface{}{
		"patches": []map[string]interface{}{
			{
				"object_id":  objectID,
				"hostname":   hostname,
				"run_before": 0,
				"run_after":  0,
				"patch_id":   "",
				"patch_text": "xxxxxxxxxxx",
				"config_md5": "deadbeef",
			},
		},
		"files":    []map[string]interface{}{},
		"ticket":   "",
		"username": "",
	})
	patch := resource.Patch{
		Patches: []resource.PatchSingle{
			{
				PatchText: "xxxxxxxxxxx",
				ConfigMD5: "deadbeef",
			},
		},
	}
	ctx := context.Background()
	serv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		resp, _ := json.Marshal(map[string][]map[string]string{
			"result": {{
				"id": "calavaralera",
			}},
		})
		defer r.Body.Close()
		body, _ = io.ReadAll(r.Body)
		_, _ = w.Write(resp)
	}))
	ck := NewClient(serv.URL, &http.Client{}, &mockTvmClient{}, 0)
	_, err := ck.DeployPatch(ctx, objectID, patch, hostname)
	assert.NoError(t, err)
	assert.JSONEq(t, string(body), string(expectedBody))
}

type mockTvmClient struct{}

func (m *mockTvmClient) GetServiceTicketForAlias(ctx context.Context, alias string) (string, error) {
	return "", nil
}
func (m *mockTvmClient) GetServiceTicketForID(ctx context.Context, dstID tvm.ClientID) (string, error) {
	return "", nil
}
func (m *mockTvmClient) CheckServiceTicket(ctx context.Context, ticket string) (*tvm.CheckedServiceTicket, error) {
	return nil, nil
}
func (m *mockTvmClient) CheckUserTicket(ctx context.Context, ticket string, opts ...tvm.CheckUserTicketOption) (*tvm.CheckedUserTicket, error) {
	return nil, nil
}
func (m *mockTvmClient) GetRoles(ctx context.Context) (*tvm.Roles, error) {
	return nil, nil
}
func (m *mockTvmClient) GetStatus(ctx context.Context) (tvm.ClientStatusInfo, error) {
	return tvm.ClientStatusInfo{}, nil
}
