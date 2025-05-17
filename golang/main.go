package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

type ModelConfig struct {
	API struct {
		URL string `yaml:"url"`
	} `yaml:"api"`
	Model struct {
		Path string `yaml:"path"`
	} `yaml:"model"`
	SystemPrompt string `yaml:"system_prompt"`
}

type ModelData struct {
	ID      string `json:"id"`
	Created int64  `json:"created"`
}

type ModelList struct {
	Data []ModelData `json:"data"`
}

var configs map[string]ModelConfig

func loadConfigs(dir string) map[string]ModelConfig {
	cfgs := make(map[string]ModelConfig)
	entries, err := os.ReadDir(dir)
	if err != nil {
		log.Println("failed to read config dir:", err)
		return cfgs
	}
	for _, e := range entries {
		if e.IsDir() || !(filepath.Ext(e.Name()) == ".yaml" || filepath.Ext(e.Name()) == ".yml") {
			continue
		}
		path := filepath.Join(dir, e.Name())
		mc := parseSimpleYAML(path)
		id := e.Name()[:len(e.Name())-len(filepath.Ext(e.Name()))]
		cfgs[id] = mc
	}
	return cfgs
}

// parseSimpleYAML parses a very small subset of YAML used in the sample configs
// without requiring any external dependencies. This is not a full YAML parser
// and only supports the specific structure found in the repository's config
// files.
func parseSimpleYAML(path string) ModelConfig {
	file, err := os.Open(path)
	if err != nil {
		return ModelConfig{}
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var cfg ModelConfig
	section := ""
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if strings.HasSuffix(line, ":") {
			section = strings.TrimSuffix(line, ":")
			continue
		}
		if section == "api" && strings.HasPrefix(line, "url:") {
			cfg.API.URL = strings.TrimSpace(strings.TrimPrefix(line, "url:"))
		} else if section == "model" && strings.HasPrefix(line, "path:") {
			cfg.Model.Path = strings.TrimSpace(strings.TrimPrefix(line, "path:"))
		} else if strings.HasPrefix(line, "system_prompt:") {
			cfg.SystemPrompt = strings.TrimSpace(strings.TrimPrefix(line, "system_prompt:"))
		}
	}
	return cfg
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func modelsHandler(w http.ResponseWriter, r *http.Request) {
	list := ModelList{Data: []ModelData{}}
	for id := range configs {
		list.Data = append(list.Data, ModelData{ID: id, Created: time.Now().Unix()})
	}
	json.NewEncoder(w).Encode(list)
}

func chatCompletionHandler(w http.ResponseWriter, r *http.Request) {
	// Placeholder implementation - forward request to configured API
	var req map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	modelID, _ := req["model"].(string)
	cfg, ok := configs[modelID]
	if !ok {
		http.Error(w, "model not found", http.StatusNotFound)
		return
	}
	// Forward request
	body, _ := json.Marshal(req)
	resp, err := http.Post(cfg.API.URL, "application/json", bytes.NewReader(body))
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}

func newServer(addr, cfgDir string) *http.Server {
	configs = loadConfigs(cfgDir)
	mux := http.NewServeMux()
	mux.HandleFunc("/health", healthHandler)
	mux.HandleFunc("/v1/models", modelsHandler)
	mux.HandleFunc("/v1/chat/completions", chatCompletionHandler)
	return &http.Server{Addr: addr, Handler: mux}
}

// listenAndServe is a package level variable so tests can replace it.
var listenAndServe = func(addr string, h http.Handler) error {
	return http.ListenAndServe(addr, h)
}

func run(addr, cfgDir string) error {
	srv := newServer(addr, cfgDir)
	log.Println("starting server on " + addr)
	return listenAndServe(srv.Addr, srv.Handler)
}

// runFn allows tests to replace the run function used by main.
var runFn = run

func main() {
	if err := runFn(":8000", "../src/llm_wrapper/configs"); err != nil {
		log.Fatal(err)
	}

}
