package main

import "testing"

func TestParseYAML(t *testing.T) {
	cfg, err := parseYAML("../../../src/llm_wrapper/configs/expert.sample.yaml")
	if err != nil {
		t.Errorf("failed to parse YAML: %v", err)
		return
	}
	if cfg.API.URL == "" {
		t.Error("failed to parse api.url")
	}
}

// For backwards compatibility, you could also keep the original function
// that uses the new implementation internally
func TestParseSimpleYAML(t *testing.T) {
	cfg, err := parseYAML("../../../src/llm_wrapper/configs/expert.sample.yaml")
	if err != nil {
		t.Errorf("failed to parse YAML: %v", err)
		return
	}
	if cfg.API.URL == "" {
		t.Error("failed to parse api.url")
	}
}
