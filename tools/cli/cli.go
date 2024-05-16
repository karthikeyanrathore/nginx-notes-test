package cli

import (
	"fmt"
	"os"
	"github.com/jessevdk/go-flags"
)

type Options struct {

	PathDir   string  `short:"d" long:"path_dir" description:"path to notes director"`
	Username  string  `short:"u"  long:"username" description:"username to signup/login"`
	Password  string  `short:"p"  long:"password" description:"password to signup/login"`
	Register  bool    `long:"register" description:"signup an account"`
	Publish   bool    `long:"publish" description:"publish notes to server"`
}

func RegisterNginxAccount(username string, password string) {
	fmt.Println("register")
}

func Run() {

	fmt.Println("CLI")

	/*
	Take input of the following
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


	var opts  = Options{}

	_, err := flags.ParseArgs(&opts, os.Args)

	if (err != nil){
		fmt.Println(err)
		os.Exit(1)
	}

	if (opts.Register) {
		RegisterNginxAccount(opts.Username, opts.Password)
	}

}