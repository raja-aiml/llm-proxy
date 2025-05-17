package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"time"

	"llmwrapper-go/config"
)

type ModelData struct {
	ID      string `json:"id"`
	Created int64  `json:"created"`
}

type ModelList struct {
	Data []ModelData `json:"data"`
}

var configs map[string]config.ModelConfig

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

func main() {
	configs = config.LoadAllConfigs()
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/v1/models", modelsHandler)
	http.HandleFunc("/v1/chat/completions", chatCompletionHandler)
	log.Println("starting server on :8000")
	log.Fatal(http.ListenAndServe(":8000", nil))
}
