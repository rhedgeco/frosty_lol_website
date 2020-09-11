let socket = new WebSocket("ws://localhost:443");
let chatType = document.getElementById("chat-type");
let messageHolder = document.getElementById("chat-messages");
let connected = false;
let chat_template = document.getElementById("chat-template");
let date_template = document.getElementById("date-template");
let user_template = document.getElementById("user-template");
let chat_form = document.getElementById("chat-form");
let chat_signin = document.getElementById("chat-sign-in");

function onSignIn(googleUser) {
    let profile = googleUser.getBasicProfile();
    let id_token = googleUser.getAuthResponse().id_token;
    let auth2 = gapi.auth2.getAuthInstance();
    auth2.disconnect();
    console.log('Token: ' + id_token);
    console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
    console.log('Name: ' + profile.getName());
    console.log('Image URL: ' + profile.getImageUrl());
    console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.

    send_token(id_token);
}

function signOut() {
    let auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        console.log('User signed out.');
    });
}

function send_token(id_token) {
    let xhr = new XMLHttpRequest();
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
    let temp = chat_template.cloneNode(true);
    temp.innerHTML = temp.innerHTML.replace("chat_message", message);
    temp.innerHTML = temp.innerHTML.replace("chat_time", time);
    return temp;
}

function get_date_template(date) {
    let temp = date_template.cloneNode(true);
    temp.innerHTML = temp.innerHTML.replace("chat_date", date);
    return temp;
}

function get_user_template(user) {
    let temp = user_template.cloneNode(true);
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
    let chat = chatType.value;
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
    let req = new XMLHttpRequest();
    req.open('GET', 'api/chat');
    req.onload = function () {
        if (req.status === 200) {
            messageHolder.innerHTML = "";
            let lastDate = "";
            let lastUser = "";
            let chats = JSON.parse(req.responseText);
            for (let i = 0; i < chats.length; i++) {
                let date = chats[i][2];
                let user = chats[i][3];
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