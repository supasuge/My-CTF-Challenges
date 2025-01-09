from models import Game, Flag
from database import db_session, init_db

def seed_db():
    init_db()
    games = [
        Game(1, "1990", "Super Mario World"),
        Game(2, "1980", "Snake"),
        Game(3, "1984", "Tetris"),
        Game(4, "1992", "Sonic The Hedgehog 2"),
        Game(5, "1980", "Pac-Man"),
        Game(6, "1985", "Super Mario Bros."),
        Game(7, "1997", "Goldeneye 007"),
        Game(8, "1993", "Doom"),
        Game(9, "1998", "Metal Gear Solid"),
        Game(10, "1996", "Super Mario 64"),
        Game(11, "1991", "Street Fighter II: The World Warrior"),
        Game(12, "1992", "Super Mario Kart"),
        Game(13, "1996", "Pokémon Red/Blue"),
        Game(14, "1986", "The Legend of Zelda"),
        Game(15, "1992", "Streets Of Rage 2"),
        Game(16, "1996", "Tomb Raider"),
        Game(17, "2000", "Tony Hawk's Pro Skater 2"),
        Game(18, "1999", "Super Smash Bros."),
        Game(19, "2007", "Super Mario Galaxy"),
        Game(20, "2008", "Grand Theft Auto IV"),
        Game(21, "1997", "Final Fantasy VII"),
        Game(22, "1997", "Grand Theft Auto"),
        Game(23, "1994", "Donkey Kong Country"),
        Game(24, "1998", "Spyro The Dragon"),
        Game(25, "1996", "Crash Bandicoot"),
        Game(26, "1991", "1941: Counter Attack"),
        Game(27, "1991", "A Boy and His Blob: the Rescue of Princess Blobette"),
        Game(28, "1991", "Adventures in the Magic Kingdom"),
        Game(29, "1991", "Aero Blasters: Trouble Specialty Raid Unit"),
        Game(30, "1991", "Air Duel"),
        Game(31, "1991", "Air Inferno"),
        Game(32, "1991", "Air Supply"),
        Game(33, "1991", "ActRaiser"),
        Game(34, "1991", "Al Unser Jr. Turbo Racing"),
        Game(35, "1991", "Alex Kidd in Shinobi World"),
        Game(36, "1991", "Alien Storm"),
        Game(37, "1991", "Aliens"),
        Game(38, "1991", "Altered Destiny"), 
        Game(39, "1991", "Amaransu"),
        Game(40, "1991", "American Horseshoes"),
        Game(41, "1991", "American Poker II"),
        Game(42, "1991", "Angel Nieto Pole 500"),
        Game(43, "1991", "The Legendaary Axe II"), 
        Game(44, "1991", "Aqua Jack"),
        Game(45, "1991", "Arkista's Ring"),
        Game(46, "1991", "Arrow Flash"),
        Game(47, "1991", "Ashita Tenki ni Nâre"),
        Game(48, "1991", "Success Joe"),
        Game(49, "1991", "Ashura Blaster"),
        Game(50, "1991", "Atomic Point")
    ]

    for game in games:
        db_session.add(game)

    flag = open("flag.txt").read().rstrip()

    db_session.add(Flag(flag))
    db_session.commit()