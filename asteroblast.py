# Include all necessary tools.
import math
import random
# https://pythonhosted.org/SuperWires/index.html
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


class Bumper(ScreenWrapper):
    """Collision detection system."""

    def update(self):
        # Inherit wrapping mechanics.
        super(Bumper, self).update()

        # Simple check if any other sprite overlaps self-object...
        if self.overlapping_sprites:
            # ... and for any such sprite -- it should destroy itself.
            for sprite in self.overlapping_sprites:
                sprite.die()
            self.die()

    def die(self):
        # Create new outburst instance and put it onto the screen.
        new_explosion = Explosion(x=self.x, y=self.y)
        games.screen.add(new_explosion)
        self.destroy()


class Explosion(games.Animation):
    """Outburst animation after collision detection."""

    # Load assets.
    ANIMATION_IMAGES = [
        "./assets/graphics/explosion-1.png",
        "./assets/graphics/explosion-2.png",
        "./assets/graphics/explosion-3.png",
        "./assets/graphics/explosion-4.png",
        "./assets/graphics/explosion-5.png",
        "./assets/graphics/explosion-6.png",
        "./assets/graphics/explosion-7.png",
        "./assets/graphics/explosion-8.png",
        "./assets/graphics/explosion-9.png",
        "./assets/graphics/explosion-10.png",
    ]

    def __init__(self, x, y):
        # Appeal to the games.Animation constructor in order
        # to set up frames and call upon coordinates.
        super(Explosion, self).__init__(
            images=Explosion.ANIMATION_IMAGES,
            x=x,
            y=y,
            # Configure animation FPS.
            repeat_interval=5,
            # Set how many times animation shall display itself.
            n_repeats=1,
            is_collideable=False
        )

class Debris(ScreenWrapper):
    """Space rock -- enemy of the game.An asteroid to be shot."""

    VELOCITY = 3
    CRASH_SPAWNS = 2

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

    # Class var for debris count.
    belt = 0

    def __init__(self, game, x, y, size):
        # Appeal to the ScreenWrapper constructor in order
        # to set up the image and call upon coordinates.
        super(Debris, self).__init__(
            image=Debris.ASTEROID_IMAGES[size],
            x=x,
            y=y,
            # Set up debris speed randomly:
            # Debris.VELOCITY factor gets multiplied by a random number
            # from range of 0-0.9(9) for diversity. Next, it's getting
            # multiplied by either -1 or 1 which determines it's positive/negative
            # coordinates feed -- direction of movement.
            # The equation ends divided by size of the object --
            # smaller ones tend to be speedier.
            dx = Debris.VELOCITY*random.random()*random.choice([-1, 1])/size,
            dy = Debris.VELOCITY*random.random()*random.choice([-1, 1])/size,
            # Set up debris angle randomly for variety.
            angle=random.randrange(361)
        )

        self.size = size
        self.game = game

        Debris.belt += 1
        print(Debris.belt)

    def die(self):
        Debris.belt -= 1
        print(Debris.belt)

        # Make space rocks break up until there is no smaller size.
        if self.size != Debris.SMALL:
            for _ in range(Debris.CRASH_SPAWNS):
                # Spawn two smaller sized asteroids in the place of the crash.
                new_debris = Debris(
                    game=self.game,
                    x=self.x,
                    y=self.y,
                    size=self.size-1
                )
                games.screen.add(new_debris)

        super(Debris, self).die()

        # If there are no space rocks left...
        if Debris.belt == 0:
            # ... appeal to the Game class and it's advance method
            # in order to get to higher level.
            self.game.advance()


class Blast(Bumper):
    """A projectile. Spacecraft's blaster weapon system."""

    SPAWN_BUFFER_PX = 40
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
            dy=dy,
            is_collideable=True
        )

        self.lifetime = Blast.BLAST_LIFETIME

    # Check for important object events in real time.
    def update(self):
        # Inherit wrapping mechanics and collision detection.
        super(Blast, self).update()

        # Decrement the life time of the projectile...
        self.lifetime -= 1
        # ... and remove it from the screen if it's lifetime parameter
        # reaches 0.
        if self.lifetime == 0:
            self.destroy()


