package main

import (
	"fmt"
	"log"
	"net/http"
	// "os"
)

var CurrentIdentifier = 0

func GetCurrentIdentifier() int {
	return CurrentIdentifier
}

func SetCurrentIdentifier(newVaue int) {
	CurrentIdentifier = newVaue
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Received Request")
	w.WriteHeader(200)
	fmt.Fprintf(w, "Current Identifier %d \n", GetCurrentIdentifier())

}

func setupCR() {
	fmt.Println("Hello world sample started.")
	http.HandleFunc("/", handler)
	// port := os.Getenv("PORT")
	port := "8080"
	// if port == "" {
	// 	port = "8080"
	// }
	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%s", port), nil))
}
