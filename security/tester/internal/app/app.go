package app

import (
	"bytes"
	"context"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"net"
	"strings"
	"sync"
	"time"

	"golang.org/x/crypto/ssh"
	"golang.org/x/crypto/ssh/agent"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/nop"
	"a.yandex-team.ru/security/skotty/tester/internal/hostkey"
	"a.yandex-team.ru/security/skotty/tester/internal/krl"
	"a.yandex-team.ru/security/skotty/tester/internal/staff"
)

type App struct {
	l        log.Logger
	listener net.Listener
	krl      *krl.KRL
	staffc   *staff.Client
	sshConf  ssh.ServerConfig
	done     chan struct{}
	keys     map[string][]ssh.PublicKey
	keysMu   sync.Mutex
}

type ClientInfo struct {
	Username           string
	AuthKeys           []ssh.PublicKey
	AgentKeys          []ssh.PublicKey
	AgentForwarded     bool
	SudoAvailable      bool
	HaveTerm           bool
	StaffKeys          []string
	StaffkeysErr       error
	ClientVersion      string
	ClientCompatNotice string
	mu                 sync.Mutex
}

func NewApp(opts ...Option) *App {
	app := &App{
		l:    &nop.Logger{},
		done: make(chan struct{}),
		keys: make(map[string][]ssh.PublicKey),
	}

	for _, opt := range opts {
		opt(app)
	}

	var err error
	app.krl, err = krl.NewKRL(app.l)
	if err != nil {
		panic("can't create KRL reader: " + err.Error())
	}

	app.sshConf = ssh.ServerConfig{
		MaxAuthTries:  -1,
		ServerVersion: "SSH-2.0-SkottyTester",
		KeyboardInteractiveCallback: func(c ssh.ConnMetadata, _ ssh.KeyboardInteractiveChallenge) (*ssh.Permissions, error) {
			if isSignSession(c) {
				return nil, errors.New("keyboard auth is prohibited for sign check")
			}

			return nil, nil
		},
		PublicKeyCallback: app.publicKeyCallback,
	}

	for _, key := range hostkey.PrivateKeys {
		app.sshConf.AddHostKey(key)
	}

	return app
}

func (a *App) ListenAndServe(addr string) error {
	defer close(a.done)

	listener, err := net.Listen("tcp6", addr)
	if err != nil {
		return fmt.Errorf("failed to listen: %w", err)
	}

	a.listener = listener
	a.l.Info("listening", log.String("addr", addr))
	for {
		tcpConn, err := listener.Accept()
		if err != nil {
			if errors.Is(err, net.ErrClosed) {
				return nil
			}

			a.l.Warn("failed to accept incoming connection", log.Error(err))
			continue
		}

		sshConn, chans, reqs, err := ssh.NewServerConn(tcpConn, &a.sshConf)
		if err != nil {
			switch {
			case errors.Is(err, io.EOF):
			case strings.Contains(strings.ToLower(err.Error()), "connection reset by peer"):
			default:
				a.l.Error("failed to handshake", log.Error(err))
			}
			continue
		}

		sessID := newSessID(sshConn.SessionID())
		a.l.Info("new SSH connection",
			log.String("remote_addr", sshConn.RemoteAddr().String()),
			log.String("version", string(sshConn.ClientVersion())),
			log.String("session_id", sessID))

		a.keysMu.Lock()
		authKeys := a.keys[sessID]
		delete(a.keys, sessID)
		a.keysMu.Unlock()

		// Discard all global out-of-band Requests
		go ssh.DiscardRequests(reqs)
		// Accept all channels
		go a.handleChannels(sessID, authKeys, sshConn, chans)
	}
}

func (a *App) Shutdown(ctx context.Context) {
	_ = a.listener.Close()
	a.krl.Shutdown(ctx)

	select {
	case <-ctx.Done():
	case <-a.done:
	}
}

func (a *App) publicKeyCallback(c ssh.ConnMetadata, key ssh.PublicKey) (*ssh.Permissions, error) {
	a.keysMu.Lock()
	defer a.keysMu.Unlock()

	sessID := newSessID(c.SessionID())
	if !isSignSession(c) {
		a.keys[sessID] = append(a.keys[sessID], key)
		return nil, errors.New("try one more time")
	}

	expectedHash := c.User()
	hashFn := sha256Fingerprint
	if strings.HasPrefix(expectedHash, "MD5") {
		hashFn = md5Fingerprint
	}

	if hashFn(key) != c.User() {
		return nil, fmt.Errorf("unexpected key: %s (actual) != %s (expected)", hashFn(key), c.User())
	}

	a.keys[sessID] = append(a.keys[sessID], key)
	return &ssh.Permissions{}, nil
}

