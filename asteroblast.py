# Include all necessary tools.
import math
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


class Blast(ScreenWrapper):
    """A projectile. Spacecraft's blaster weapon system."""

    # Load assets.
    BLAST_IMG = games.load_image("./assets/graphics/blast-ball.png")

    def __init__(self, craft_x, craft_y, craft_angle):
        # Appeal to the ScreenWrapper constructor in order
        # to set up the image and call upon coordinates.
        super(Blast, self).__init__(
            image=Blast.BLAST_IMG,
            x=craft_x,
            y=craft_y
        )


class Spacecraft(ScreenWrapper):
    """An actual player."""

    TURN_FACTOR = 5
    VELOCITY_FACTOR = 0.1
    VELOCITY_MAX = 4

    # Load assets.
    SPACECRAFT_IMG = games.load_image("./assets/graphics/spacecraft.png")

    def __init__(self, x, y):
        # Appeal to the ScreenWrapper constructor in order
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

        # Turn ship leftwards along it's axis via LEFT KEY.
        if games.keyboard.is_pressed(games.K_LEFT):
            self.angle -= Spacecraft.TURN_FACTOR

        # Turn ship rightwards along it's axis via RIGHT KEY.
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.angle += Spacecraft.TURN_FACTOR

        # Propel ship forward.
        if games.keyboard.is_pressed(games.K_UP):
            # The trick is to shift the craft along the cartesian coordinate system:
            # using math sine and cosine functions here to determine the exact placement;
            # the actual angle of the sprite has to be converted from degrees to radians,
            # because superwires uses degrees and math trigonometric functions are running
            # on radians;
            # speed is incremented by the VELOCITY_FACOTR constant infinitely via UP KEY...
            self.dx += Spacecraft.VELOCITY_FACTOR * math.sin(math.radians(self.angle))
            self.dy += Spacecraft.VELOCITY_FACTOR * -math.cos(math.radians(self.angle))

        # ...until it's regulated via update() method itself - the craft cannot go faster
        # than value specified in VELOCITY_MAX constant.
        # Basically these two lines are picking the velocity factor between:
        # 0, which is game starting value -
        # and 4, which is max speed (VELOCITY_MAX).
        # Everything happens in terms of (x, y) coordinate system.
        self.dx = min(max(self.dx, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)
        self.dy = min(max(self.dy, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)

        # Shoot a projectile via SPACE KEY.
        if games.keyboard.is_pressed(games.K_SPACE):
            new_blast = Blast(craft_x=self.x, craft_y=self.y, craft_angle=self.angle)
            games.screen.add(new_blast)


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
