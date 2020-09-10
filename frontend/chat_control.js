let socket = new WebSocket("ws://localhost:8765");
let chatType = document.getElementById("chat-type");
let messageHolder = document.getElementById("chat-messages");
let connected = false;
let chat_template = document.getElementById("chat-template");
let date_template = document.getElementById("date-template");

socket.onopen = function (e) {
    connected = true;
};

socket.onmessage = function (event) {
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

function toggle_icon(icon1, icon2, object) {
    if (object.text === icon1) object.text = icon2;
    else object.text = icon1;
}

function toggle_minimize(object) {
    if(object.classList.contains('minimize')) object.classList.remove('minimize');
    else object.classList.add('minimize');
}

function send_message() {
    let chat = chatType.value;
    if(chat === "") return;
    chatType.value = "";
    socket.send(chat);
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
        if(req.status === 200) {
            messageHolder.innerHTML = "";
            let lastDate = "";
            let chats = JSON.parse(req.responseText);
            for (let i = 0; i < chats.length; i++) {
                let date = chats[i][2];
                if (lastDate !== date) {
                    messageHolder.append(get_date_template(date));
                    lastDate = date;
                }
                messageHolder.append(get_chat_template(chats[i][0], chats[i][1]));
            }
            update_chat_scroll();
        }
    };
    req.send();
}