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
	_ "strconv"
	"path/filepath"
)

var REGISTER_ENDPOINT string = "/api/auth/signup"
var LOGIN_ENDPOINT string = "/api/auth/login"

// go API example: https://github.com/djotaku/spacetraders_go/blob/1ae00e1de58caa0701c1c271aad4d22dcd18e95d/spacetradersapi/api.go

type Options struct {

	PathDir   string  `short:"d" long:"path_dir" description:"path to notes director"`
	Username  string  `short:"u"  long:"username" description:"username to signup/login"`
	Password  string  `short:"p"  long:"password" description:"password to signup/login"`
	Register  bool    `long:"register" description:"signup an account"`
	Publish   bool    `long:"publish" description:"publish notes to server"`
	Address   string  `long:"address" description:"nginx server address"`
}

type DataWrapper struct {
	Data any `json:"data`
}

type ResponseAfterLogin struct {
	AccessToken string  `json:"access_token"`
	UserID int 			`json:"user_id`
	Username string		`json:"username"`
}

func cmd_error(err error){
	fmt.Println("[ERROR]", err)
	os.Exit(1)
}

func ParseAddress(addr string) string {
	URL, err := url.Parse(addr)
	if err != nil {
		cmd_error(err)
	}
	// fmt.Println("Ok parsed address", URL.Host, URL.Scheme)
	address := URL.Scheme + "://" + URL.Host
	return address
}

func RegisterNginxAccount(opts *Options) {

	address := ParseAddress(opts.Address)
	_, err := http.Head(address)
	if err != nil {
		cmd_error(err)
	}
	fmt.Println("[INFO] Ok, server connection")

	payload_bytes, err := json.Marshal(map[string]string{"username": opts.Username, "password": opts.Password})
	if err != nil {
		cmd_error(err)
	}

	registerURI := address + REGISTER_ENDPOINT
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

func PublishNotesFromDir(opts *Options) {
	addr := ParseAddress(opts.Address)
	payload_bytes, _ := json.Marshal(map[string]string{"username": opts.Username, "password": opts.Password})
	LoginURI := addr + LOGIN_ENDPOINT
	resp, err := http.Post(
		LoginURI,
		"application/json",
		// https://www.reddit.com/r/golang/comments/92mm9k/what_exactly_is_bytesbuffer/
		// bytes.NewBuffer
		// it’s an adaptor that lets you use a byte slice as an io.Writer and turn strings/byte slices into io.Readers.
		bytes.NewBuffer(payload_bytes), // io.Reader taken as input by http.Post
	)
	if err != nil {
		cmd_error(err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		cmd_error(errors.New("could not login. check logs!"))
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		cmd_error(err)
	}

	// message := ResponseAfterLogin{}
	message := &ResponseAfterLogin{}
	if err = json.Unmarshal(body, &DataWrapper{message}); err != nil {
		cmd_error(err)
	}
	// fmt.Println(string(body))
	// fmt.Println(message.AccessToken)

	file_notes, err := ioutil.ReadDir(opts.PathDir)
	if err != nil {
		cmd_error(err)
	}
	NoteCount := (len(file_notes))
	fmt.Println(fmt.Sprintf("[INFO] %d notes present in directory", NoteCount))
	for  _, file_note := range file_notes[:3] {
		fullpath := filepath.Join(opts.PathDir, file_note.Name())
		dat, err := (os.ReadFile(fullpath))
		if err != nil {
			cmd_error(err)
		}
		// TODO: find a way to ignore empty file content
		file_content := string(dat)
		// fmt.Println(fullpath)
		fmt.Println(file_content)
		// // fmt.Println(datstr)
		// fmt.Println(file_note.Size())
	}	

}

// func Push(note string) bool {
// 	pass
// }

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
		cmd_error(err)
	}
	
	if (opts.Register) {
		if opts.Username == "" || opts.Password == "" {
			cmd_error(errors.New("missing username/password."))
		}
		RegisterNginxAccount(&opts)
	}

	if (opts.Publish) {
		// publish notes from local dir to server.
		if opts.Username == "" || opts.Password == "" || opts.PathDir == "" {
			cmd_error(errors.New("missing username/password/path directory."))
		}
		PublishNotesFromDir(&opts)
	}

}

/*
go build && ./tools --address http://0.0.0.0:80/  \
	--username ram  \
	--password ram  \
	--register

go build && ./tools --address http://0.0.0.0:80/  \
	--username ram  \
	--password ram  \
	--path_dir /home/vagrant/notes \
	--publish
*/