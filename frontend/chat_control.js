var socket = new WebSocket("ws://localhost:8765");
var chatType = document.getElementById("chat-type");
var messageHolder = document.getElementById("chat-messages");
var connected = false;
var chat_template = document.getElementById("chat-template");
var date_template = document.getElementById("date-template");
var user_template = document.getElementById("user-template");
var chat_form = document.getElementById("chat-form");
var chat_signin = document.getElementById("chat-sign-in");

function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    var id_token = googleUser.getAuthResponse().id_token;
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.disconnect();
    console.log('Token: ' + id_token);
    console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
    console.log('Name: ' + profile.getName());
    console.log('Image URL: ' + profile.getImageUrl());
    console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.

    send_token(id_token);
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        console.log('User signed out.');
    });
}

function send_token(id_token) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'api/g-oauth?idtoken=' + id_token);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function () {
        if (xhr.status === 200) {
            console.log(xhr.responseText); // SessionID
            document.cookie = 'session_id=' + xhr.responseText;
            socket.send(xhr.responseText);
        }
    };
    xhr.send();
}


socket.onopen = function (e) {
    // do nothing
};

socket.onmessage = function (event) {
    if (event.data === "validated") {
        connected = true;
        chat_form.classList.remove("hide");
        chat_signin.classList.add("hide");
    }
    update_all_messages();
};

socket.onclose = function (event) {
    connected = false;
};

socket.onerror = function (error) {
    alert(`Chat error: ${error.message}`);
};

window.onload = function () {
    update_all_messages();
};

function get_chat_template(message, time) {
    var temp = chat_template.cloneNode(true);
    temp.innerHTML = temp.innerHTML.replace("chat_message", message);
    temp.innerHTML = temp.innerHTML.replace("chat_time", time);
    return temp;
}

function get_date_template(date) {
    var temp = date_template.cloneNode(true);
    temp.innerHTML = temp.innerHTML.replace("chat_date", date);
    return temp;
}

function get_user_template(user) {
    var temp = user_template.cloneNode(true);
    temp.innerHTML = temp.innerHTML.replace("chat_user", user);
    return temp;
}

function clean_chat(chat) {
    chat = chat.replace(/&/g, "&amp;");
    chat = chat.replace(/</g, "&lt;");
    chat = chat.replace(/>/g, "&gt;");
    chat = chat.replace(/"/g, "&quot;");
    chat = chat.replace(/'/g, "&#39;");
    return chat;
}

function toggle_icon(icon1, icon2, object) {
    if (object.text === icon1) object.text = icon2;
    else object.text = icon1;
}

function toggle_minimize(object) {
    if (object.classList.contains('minimize')) object.classList.remove('minimize');
    else object.classList.add('minimize');
}

function send_message() {
    var chat = chatType.value;
    if (chat === "") return;
    chatType.value = "";
    socket.send(chat);
    chat = clean_chat(chat);
    messageHolder.append(get_chat_template(chat, "[...]"));
    update_chat_scroll();
}

function update_chat_scroll() {
    messageHolder.scrollTop = messageHolder.scrollHeight;
}

function update_all_messages() {
    var req = new XMLHttpRequest();
    req.open('GET', 'api/chat');
    req.onload = function () {
        if (req.status === 200) {
            messageHolder.innerHTML = "";
            var lastDate = "";
            var lastUser = "";
            var chats = JSON.parse(req.responseText);
            for (var i = 0; i < chats.length; i++) {
                var date = chats[i][2];
                var user = chats[i][3];
                if (lastDate !== date) {
                    messageHolder.append(get_date_template(date));
                    lastDate = date;
                }
                if (lastUser !== user) {
                    messageHolder.append(get_user_template(user));
                    lastUser = user;
                }
                messageHolder.append(get_chat_template(chats[i][0], chats[i][1]));
            }
            update_chat_scroll();
        }
    };
    req.send();
}