# Include all necessary tools.
from superwires import games

# Create window and get access to games instructions subset.
games.init(
    screen_width=800,
    screen_height=600,
    fps=60
)


class Game(object):
    """Gameplay core mechanics."""

    # Load assets.
    ORBIT_IMG = games.load_image("./assets/graphics/orbit.png")

    # Allow the player to perform an actual gameplay - level by level.
    def play(self):
        # Set up chosen background.
        games.screen.background = Game.ORBIT_IMG

        # Run the actual game - keep the screen running
        # by evoking the main loop.
        games.screen.mainloop()


def main():
    # Create Game instance.
    asteroblast = Game()
    # Defend these skies!
    asteroblast.play()


if __name__ == "__main__":
    main()
