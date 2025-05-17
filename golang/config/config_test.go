package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadAllValid(t *testing.T) {
	dir := t.TempDir()
	cfgPath := filepath.Join(dir, "foo.yaml")
	os.WriteFile(cfgPath, []byte("api:\n  url: http://x\nmodel:\n  path: m\nsystem_prompt: hi"), 0o644)

	cfgs := LoadAll(dir)
	if len(cfgs) != 1 {
		t.Fatalf("expected 1 config, got %d", len(cfgs))
	}
	cfg := cfgs["foo"]
	if cfg.API.URL != "http://x" || cfg.Model.Path != "m" || cfg.SystemPrompt != "hi" {
		t.Fatalf("unexpected config: %+v", cfg)
	}
}

func TestLoadAllMissingDir(t *testing.T) {
	cfgs := LoadAll("/nonexistent")
	if len(cfgs) != 0 {
		t.Fatalf("expected empty configs, got %d", len(cfgs))
	}
}

func TestLoadAllIgnoresNonYAML(t *testing.T) {
	dir := t.TempDir()
	os.WriteFile(filepath.Join(dir, "ignore.txt"), []byte("bad"), 0o644)
	os.WriteFile(filepath.Join(dir, "good.yml"), []byte("api:\n  url: u\nmodel:\n  path: p"), 0o644)
	cfgs := LoadAll(dir)
	if len(cfgs) != 1 {
		t.Fatalf("expected 1 config, got %d", len(cfgs))
	}
	if _, ok := cfgs["good"]; !ok {
		t.Fatalf("expected good config loaded")
	}
}

func TestLoadAllSkipsInvalid(t *testing.T) {
	dir := t.TempDir()
	os.WriteFile(filepath.Join(dir, "bad.yaml"), []byte(":::"), 0o644)
	cfgs := LoadAll(dir)
	if len(cfgs) != 0 {
		t.Fatalf("expected no configs, got %d", len(cfgs))
	}
}
