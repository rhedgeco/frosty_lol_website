create table
if not exists users
(
    user_id          text not null,
    nickname        text,
    session_id      text,
    session_timeout text,
    photo           text
);

create unique index if not exists google_oauth_user_id_uindex
    on users (user_id);