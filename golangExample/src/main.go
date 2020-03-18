package main

import (
	"context"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"time"
)

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Hello world received a request.")
	target := os.Getenv("TARGET")
	if target == "" {
		target = "World"
	}
	fmt.Fprintf(w, "Hello %s!\n", target)
}

func setupCR() {
	fmt.Println("Hello world sample started.")

	http.HandleFunc("/", handler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%s", port), nil))
}

func verifyPropertyExists(currentIdentifier int) (bool, error) {
	fmt.Println("\nVisiting property", currentIdentifier)

	baseURL := os.Getenv("_BASE_URL")

	u, err := url.Parse("https://" + baseURL + "/expose/" + strconv.Itoa(currentIdentifier))
	if err != nil {
		return false, fmt.Errorf("failed to parse url", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10000*time.Millisecond)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "HEAD", u.String(), nil)
	if err != nil {
		log.Fatalf("failed to build request %+v", err)
	}

	c := http.Client{Timeout: 30000 * time.Millisecond}

	res, err := c.Do(req)
	if err != nil {
		switch err.(type) {
		case net.Error:
			err = fmt.Errorf("⏳timeout checking ⏳ %d\n%+v", currentIdentifier, err)
		default:
			err = fmt.Errorf("failed making http request to %s\n%+v", u.String(), err)
		}
		return false, err
	}

	io.Copy(ioutil.Discard, res.Body)
	defer res.Body.Close()

	switch res.StatusCode {
	case http.StatusOK:
		return true, nil
	case http.StatusMovedPermanently:
		return true, nil
	case http.StatusNotFound:
		return false, nil
	default:
		return false, fmt.Errorf("unexpected status code %d", res.StatusCode)
	}
}

func scanProperties() {
	fmt.Println("Started scanning properties")

	initialIdentifier := 114987500
	currentIdentifier := initialIdentifier
	biggestIdentifier := 114990500

	for {
		exists, err := verifyPropertyExists(currentIdentifier)
		if err != nil {
			fmt.Printf("failed verifying property %d \n %+v\n", currentIdentifier, err)
		} else if exists {
			fmt.Printf("✅ - Property %d exists\n", currentIdentifier)
		} else {
			fmt.Printf("🚫 - Property %d does not exist\n", currentIdentifier)
		}

		currentIdentifier = currentIdentifier + 1
		if currentIdentifier > biggestIdentifier {
			log.Println("restarting counter")
			currentIdentifier = initialIdentifier
		}

		time.Sleep(1000 * time.Millisecond)
	}
	fmt.Println("Unexpected exit from while loop")
}

func main() {
	go setupCR()
	scanProperties()
}