class Spacecraft(Bumper):
    """An actual player."""

    TURN_FACTOR = 5
    VELOCITY_FACTOR = 0.1
    VELOCITY_MAX = 4
    REVERSE_PULL_FACTOR = 0.07
    BLASTER_DELAY = 30

    # Load assets.
    SPACECRAFT_IMG = games.load_image("./assets/graphics/spacecraft.png")

    def __init__(self, x, y):
        # Appeal to the ScreenWrapper constructor in order
        # to set up the image and call upon coordinates.
        super(Spacecraft, self).__init__(
            image=Spacecraft.SPACECRAFT_IMG,
            x=x,
            y=y,
            is_collideable=True
        )

        self.blaster_cooldown = 0

    # Check for important object events in real time.
    def update(self):
        print(self.dx, self.dy)

        # Inherit wrapping mechanics and collision detection.
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
            # speed is incremented by the VELOCITY_FACOTR constant infinitely via UP KEY.
            self.dx += Spacecraft.VELOCITY_FACTOR * math.sin(math.radians(self.angle))
            self.dy += Spacecraft.VELOCITY_FACTOR * -math.cos(math.radians(self.angle))

        # Activate reverse pull.
        if games.keyboard.is_pressed(games.K_DOWN):
            self.dx -= Spacecraft.REVERSE_PULL_FACTOR * math.sin(math.radians(self.angle))
            self.dy -= Spacecraft.REVERSE_PULL_FACTOR * -math.cos(math.radians(self.angle))

        # Decelerate the ship until stillness.
        if games.keyboard.is_pressed(games.K_r):
            if self.dx > 0:
                self.dx -= Spacecraft.VELOCITY_FACTOR
            elif self.dx < 0:
                self.dx += Spacecraft.VELOCITY_FACTOR

            if self.dy > 0:
                self.dy -= Spacecraft.VELOCITY_FACTOR
            elif self.dy < 0:
                self.dy += Spacecraft.VELOCITY_FACTOR

        self.regulate_velocity()

        # Shoot a projectile via SPACE KEY.
        # Only works if the blaster has cooled off!
        if (games.keyboard.is_pressed(games.K_SPACE) and self.blaster_cooldown == 0) \
        or (games.keyboard.is_pressed(games.K_f) and self.blaster_cooldown ==0):
            new_blast = Blast(craft_x=self.x, craft_y=self.y, craft_angle=self.angle)
            games.screen.add(new_blast)
            self.blaster_cooldown = Spacecraft.BLASTER_DELAY

        # Wait until the blaster cools off.
        # This avoids on-screen projectile overcrowding.
        if self.blaster_cooldown:
            self.blaster_cooldown -= 1

    # Velocity is regulated via update() method itself -- the craft cannot go faster
    # than value specified in VELOCITY_MAX constant.
    # Basically these two lines are picking the velocity factor between:
    # 0, which is game starting value -
    # and 4, which is max speed (VELOCITY_MAX).
    # Everything happens in terms of (x, y) coordinate system.
    def regulate_velocity(self):
        self.dx = min(max(self.dx, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)
        self.dy = min(max(self.dy, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)


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
        self.depth = 0

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
        # Increment the level depth and it's difficulty.
        # Player gets more debris to shoot with each level iteration.
        self.depth += 1
        for _ in range(self.depth):
            # Avoid spawning debris on the ship or close to it.
            MIN_SPAWN_BUFFER_PX = 300
            MAX_SPAWN_BUFFER_PX = 350

            x_shift = self.spacecraft.x + random.randint(MIN_SPAWN_BUFFER_PX, MAX_SPAWN_BUFFER_PX)
            y_shift = self.spacecraft.y + random.randint(MIN_SPAWN_BUFFER_PX, MAX_SPAWN_BUFFER_PX)

            new_debris = Debris(
                game=self,
                x=x_shift,
                y=y_shift,
                size=random.randint(Debris.MEDIUM, Debris.BIG)
            )
            games.screen.add(new_debris)


def main():
    # Create Game instance.
    asteroblast = Game()
    # Defend these skies!
    asteroblast.play()


if __name__ == "__main__":
    main()
