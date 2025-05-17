package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

func main() {
	query := flag.String("query", "", "prompt to send")
	model := flag.String("model", "expert", "model id")
	stream := flag.Bool("stream", true, "stream output")
	base := flag.String("base-url", "http://localhost:8000/v1", "server base url")
	flag.Parse()

	if *query == "" {
		fmt.Print("You: ")
		line, _ := bufio.NewReader(os.Stdin).ReadString('\n')
		*query = strings.TrimSpace(line)
	}

	payload := map[string]interface{}{
		"model":    *model,
		"messages": []map[string]string{{"role": "user", "content": *query}},
		"stream":   *stream,
	}
	body, _ := json.Marshal(payload)
	resp, err := http.Post(*base+"/chat/completions", "application/json", bytes.NewReader(body))
	if err != nil {
		fmt.Println("request error:", err)
		os.Exit(1)
	}
	defer resp.Body.Close()
	if *stream {
		reader := bufio.NewReader(resp.Body)
		for {
			line, err := reader.ReadBytes('\n')
			if len(line) > 0 {
				fmt.Print(string(line))
			}
			if err != nil {
				break
			}
		}
	} else {
		io.Copy(os.Stdout, resp.Body)
	}
}
