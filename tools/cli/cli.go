package cli

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/jessevdk/go-flags"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	_ "strconv"
	"time"
)

var REGISTER_ENDPOINT string = "/backend/api/auth/signup"
var LOGIN_ENDPOINT string = "/backend/api/auth/login"
var PUSH_NOTE_ENDPOINT string = "/backend/api/notes/"

// go API example: https://github.com/djotaku/spacetraders_go/blob/1ae00e1de58caa0701c1c271aad4d22dcd18e95d/spacetradersapi/api.go

type Options struct {
	PathDir     string `short:"d"  long:"path_dir" description:"path to notes director"`
	Username    string `short:"u"  long:"username" description:"username to signup/login"`
	Password    string `short:"p"  long:"password" description:"password to signup/login"`
	Register    bool   `long:"register" description:"signup an account"`
	Publish     bool   `long:"publish" description:"publish notes to server"`
	Address     string `long:"address" description:"nginx server address"`
	AccessToken string `long:"accesstoken" description:"access token to view notes"`
}
type DataWrapper struct {
	Data any `json:"data`
}
type ResponseAfterLogin struct {
	AccessToken string `json:"access_token"`
	UserID      int    `json:"user_id`
	Username    string `json:"username"`
}

type JsonData struct {
	Data JsonNotes `json:"data"`
}
type JsonNotes struct {
	Notes []NoteInfo `json:"notes"`
}
type NoteInfo struct {
	Message string `json:"message"`
	NoteId  int    `json:"note_id"`
}

func cmd_error(err error) {
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
	if message["data"] == "success" {
		fmt.Println("[INFO] Ok, account registered")
	}
}

func get_prev_notes(opts *Options) []NoteInfo {
	fmt.Println(opts.Address)

	addr := ParseAddress(opts.Address)
	GetNotesURI := addr + PUSH_NOTE_ENDPOINT
	nr, err := http.NewRequest("GET", GetNotesURI, nil)
	if err != nil {
		cmd_error(err)
	}
	nr.Header.Add("Content-Type", "application/json")
	nr.Header.Add("Authorization", fmt.Sprintf("Bearer %s", opts.AccessToken))

	client := &http.Client{}
	resp, err := client.Do(nr)
	// fmt.Println(time.Second)
	if err != nil {
		cmd_error(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		fmt.Println(resp.StatusCode)
		cmd_error(errors.New("something bad happened. check logs!"))
	}
	body, _ := ioutil.ReadAll(resp.Body)

	var jd JsonData
	err = json.Unmarshal(body, &jd)
	if err != nil {
		cmd_error(err)
	}
	// fmt.Println(len(jd.Data.Notes))
	return jd.Data.Notes
}

func NotesDiff(local_notes []string, prev_notes []string) []string {
	diff_map := make(map[string]bool)
	for _, n := range local_notes {
		diff_map[n] = true
	}
	for _, n := range prev_notes {
		diff_map[n] = false
	}
	var result []string
	for note_msg, val := range diff_map {
		if val {
			result = append(result, note_msg)
		}
	}
	fmt.Println(fmt.Sprintf(" %d notes to be published", len(result)))
	return result
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
		cmd_error(errors.New("could not login, may need to register first. check logs!"))
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
	fmt.Println(fmt.Sprintf("[INFO] %d notes present in %s dir", NoteCount, opts.PathDir))
	opts.AccessToken = message.AccessToken

	prev_notes := get_prev_notes(opts)

	size_pn := (len(prev_notes))
	prev_note_msg := make([]string, size_pn)
	for i, prev := range prev_notes {
		prev_note_msg[i] = prev.Message
	}
	// fmt.Println(prev_note_msg)

	var notes_file []string
	for _, file_note := range file_notes {
		fullpath := filepath.Join(opts.PathDir, file_note.Name())
		dat, err := (os.ReadFile(fullpath))
		if err != nil {
			cmd_error(err)
		}
		file_content := string(dat)
		notes_file = append(notes_file, file_content)
	}
	new_notes := NotesDiff(notes_file, prev_note_msg)
	for i, file_note := range new_notes {
		Push(file_note, message.AccessToken, opts)
		if i%10 == 0 {
			fmt.Println("[x] wait .. 2sec.")
			time.Sleep(2 * time.Second)
		}
		i += 1
	}
	fmt.Println("[INFO] Temporary Access token: ", message.AccessToken)

}

func Push(note string, access_token string, opts *Options) {
	addr := ParseAddress(opts.Address)
	payload_bytes, _ := json.Marshal(map[string]string{"note": note})
	PushNoteURI := addr + PUSH_NOTE_ENDPOINT

	// https://pkg.go.dev/net/http#Post
	// To set custom headers, use NewRequest and DefaultClient.Do.
	nr, err := http.NewRequest(
		"POST",
		PushNoteURI,
		bytes.NewBuffer(payload_bytes),
	)
	if err != nil {
		cmd_error(err)
	}
	nr.Header.Add("Content-Type", "application/json")
	nr.Header.Add("Authorization", fmt.Sprintf("Bearer %s", access_token))

	client := &http.Client{}
	resp, err := client.Do(nr)
	// fmt.Println(time.Second)
	if err != nil {
		cmd_error(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		fmt.Println(resp.StatusCode)
		cmd_error(errors.New("something bad happened. check logs!"))
	}
	_, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		cmd_error(err)
	}
	// fmt.Println(body)
}

func Run() {

	fmt.Println(" ")
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

	if err != nil {
		cmd_error(err)
	}

	if opts.Register {
		if opts.Username == "" || opts.Password == "" {
			cmd_error(errors.New("missing username/password."))
		}
		RegisterNginxAccount(&opts)
	}

	if opts.Publish {
		// publish notes from local dir to server.
		if opts.Username == "" || opts.Password == "" || opts.PathDir == "" {
			cmd_error(errors.New("missing username/password/path directory."))
		}
		PublishNotesFromDir(&opts)
		// fmt.Println(opts.Address)
		cmd := exec.Command("xdg-open", opts.Address)
		_, err := cmd.Output()
		if err != nil {
			fmt.Println("err:", err)
		}
		// fmt.Println(stdout)
	}

}

// golang lint
// gofmt -w <filename>
// go fmt github.com/karthikeyan/tools/cli