func (a *App) handleChannels(sessID string, authKeys []ssh.PublicKey, sshConn *ssh.ServerConn, chans <-chan ssh.NewChannel) {
	handleChannel := func(newChannel ssh.NewChannel) {
		if t := newChannel.ChannelType(); t != "session" {
			a.l.Info("rejected channel", log.String("channel_type", t), log.String("session_id", sessID))
			_ = newChannel.Reject(ssh.UnknownChannelType, fmt.Sprintf("unsupported channel type: %s", t))
			return
		}

		if err := a.handleChannel(sshConn, newChannel, authKeys); err != nil {
			a.l.Warn("failed to handle client channel", log.String("session_id", sessID), log.Error(err))
		}
	}

	for newChannel := range chans {
		go handleChannel(newChannel)

	}
}

func (a *App) handleChannel(sshConn *ssh.ServerConn, newChannel ssh.NewChannel, authKeys []ssh.PublicKey) error {
	connection, requests, err := newChannel.Accept()
	if err != nil {
		return fmt.Errorf("failed to accept channel: %w", err)
	}

	clVersion := strings.TrimPrefix(string(sshConn.ClientVersion()), "SSH-2.0-")
	cl := ClientInfo{
		Username:           sshConn.User(),
		AuthKeys:           authKeys,
		ClientVersion:      clVersion,
		ClientCompatNotice: clientCompatNotice(clVersion),
	}

	func() {
		if isSignSession(sshConn) {
			cl.StaffkeysErr = errors.New("n/a for sign session")
			return
		}

		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		keys, err := a.staffc.UserKeys(ctx, sshConn.User())
		if err != nil {
			cl.StaffkeysErr = err
			return
		}

		for _, key := range keys {
			cl.StaffKeys = append(cl.StaffKeys, key.Fingerprint)
		}
	}()

	handleShell := func(req *ssh.Request) error {
		defer func() { _ = connection.Close() }()

		if err := req.Reply(true, nil); err != nil {
			return err
		}

		out, err := a.renderClientInfo(&cl)
		if err != nil {
			_, _ = io.WriteString(connection.Stderr(), err.Error())
			return err
		}

		if cl.HaveTerm {
			_, err = connection.Write(bytes.ReplaceAll(out, []byte{'\n'}, []byte{'\r', '\n'}))
		} else {
			_, err = connection.Write(out)
		}

		if err != nil {
			return fmt.Errorf("failed to write response: %w", err)
		}

		return nil
	}

	handleSSHAgent := func(req *ssh.Request) error {
		authChan, _, err := sshConn.OpenChannel("auth-agent@openssh.com", nil)
		if err != nil {
			return fmt.Errorf("failed to open ssh-agent channel: %w", err)
		}
		defer func() { _ = authChan.Close() }()

		cl.mu.Lock()
		cl.AgentForwarded = true
		cl.mu.Unlock()

		clientAgent := agent.NewClient(authChan)
		agentKeys, err := clientAgent.List()
		if err != nil {
			return fmt.Errorf("failed to list agent keys: %w", err)
		}

		cl.mu.Lock()
		cl.AgentKeys = make([]ssh.PublicKey, len(agentKeys))
		for i, k := range agentKeys {
			cl.AgentKeys[i] = k
		}
		cl.mu.Unlock()

		_, err = clientAgent.Extension("skotty-sudo-check", nil)
		cl.mu.Lock()
		cl.SudoAvailable = err == nil
		cl.mu.Unlock()

		return req.Reply(true, nil)
	}

	for req := range requests {
		var err error
		switch req.Type {
		case "shell", "exec":
			err = handleShell(req)
		case "pty-req", "window-change":
			cl.mu.Lock()
			cl.HaveTerm = true
			cl.mu.Unlock()

			_ = req.Reply(true, nil)
		case "auth-agent-req@openssh.com":
			err = handleSSHAgent(req)
		case "env":
			// pass
		default:
			a.l.Info("unsupported req", log.String("req_type", req.Type))
		}

		if err != nil {
			a.l.Warn("failed to handle client request", log.String("req_type", req.Type), log.Error(err))
		}
	}

	return nil
}

func newSessID(sshSessionID []byte) string {
	return hex.EncodeToString(sshSessionID)
}

func isSignSession(meta ssh.ConnMetadata) bool {
	user := meta.User()
	return strings.HasPrefix(user, "MD5") || strings.HasPrefix(user, "SHA256")
}

func sha256Fingerprint(key ssh.PublicKey) string {
	if cert, ok := key.(*ssh.Certificate); ok {
		return ssh.FingerprintSHA256(cert.Key)
	}

	return ssh.FingerprintSHA256(key)
}

func md5Fingerprint(key ssh.PublicKey) string {
	if cert, ok := key.(*ssh.Certificate); ok {
		return ssh.FingerprintLegacyMD5(cert.Key)
	}

	return ssh.FingerprintLegacyMD5(key)
}
