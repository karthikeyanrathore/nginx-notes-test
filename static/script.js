
const NGINX_SERVER_HOST = "http://0.0.0.0"
const NGINX_SERVER_PORT = 80

var API_VERSION = null

function dostuff() {
    var AccessToken = document.getElementById("accesstoken").value;
    ApiGetNotes(AccessToken);
    console.log("kjasdgj");
}

function ApiGetNotes(AccessToken) {
    const URI = `${NGINX_SERVER_HOST}:${NGINX_SERVER_PORT}/api/notes`
    fetch(URI, {
        headers: {
            Authorization: "Bearer " + AccessToken,
        },
    })
        .then((response) => response.json())
        .then((ret) => {
            if (ret["data"] != undefined) {
                var errorbtn = document.getElementById("errorAlert");
                errorbtn.innerHTML = "";
                errorbtn.classList.remove("show");
                errorbtn.classList.add("d-none");
                ShowMe(ret);
            } else {
                console.log(ret);
                var errorbtn = document.getElementById("errorAlert");
                errorbtn.classList.remove("d-none");
                errorbtn.classList.add("show");
                errorbtn.innerHTML = ret[0]["error"];
            }
        });
}

function ShowMe(res) {
    console.log("ShowMe");
    // console.log(res["data"]["notes"])
    document.getElementById("links-list").innerHTML = "";
    const data = res["data"]["notes"];
    const linksList = document.getElementById("links-list");

    if (!data.length) {
        console.log("EMPTY");
        var message = document.getElementById("info-message");
        message.classList.remove("d-none");
        message.classList.add("show");
        message.innerHTML = "No Notes found.";
    } else {
        var message = document.getElementById("info-message");
        message.classList.remove("show");
        message.classList.add("d-none");
        message.innerHTML = "";
    }

    data.forEach((x) => {
        const linkElement = document.createElement("a");
        linkElement.target = "_blank";
        linkElement.href = `${NGINX_SERVER_HOST}:${NGINX_SERVER_PORT}/api/notes/${x.note_id}/raw`;
        linkElement.textContent = x.message.substring(
            0,
            Math.min(100, x.message.length)
        );
        linkElement.classList.add("list-group-item");
        // linkElement.onclick = function(event) {
        //     event.preventDefault(); // Prevent default link behavior
        //     console.log(x.note_id)
        // };

        linksList.appendChild(linkElement);
    });
}

function OpenRawNote(note_id) {
    console.log("RAW");
    console.log(note_id);
}


function ServerHealthCheck() {
    var span_id = document.getElementById("span_id")
    var connect = document.getElementById("connect")
    fetch(`${NGINX_SERVER_HOST}:${NGINX_SERVER_PORT}/version`).then(
        response => {
           
            if (response.ok) {
                console.log("Ok connection")
                span_id.classList.add("online")
                connect.innerHTML = "connected"
                console.log(response)
            }
            else {
                console.log("disconnected")
                span_id.classList.remove("online")
                connect.innerHTML = "disconnected"
            }
        })
        .catch(
            error => {
                console.log(error)
                console.log("disconnected")
                span_id.classList.remove("online")
                connect.innerHTML = "disconnected"
            })
}

function SetDomain() {
    console.log("domain")
    var domain = document.getElementById("Domain")
    domain.innerHTML = "domain: " + `${NGINX_SERVER_HOST}`.substring(7) + ":" + NGINX_SERVER_PORT  + "<br>" + "version: " + API_VERSION
}



// Periodic jobs
setInterval(ServerHealthCheck, 5000); // 5 sec 

ServerHealthCheck()

SetDomain()