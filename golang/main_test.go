package main

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func TestParseSimpleYAML(t *testing.T) {
	f, err := os.CreateTemp(t.TempDir(), "cfg-*.yaml")
	if err != nil {
		t.Fatal(err)
	}
	content := "api:\n  url: http://example.com\nmodel:\n  path: /tmp/model\nsystem_prompt: hello"
	if _, err := f.WriteString(content); err != nil {
		t.Fatal(err)
	}
	f.Close()

	cfg := parseSimpleYAML(f.Name())
	if cfg.API.URL != "http://example.com" {
		t.Fatalf("unexpected api url: %s", cfg.API.URL)
	}
	if cfg.Model.Path != "/tmp/model" {
		t.Fatalf("unexpected model path: %s", cfg.Model.Path)
	}
	if cfg.SystemPrompt != "hello" {
		t.Fatalf("unexpected system prompt: %s", cfg.SystemPrompt)
	}
}

func TestParseSimpleYAMLMissing(t *testing.T) {
	cfg := parseSimpleYAML("/no/file")
	if cfg.API.URL != "" || cfg.Model.Path != "" || cfg.SystemPrompt != "" {
		t.Fatalf("expected empty config")
	}
}

func TestLoadConfigs(t *testing.T) {
	dir := t.TempDir()
	yaml1 := filepath.Join(dir, "model1.yaml")
	os.WriteFile(yaml1, []byte("api:\n  url: http://one\nmodel:\n  path: /one"), 0644)
	yaml2 := filepath.Join(dir, "model2.yml")
	os.WriteFile(yaml2, []byte("api:\n  url: http://two\nmodel:\n  path: /two"), 0644)

	cfgs := loadConfigs(dir)
	if len(cfgs) != 2 {
		t.Fatalf("expected 2 configs, got %d", len(cfgs))
	}
	if cfgs["model1"].Model.Path != "/one" {
		t.Fatalf("wrong path: %s", cfgs["model1"].Model.Path)
	}
}

func TestLoadConfigsWithIgnoredFiles(t *testing.T) {
	dir := t.TempDir()
	os.Mkdir(filepath.Join(dir, "sub"), 0755)
	os.WriteFile(filepath.Join(dir, "skip.txt"), []byte("ignore"), 0644)
	os.WriteFile(filepath.Join(dir, "m.yaml"), []byte("api:\n  url: x\nmodel:\n  path: y"), 0644)
	cfgs := loadConfigs(dir)
	if len(cfgs) != 1 {
		t.Fatalf("expected 1 config, got %d", len(cfgs))
	}
}

func TestLoadConfigsMissingDir(t *testing.T) {
	cfgs := loadConfigs("/nonexistent")
	if len(cfgs) != 0 {
		t.Fatalf("expected 0 configs")
	}
}

func TestHealthHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rr := httptest.NewRecorder()
	healthHandler(rr, req)
	if rr.Code != http.StatusOK {
		t.Fatalf("status %d", rr.Code)
	}
	var data map[string]string
	json.Unmarshal(rr.Body.Bytes(), &data)
	if data["status"] != "ok" {
		t.Fatalf("unexpected body: %v", data)
	}
}

func TestModelsHandler(t *testing.T) {
	configs = map[string]ModelConfig{
		"a": {},
		"b": {},
	}
	req := httptest.NewRequest(http.MethodGet, "/v1/models", nil)
	rr := httptest.NewRecorder()
	modelsHandler(rr, req)
	if rr.Code != http.StatusOK {
		t.Fatalf("status %d", rr.Code)
	}
	var list ModelList
	json.Unmarshal(rr.Body.Bytes(), &list)
	if len(list.Data) != 2 {
		t.Fatalf("expected 2 models, got %d", len(list.Data))
	}
}

func TestRunAndMain(t *testing.T) {
	called := 0
	listenAndServe = func(addr string, h http.Handler) error {
		called++
		srv := &http.Server{Addr: "127.0.0.1:0", Handler: h}
		go srv.ListenAndServe()
		srv.Close()
		if called == 1 {
			return nil
		}
		return io.ErrUnexpectedEOF
	}
	defer func() { listenAndServe = http.ListenAndServe }()

	if err := run("127.0.0.1:0", t.TempDir()); err != nil {
		t.Fatalf("run returned error: %v", err)
	}

	// second call to exercise error path
	err := run("127.0.0.1:0", t.TempDir())
	if err == nil {
		t.Fatalf("expected error")
	}

	// main should call run and handle error via log.Fatal; replace runFn
	exitCalled := false
	runBackup := runFn
	runFn = func(a, b string) error { return io.ErrUnexpectedEOF }
	defer func() { runFn = runBackup }()

	// capture os.Exit via defer
	if pid := os.Getpid(); pid > 0 {
		// intercept log.Fatal by running main in a subprocess
		if os.Getenv("MAINTEST") == "1" {
			main()
			return
		}
		cmd := exec.Command(os.Args[0], "-test.run=TestRunAndMain")
		cmd.Env = append(os.Environ(), "MAINTEST=1")
		err := cmd.Run()
		if e, ok := err.(*exec.ExitError); ok && !e.Success() {
			exitCalled = true
		}
	}

	if !exitCalled {
		t.Fatalf("expected main to exit with failure")
	}
}

func TestChatCompletionHandler(t *testing.T) {
	upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		io.Copy(w, r.Body)
	}))
	defer upstream.Close()

	configs = map[string]ModelConfig{
		"test": {API: struct {
			URL string "yaml:\"url\""
		}{URL: upstream.URL}},
	}

	body := []byte(`{"model":"test","prompt":"hi"}`)
	req := httptest.NewRequest(http.MethodPost, "/v1/chat/completions", bytes.NewReader(body))
	rr := httptest.NewRecorder()
	chatCompletionHandler(rr, req)
	if rr.Code != http.StatusOK {
		t.Fatalf("status %d", rr.Code)
	}
	if !bytes.Equal(rr.Body.Bytes(), body) {
		t.Fatalf("unexpected response: %s", rr.Body.String())
	}
}

func TestChatCompletionHandler_BadJSON(t *testing.T) {
	configs = map[string]ModelConfig{"m": {API: struct {
		URL string `yaml:"url"`
	}{URL: "http://example.com"}}}
	req := httptest.NewRequest(http.MethodPost, "/v1/chat/completions", bytes.NewReader([]byte("bad{")))
	rr := httptest.NewRecorder()
	chatCompletionHandler(rr, req)
	if rr.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d", rr.Code)
	}
}

func TestChatCompletionHandler_PostError(t *testing.T) {
	configs = map[string]ModelConfig{"m": {API: struct {
		URL string `yaml:"url"`
	}{URL: "http://invalid"}}}
	body := []byte(`{"model":"m"}`)
	req := httptest.NewRequest(http.MethodPost, "/v1/chat/completions", bytes.NewReader(body))
	rr := httptest.NewRecorder()
	chatCompletionHandler(rr, req)
	if rr.Code != http.StatusBadGateway {
		t.Fatalf("expected 502, got %d", rr.Code)
	}
}

func TestChatCompletionHandler_NotFound(t *testing.T) {
	configs = map[string]ModelConfig{}
	body := []byte(`{"model":"missing"}`)
	req := httptest.NewRequest(http.MethodPost, "/v1/chat/completions", bytes.NewReader(body))
	rr := httptest.NewRecorder()
	chatCompletionHandler(rr, req)
	if rr.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", rr.Code)
	}
}
