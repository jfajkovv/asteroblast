# Include all necessary tools.
from superwires import games

# Create window and get access to games instructions subset.
games.init(
    screen_width=800,
    screen_height=600,
    fps=60
)

# Some useful globals.
WINDOW_WIDTH = games.screen.width
WINDOW_HEIGHT = games.screen.height


class ScreenWrapper(games.Sprite):
    """The screen "wrapper"."""

    # If the object gets beyond given edge of the screen,
    # transfer it to the opposite side...
    def update(self):
        # ...from bottom to top.
        if self.top > WINDOW_HEIGHT:
            self.bottom = 0

        # ...from top to bottom.
        if self.bottom < 0:
            self.top = WINDOW_HEIGHT

        # ... from right to left.
        if self.left > WINDOW_WIDTH:
            self.right = 0

        # ...from left to right.
        if self.right < 0:
            self.left = WINDOW_WIDTH


class Spacecraft(ScreenWrapper):
    """An actual player."""

    # Load assets.
    SPACECRAFT_IMG = games.load_image('./assets/graphics/spacecraft.png')

    def __init__(self, x, y):
        # Appeal to the Sprite constructor in order
        # to set up the image and call upon coordinates.
        super(Spacecraft, self).__init__(
            image=Spacecraft.SPACECRAFT_IMG,
            x=x,
            y=y
        )

    # Check for important object events in real time.
    def update(self):
        # Inherit wrapping mechanics.
        super(Spacecraft, self).update()

        # Allow for an upward movement via UP ARROW KEY.
        if games.keyboard.is_pressed(games.K_UP):
            self.y -= 5

        # Allow for downward movement via DOWN ARROW KEY.
        if games.keyboard.is_pressed(games.K_DOWN):
            self.y += 5

        # Allow for leftward movement via LEFT ARROW KEY.
        if games.keyboard.is_pressed(games.K_LEFT):
            self.x -= 5

        # Allow for rightward movement via RIGH ARROW KEY.
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.x += 5


class Game(object):
    """Gameplay core mechanics."""

    # Load assets.
    ORBIT_IMG = games.load_image(
        filename="./assets/graphics/orbit.png",
        transparent=False
    )

    # Set up handy constants.
    SCREEN_WIDTH_CENTER = WINDOW_WIDTH/2
    SCREEN_HEIGHT_CENTER = WINDOW_HEIGHT/2


    def __init__(self):
        # Construct spacecraft object
        # and add it to the screen.
        self.spacecraft = Spacecraft(
            x=Game.SCREEN_WIDTH_CENTER,
            y=Game.SCREEN_HEIGHT_CENTER
        )
        games.screen.add(self.spacecraft)


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
