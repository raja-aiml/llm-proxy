package config

import (
	"bufio"
	"io"
	"log"
	"os"
	"path/filepath"
	"strings"
)

// ModelConfig mirrors the minimal YAML schema used in the Python implementation.
type ModelConfig struct {
	API struct {
		URL string
	}
	Model struct {
		Path string
	}
	SystemPrompt string
}

// ConfigDir defines where configuration YAML files are loaded from.
var ConfigDir = "../src/llm_wrapper/configs"

// LoadAllConfigs reads all YAML files from ConfigDir and returns them keyed by filename without extension.
func LoadAllConfigs() map[string]ModelConfig {
	cfgs := make(map[string]ModelConfig)

	entries, err := os.ReadDir(ConfigDir)
	if err != nil {
		log.Printf("failed to read config dir: %v", err)
		return cfgs
	}
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		ext := filepath.Ext(e.Name())
		if ext != ".yaml" && ext != ".yml" {
			continue
		}
		path := filepath.Join(ConfigDir, e.Name())
		mc, err := parseSimpleYAML(path)
		if err != nil {
			log.Printf("failed to load config file %s: %v", e.Name(), err)
			continue
		}
		id := strings.TrimSuffix(e.Name(), ext)
		cfgs[id] = mc
	}
	return cfgs
}

// parseSimpleYAML parses the small subset of YAML used in example configs.
// It only supports keys: api.url, model.path and system_prompt.
func parseSimpleYAML(path string) (ModelConfig, error) {
	f, err := os.Open(path)
	if err != nil {
		return ModelConfig{}, err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	var cfg ModelConfig
	section := ""
	recognized := false
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if len(line) == 0 || strings.HasPrefix(line, "#") {
			continue
		}
		if strings.HasSuffix(line, ":") {
			section = strings.TrimSuffix(line, ":")
			continue
		}
		if section == "api" && strings.HasPrefix(line, "url:") {
			cfg.API.URL = strings.TrimSpace(strings.TrimPrefix(line, "url:"))
			recognized = true
		} else if section == "model" && strings.HasPrefix(line, "path:") {
			cfg.Model.Path = strings.TrimSpace(strings.TrimPrefix(line, "path:"))
			recognized = true
		} else if strings.HasPrefix(line, "system_prompt:") {
			cfg.SystemPrompt = strings.TrimSpace(strings.TrimPrefix(line, "system_prompt:"))
			recognized = true
		}
	}
	if err := scanner.Err(); err != nil {
		return ModelConfig{}, err
	}
	if !recognized {
		return ModelConfig{}, io.ErrUnexpectedEOF
	}
	return cfg, nil
}
