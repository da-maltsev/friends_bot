from enum import Enum


class AddMeetingEnum(int, Enum):
    title = 1
    month = 2
    day = 3
    hour = 4
    minute = 5
    location = 6


class MeetingTypesEnum(str, Enum):
    beer = "Попить пива"
    meet = "Увидеться"
    birthday = "День рождения"
    talk = "Поболтать"
    walk = "Погулять"
    play = "Поиграть"


class MeetingLocationEnum(str, Enum):
    home = "Дома"
    bar = "Бар"
    street = "На улице"
    cinema = "В кино"
    theatre = "В театре"
    online = "Онлайн"
