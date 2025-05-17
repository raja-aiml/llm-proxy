package config

import (
	"bufio"
	"os"
	"path/filepath"
	"strings"
)

type API struct {
	URL string
}

type Model struct {
	Path string
}

type ModelConfig struct {
	API          API
	Model        Model
	SystemPrompt string
}

// LoadAll reads all YAML config files under dir.
// It ignores non-YAML files and invalid configs.
func LoadAll(dir string) map[string]ModelConfig {
	cfgs := make(map[string]ModelConfig)
	entries, err := os.ReadDir(dir)
	if err != nil {
		return cfgs
	}
	for _, e := range entries {
		if e.IsDir() || !(strings.HasSuffix(e.Name(), ".yaml") || strings.HasSuffix(e.Name(), ".yml")) {
			continue
		}
		path := filepath.Join(dir, e.Name())
		cfg, err := parseSimpleYAML(path)
		if err != nil {
			continue
		}
		if cfg.API.URL == "" && cfg.Model.Path == "" && cfg.SystemPrompt == "" {
			// treat empty config as invalid
			continue
		}
		id := strings.TrimSuffix(e.Name(), filepath.Ext(e.Name()))
		cfgs[id] = cfg
	}
	return cfgs
}

// parseSimpleYAML parses a minimal subset of YAML used by the configs.
func parseSimpleYAML(path string) (ModelConfig, error) {
	f, err := os.Open(path)
	if err != nil {
		return ModelConfig{}, err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	var cfg ModelConfig
	section := ""
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		if strings.HasSuffix(line, ":") {
			section = strings.TrimSuffix(line, ":")
			continue
		}
		switch {
		case section == "api" && strings.HasPrefix(line, "url:"):
			cfg.API.URL = strings.TrimSpace(strings.TrimPrefix(line, "url:"))
		case section == "model" && strings.HasPrefix(line, "path:"):
			cfg.Model.Path = strings.TrimSpace(strings.TrimPrefix(line, "path:"))
		case strings.HasPrefix(line, "system_prompt:"):
			cfg.SystemPrompt = strings.TrimSpace(strings.TrimPrefix(line, "system_prompt:"))
		default:
			// unrecognized line -> mark invalid
			return ModelConfig{}, os.ErrInvalid
		}
	}
	if err := scanner.Err(); err != nil {
		return ModelConfig{}, err
	}
	return cfg, nil
}
