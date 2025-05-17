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
	"time"

	"gopkg.in/yaml.v3"
)

type Parameters struct {
	Temperature float64 `yaml:"temperature"`
	TopP        float64 `yaml:"top_p"`
	TopK        int     `yaml:"top_k"`
	Stream      bool    `yaml:"stream"`
}

type ModelConfig struct {
	API struct {
		URL string `yaml:"url"`
	} `yaml:"api"`
	Model struct {
		Path string `yaml:"path"`
	} `yaml:"model"`
	SystemPrompt string     `yaml:"system_prompt"`
	Parameters   Parameters `yaml:"parameters"`
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
		mc, err := parseYAML(path)
		if err != nil {
			log.Printf("failed to parse config %s: %v", path, err)
			continue
		}
		id := e.Name()[:len(e.Name())-len(filepath.Ext(e.Name()))]
		cfgs[id] = mc
	}
	return cfgs
}

// parseYAML parses a YAML config file and returns a ModelConfig
func parseYAML(path string) (ModelConfig, error) {
	var cfg ModelConfig

	data, err := os.ReadFile(path)
	if err != nil {
		return ModelConfig{}, err
	}

	err = yaml.Unmarshal(data, &cfg)
	if err != nil {
		return ModelConfig{}, err
	}

	return cfg, nil
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
	body, _ := json.Marshal(req)
	upstreamReq, err := http.NewRequest("POST", cfg.API.URL, bytes.NewReader(body))
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}
	upstreamReq.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(upstreamReq)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	if stream, _ := req["stream"].(bool); stream {
		w.Header().Set("Content-Type", "text/event-stream")
		w.Header().Set("Cache-Control", "no-cache")
		w.Header().Set("Connection", "keep-alive")
		w.Header().Set("X-Accel-Buffering", "no")
		w.WriteHeader(http.StatusOK)
		flusher, ok := w.(http.Flusher)
		reader := bufio.NewReader(resp.Body)
		for {
			line, err := reader.ReadBytes('\n')
			if len(line) > 0 {
				w.Write(line)
				if ok {
					flusher.Flush()
				}
			}
			if err != nil {
				break
			}
		}
	} else {
		w.WriteHeader(resp.StatusCode)
		io.Copy(w, resp.Body)
	}
}

func main() {
	configs = loadConfigs("../src/llm_wrapper/configs")
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/v1/models", modelsHandler)
	http.HandleFunc("/v1/chat/completions", chatCompletionHandler)
	log.Println("starting server on :8000")
	log.Fatal(http.ListenAndServe(":8000", nil))
}
