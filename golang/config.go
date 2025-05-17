package main

import (
	"bufio"
	"log"
	"os"
	"path/filepath"
	"strings"
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

func LoadConfigs(dir string) map[string]ModelConfig {
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
		mc, ok := parseSimpleYAML(path)
		if !ok {
			continue
		}
		id := e.Name()[:len(e.Name())-len(filepath.Ext(e.Name()))]
		cfgs[id] = mc
	}
	return cfgs
}

// parseSimpleYAML parses a subset of YAML used in configs.
func parseSimpleYAML(path string) (ModelConfig, bool) {
	file, err := os.Open(path)
	if err != nil {
		return ModelConfig{}, false
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
	if cfg.API.URL == "" && cfg.Model.Path == "" && cfg.SystemPrompt == "" {
		return ModelConfig{}, false
	}
	return cfg, true
}
