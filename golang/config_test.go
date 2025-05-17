package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadConfigsValid(t *testing.T) {
	dir := t.TempDir()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	data := []byte("api:\n  url: u\nmodel:\n  path: p\n")
	os.WriteFile(filepath.Join(dir, "foo.yaml"), data, 0o644)
	cfgs := LoadConfigs(dir)
	if _, ok := cfgs["foo"]; !ok {
		t.Fatalf("expected config 'foo'")
	}
	if cfgs["foo"].API.URL != "u" {
		t.Fatalf("unexpected URL: %s", cfgs["foo"].API.URL)
	}
}

func TestLoadConfigsMissingDir(t *testing.T) {
	cfgs := LoadConfigs("/does/not/exist")
	if len(cfgs) != 0 {
		t.Fatalf("expected empty map for missing dir")
	}
}

func TestLoadConfigsIgnoreNonYAML(t *testing.T) {
	dir := t.TempDir()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	os.WriteFile(filepath.Join(dir, "ignore.txt"), []byte("bad"), 0o644)
	os.WriteFile(filepath.Join(dir, "bar.yml"), []byte("api:\n  url: u\nmodel:\n  path: p\n"), 0o644)
	cfgs := LoadConfigs(dir)
	if len(cfgs) != 1 {
		t.Fatalf("expected 1 config, got %d", len(cfgs))
	}
	if _, ok := cfgs["bar"]; !ok {
		t.Fatalf("missing bar config")
	}
}

func TestLoadConfigsInvalidYAML(t *testing.T) {
	dir := t.TempDir()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	os.WriteFile(filepath.Join(dir, "bad.yaml"), []byte(":::"), 0o644)
	cfgs := LoadConfigs(dir)
	if len(cfgs) != 0 {
		t.Fatalf("expected 0 configs, got %d", len(cfgs))
	}
}
