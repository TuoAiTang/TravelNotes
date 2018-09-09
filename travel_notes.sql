create table mafengwo_travel_notes(
	id int primary key AUTO_INCREMENT,
    title varchar(255),
    author varchar(255),
    sharetime varchar(255),
    viewCount int,
    commentCount int,
    favCount int,
    shareCount int,
    startTime varchar(255),
    duration varchar(255),
    personType varchar(255),
    averageCost varchar(255),
	content text
    )