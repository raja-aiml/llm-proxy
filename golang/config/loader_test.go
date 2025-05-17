package config

import (
	"os"
	"path/filepath"
	"testing"
)

// helper to create temporary config directory
func setupTempDir(t *testing.T) string {
	t.Helper()
	dir := t.TempDir()
	ConfigDir = dir
	return dir
}

func writeFile(t *testing.T, dir, name, content string) {
	t.Helper()
	path := filepath.Join(dir, name)
	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		t.Fatalf("write file: %v", err)
	}
}

func TestLoadAllConfigsWithValidYAML(t *testing.T) {
	dir := setupTempDir(t)
	writeFile(t, dir, "foo.yaml", "api:\n  url: u\nmodel:\n  path: p\n")

	configs := LoadAllConfigs()
	cfg, ok := configs["foo"]
	if !ok {
		t.Fatalf("expected foo config")
	}
	if cfg.API.URL != "u" {
		t.Errorf("unexpected api.url %q", cfg.API.URL)
	}
	if cfg.Model.Path != "p" {
		t.Errorf("unexpected model.path %q", cfg.Model.Path)
	}
}

func TestLoadAllConfigsMissing(t *testing.T) {
	dir := setupTempDir(t)
	os.RemoveAll(dir) // remove directory to simulate missing
	configs := LoadAllConfigs()
	if len(configs) != 0 {
		t.Fatalf("expected empty configs")
	}
}

func TestLoadAllConfigsIgnoresNonYAML(t *testing.T) {
	dir := setupTempDir(t)
	writeFile(t, dir, "ignore.txt", "ignore")
	writeFile(t, dir, "good.yml", "api:\n  url: u\nmodel:\n  path: p\n")

	configs := LoadAllConfigs()
	if len(configs) != 1 {
		t.Fatalf("expected one config, got %d", len(configs))
	}
	if _, ok := configs["good"]; !ok {
		t.Fatalf("expected good config present")
	}
}

func TestLoadAllConfigsInvalidYAML(t *testing.T) {
	dir := setupTempDir(t)
	writeFile(t, dir, "bad.yaml", "::::")

	configs := LoadAllConfigs()
	if len(configs) != 0 {
		t.Fatalf("expected no configs loaded")
	}
}
