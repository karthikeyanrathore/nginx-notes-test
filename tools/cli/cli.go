package cli

import (
	"fmt"
	"errors"
	"os"
	"github.com/jessevdk/go-flags"
	"net/http"
	"net/url"
	"encoding/json"
	"bytes"
	"io/ioutil"
)

type Options struct {

	PathDir   string  `short:"d" long:"path_dir" description:"path to notes director"`
	Username  string  `short:"u"  long:"username" description:"username to signup/login"`
	Password  string  `short:"p"  long:"password" description:"password to signup/login"`
	Register  bool    `long:"register" description:"signup an account"`
	Publish   bool    `long:"publish" description:"publish notes to server"`
	Address   string  `long:"address" description:"nginx server address"`
}


func cmd_error(err error){
	fmt.Println("[ERROR]", err)
	os.Exit(1)
}

func RegisterNginxAccount(opts *Options) {

	URL, err := url.Parse(opts.Address)
	if err != nil {
		cmd_error(err)
	}
	// fmt.Println("Ok parsed address", URL.Host, URL.Scheme)
	address := URL.Scheme + "://" + URL.Host
	_, err = http.Head(address)
	if err != nil {
		cmd_error(err)
	}
	fmt.Println("[INFO] Ok, server connection")

	payload_bytes, err := json.Marshal(map[string]string{"username": opts.Username, "password": opts.Password})
	if err != nil {
		cmd_error(err)
	}

	registerURI := address + "/api/auth/signup"
	resp, err := http.Post(
		registerURI,
		"application/json",
		// https://www.reddit.com/r/golang/comments/92mm9k/what_exactly_is_bytesbuffer/
		// bytes.NewBuffer
		// it’s an adaptor that lets you use a byte slice as an io.Writer and turn strings/byte slices into io.Readers.
		bytes.NewBuffer(payload_bytes), // io.Reader taken as input by http.Post
	)
	defer resp.Body.Close()
	if resp.StatusCode == 403 {
		cmd_error(errors.New("Pick a different username."))
	}
	if resp.StatusCode != 200 {
		cmd_error(errors.New("error occurred. check logs!"))
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		cmd_error(err)
	}
	var message map[string]interface{}
	if err = json.Unmarshal(body, &message); err != nil {
		cmd_error(err)
	}
	if (message["data"] == "success"){
		fmt.Println("[INFO] Ok, account registered")
	}
}

func Run() {

	fmt.Println(" ***CLI*** \n")
	/*
	Take input of the following
		* nginx server address
		* directory path of the notes (ex: /home/vagrant/notes)
		* username
		* password
		* register y/n
		* login & publish at the same time y/n
		* sync_publish y/n (background job might do this later)
	* user first have to signup and then publish his notes.
	* publish
		* iterate over all the notes and check if note already present in db, if not then add it.
	*/


	var opts = Options{}

	_, err := flags.ParseArgs(&opts, os.Args)

	if (err != nil){
		fmt.Println(err)
		os.Exit(1)
	}

	if (opts.Register) {
		RegisterNginxAccount(&opts)
	}

}

/*
go build && ./tools --address http://0.0.0.0:80/  \
	--username ram  \
	--password ram  \
	--register
*/