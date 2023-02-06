package gortrpc

import (
	"encoding/json"
	"io"
	"net/rpc"
	"strings"
	"testing"

	"github.com/valyala/fastjson"
)

func Test_clientResponse_UnmarshalJSON(t *testing.T) {
	type fields struct {
		Version     string
		ID          *uint64
		Result      *json.RawMessage
		Error       *Error
		XRealServer string
	}
	type args struct {
		raw []byte
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr bool
	}{
		{
			name: "sshresult",
			fields: fields{
				Version:     "2.0",
				ID:          &[]uint64{0}[0],
				Result:      &[]json.RawMessage{json.RawMessage(`{"result":true,"session_id":2000863405}`)}[0],
				Error:       nil,
				XRealServer: "man1-rt1.yndx.net",
			},
			args:    args{[]byte(`{"id":0,"jsonrpc":"2.0","result":{"result":true,"session_id":2000863405},"XRealServer":"man1-rt1.yndx.net"}`)},
			wantErr: false,
		},
		{
			name: "string id",
			fields: fields{
				Version:     "2.0",
				ID:          &[]uint64{2}[0],
				Result:      &[]json.RawMessage{json.RawMessage(`{"result":true,"session_id":2000863405}`)}[0],
				Error:       nil,
				XRealServer: "man1-rt1.yndx.net",
			},
			args:    args{[]byte(`{"id":"2","jsonrpc":"2.0","result":{"result":true,"session_id":2000863405},"XRealServer":"man1-rt1.yndx.net"}`)},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &clientResponse{
				Version:     tt.fields.Version,
				ID:          tt.fields.ID,
				Result:      tt.fields.Result,
				Error:       tt.fields.Error,
				XRealServer: tt.fields.XRealServer,
			}
			if err := r.UnmarshalJSON(tt.args.raw); (err != nil) != tt.wantErr {
				t.Errorf("UnmarshalJSON() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func Test_clientCodec_ReadResponseHeader(t *testing.T) {
	type fields struct {
		jparser fastjson.Parser
		dec     *json.Decoder
		enc     *json.Encoder
		ua      string
		c       io.ReadWriteCloser
		resp    clientResponse
		pending map[uint64]string
	}
	type args struct {
		r *rpc.Response
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr bool
	}{
		{
			name: "id hack NOCDEV-3901",
			fields: fields{
				dec: json.NewDecoder(strings.NewReader(`{"id":"1","jsonrpc":"2.0","result":{"result":true,"session_id":2000863405},"XRealServer":"man1-rt1.yndx.net"}`)),
				enc: nil,
				ua:  "gortrpc",
				c:   nil,
				resp: clientResponse{
					Version:     "2.0",
					ID:          &[]uint64{2}[0],
					Result:      &[]json.RawMessage{json.RawMessage(`{"result":true,"session_id":2000863405}`)}[0],
					Error:       nil,
					XRealServer: "man1-rt1.yndx.net",
				},
				pending: map[uint64]string{
					2: "try_pubkey_auth",
				},
			},
			args: args{
				r: &[]rpc.Response{
					{},
				}[0],
			},
			wantErr: false,
		},
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &clientCodec{
				jparser: tt.fields.jparser,
				dec:     tt.fields.dec,
				enc:     tt.fields.enc,
				ua:      tt.fields.ua,
				c:       tt.fields.c,
				pending: tt.fields.pending,
			}
			if err := c.ReadResponseHeader(tt.args.r); (err != nil) != tt.wantErr {
				t.Errorf("ReadResponseHeader() error = %v, wantErr %v", err, tt.wantErr)
			}
			if *c.resp.ID != *tt.fields.resp.ID {
				t.Errorf("ReadResponseHeader() id mismatch got %v, want %v", *c.resp.ID, *tt.fields.resp.ID)
			}
		})
	}
}
