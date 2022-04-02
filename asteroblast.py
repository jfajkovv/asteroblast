# Include all necessary tools.
from superwires import games

# Create screen and get access to games instructions subset.
games.init(
    screen_width=800,
    screen_height=600,
    fps=60
)


class Game(object):
    """Gameplay core mechanics."""

    ORBIT_IMG = games.load_image("./assets/graphics/orbit.png")

    def play(self):
        games.screen.background = Game.ORBIT_IMG

        games.screen.mainloop()


def main():
    asteroblast = Game()
    asteroblast.play()


if __name__ == "__main__":
    main()
