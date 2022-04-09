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

    # Destroy the object -- remove it from the screen.
    def die(self):
        self.destroy()


class Debris(ScreenWrapper):
    """Space rock -- enemy of the game.An asteroid to be shot."""

    # Asteroids classification constants.
    SMALL = 1
    MEDIUM = 2
    BIG = 3

    # Load assets.
    ASTEROID_IMAGES = {
        SMALL: games.load_image('./assets/graphics/asteroid-small.png'),
        MEDIUM: games.load_image('./assets/graphics/asteroid-medium.png'),
        BIG: games.load_image('./assets/graphics/asteroid-big.png')
    }

    def __init__(self, x, y, size):
        # Appeal to the ScreenWrapper constructor in order
        # to set up the image and call upon coordinates.
        super(Debris, self).__init__(
            image=Debris.ASTEROID_IMAGES[size],
            x=x,
            y=y
        )

        self.size = size


class Blast(ScreenWrapper):
    """A projectile. Spacecraft's blaster weapon system."""

    SPAWN_BUFFER_PX = 25
    VELOCITY_FACTOR = 10
    BLAST_LIFETIME = 30
    BLAST_DELAY = 50

    # Load assets.
    BLAST_IMG = games.load_image("./assets/graphics/blast-ball.png")

    def __init__(self, craft_x, craft_y, craft_angle):
        # Object image representation shall spawn itself in front of the spacecraft.
        # Projectile position is calculated similarly to the Spacecraft class method.
        # The only difference is the shift in pixels by adding SPAWN_BUFFER_PX value.
        x = craft_x + Blast.SPAWN_BUFFER_PX * math.sin(math.radians(craft_angle))
        y = craft_y + Blast.SPAWN_BUFFER_PX * -math.cos(math.radians(craft_angle))

        # Projectile shall fly freely onwards from shooting spot.
        # Again, the movement calculation is along the x, y coordinate system -
        # crunched similarly to the Spaceship positioning method.
        dx = Blast.VELOCITY_FACTOR * math.sin(math.radians(craft_angle))
        dy = Blast.VELOCITY_FACTOR * -math.cos(math.radians(craft_angle))

        # Appeal to the ScreenWrapper constructor in order
        # to set up the image and call upon coordinates.
        super(Blast, self).__init__(
            image=Blast.BLAST_IMG,
            x=x,
            y=y,
            dx=dx,
            dy=dy
        )

        self.lifetime = Blast.BLAST_LIFETIME

    # Check for important object events in real time.
    def update(self):
        # Inherit wrapping mechanics.
        super(Blast, self).update()

        # Decrement the life time of the projectile...
        self.lifetime -= 1
        # ... and remove it from the screen if it's lifetime parameter
        # reaches 0.
        if self.lifetime == 0:
            self.die()


class Spacecraft(ScreenWrapper):
    """An actual player."""

    TURN_FACTOR = 5
    VELOCITY_FACTOR = 0.1
    VELOCITY_MAX = 4
    BLASTER_DELAY = 30

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

        self.blaster_cooldown = 0

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

        # ...until it's regulated via update() method itself -- the craft cannot go faster
        # than value specified in VELOCITY_MAX constant.
        # Basically these two lines are picking the velocity factor between:
        # 0, which is game starting value -
        # and 4, which is max speed (VELOCITY_MAX).
        # Everything happens in terms of (x, y) coordinate system.
        self.dx = min(max(self.dx, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)
        self.dy = min(max(self.dy, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)

        # Shoot a projectile via SPACE KEY.
        # Only works if the blaster has cooled off!
        if games.keyboard.is_pressed(games.K_SPACE) and self.blaster_cooldown == 0:
            new_blast = Blast(craft_x=self.x, craft_y=self.y, craft_angle=self.angle)
            games.screen.add(new_blast)
            self.blaster_cooldown = Spacecraft.BLASTER_DELAY

        # Wait until the blaster cools off.
        # This avoids on-screen projectile overcrowding.
        if self.blaster_cooldown:
            self.blaster_cooldown -= 1


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
        # This defines level number and it's difficulty.
        # Look up advance() below for details.
        self.level = 0

        # Construct spacecraft object
        # and add it to the screen.
        self.spacecraft = Spacecraft(
            x=Game.SCREEN_WIDTH_CENTER,
            y=Game.SCREEN_HEIGHT_CENTER
        )
        games.screen.add(self.spacecraft)


    # Allow the player to perform an actual gameplay -- level by level.
    def play(self):
        # Set up chosen background.
        games.screen.background = Game.ORBIT_IMG

        # Start particular level.
        self.advance()

        # Run the actual game -- keep the screen running
        # by evoking the main loop.
        games.screen.mainloop()

    def advance(self):
        # Increment the level number and it's difficulty.
        # Player gets more debris to shoot with each level iteration.
        self.level += 1
        for _ in range(self.level):
            x=100
            y=200
            new_debris = Debris(
                x=x,
                y=x,
                size=Debris.BIG
            )
            games.screen.add(new_debris)


def main():
    # Create Game instance.
    asteroblast = Game()
    # Defend these skies!
    asteroblast.play()


if __name__ == "__main__":
    main()
