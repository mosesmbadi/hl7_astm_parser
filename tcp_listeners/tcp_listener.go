package main

/*
This code will be used for troubleshooting. You can use  
it to mock an equipment that will receive the test requests
from the HL7 parser.

How to run:
cd tcp_listeners
go run simple_listener.go

Simpler than Python eh?
*/


import (
	"fmt"
	"net"
)

func main() {
	ln, err := net.Listen("tcp", ":9095")
	if err != nil {
		fmt.Println("Error starting TCP server:", err)
		return
	}
	defer ln.Close()
	fmt.Println("TCP server listening on port 9095...")

	for {
		conn, err := ln.Accept()
		if err != nil {
			fmt.Println("Error accepting connection:", err)
			continue
		}
		go handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	buf := make([]byte, 1024)
	n, err := conn.Read(buf)
	if err != nil {
		fmt.Println("Error reading from connection:", err)
		return
	}
	fmt.Printf("Received: %s\n", string(buf[:n]))
	conn.Write([]byte("Data received\n"))
}
