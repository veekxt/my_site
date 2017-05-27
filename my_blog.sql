
use my_blog;

create table `user` (
    `id` int not null AUTO_INCREMENT,
    `email` varchar(128) not null,
    `name` varchar(128) not null,
    `create_at` datetime not null,
    primary key(id)
);