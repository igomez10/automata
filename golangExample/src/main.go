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

	"cloud.google.com/go/pubsub"
)

func verifyPropertyExists(currentIdentifier int) (bool, error) {

	baseURL := os.Getenv("_BASE_URL")

	u, err := url.Parse("https://" + baseURL + "/expose/" + strconv.Itoa(currentIdentifier))
	if err != nil {
		return false, fmt.Errorf("failed to parse url %+v", err)
	}
	fmt.Println("\nVisiting property", u.String())

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

func publish(identifier string) error {
	fmt.Println("publishing", identifier)
	ctx := context.Background()
	projectID := os.Getenv("PROJECT_ID")
	topicID := os.Getenv("TOPIC_ID")
	if projectID == "" || topicID == "" {
		return fmt.Errorf("required env variables undefined")
	}
	client, err := pubsub.NewClient(ctx, projectID)
	if err != nil {
		return fmt.Errorf("pubsub.NewClient: %v", err)
	}

	t := client.Topic(topicID)
	result := t.Publish(ctx, &pubsub.Message{
		Data: []byte(identifier),
	})
	// Block until the result is returned and a server-generated
	// ID is returned for the published message.
	id, err := result.Get(ctx)
	if err != nil {
		return fmt.Errorf("Get: %v", err)
	}
	fmt.Printf("Published %s with msg ID: %v\n", identifier, id)
	return nil
}

func scanProperties() {
	fmt.Println("Started scanning properties")

	initialIdentifier := 114987500
	SetCurrentIdentifier(initialIdentifier)
	biggestIdentifier := 114990500

	for {
		exists, err := verifyPropertyExists(GetCurrentIdentifier())
		if err != nil {
			fmt.Printf("failed verifying property %d \n %+v\n", GetCurrentIdentifier(), err)
		} else if exists {
			fmt.Printf("✅ - Property %d exists\n", GetCurrentIdentifier())
			go func(curr int) {
				if err := publish(strconv.Itoa(curr)); err != nil {
					fmt.Println(err)
				}
			}(GetCurrentIdentifier())
		} else {
			fmt.Printf("🚫 - Property %d does not exist\n", GetCurrentIdentifier())
		}

		SetCurrentIdentifier(CurrentIdentifier + 1)
		if GetCurrentIdentifier() > biggestIdentifier {
			log.Println("restarting counter")
			SetCurrentIdentifier(initialIdentifier)
		}

		time.Sleep(1000 * time.Millisecond)
	}
}

func main() {
	go setupCR()
	go func() {
		for {
			fmt.Println("🩺ALIVE👨‍⚕️")
			time.Sleep(20 * time.Second)
		}
	}()

	scanProperties()
}
