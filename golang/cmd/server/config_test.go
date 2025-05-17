package main

import "testing"

func TestParseSimpleYAML(t *testing.T) {
	cfg := parseSimpleYAML("../../../src/llm_wrapper/configs/expert.sample.yaml")
	if cfg.API.URL == "" {
		t.Error("failed to parse api.url")
	}
}
