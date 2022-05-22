# Include all necessary tools.
import math
import random
# https://pythonhosted.org/SuperWires/index.html
from superwires import games, color
from time import sleep

# Create window and get access to games instructions subset.
games.init(
    screen_width=800,
    screen_height=600,
    fps=60
)

# Some useful globals.
WINDOW_WIDTH = games.screen.width
WINDOW_HEIGHT = games.screen.height
SCREEN_WIDTH_CENTER = WINDOW_WIDTH/2
SCREEN_HEIGHT_CENTER = WINDOW_HEIGHT/2


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
            # The try-except clause serves the debris that requires multiple hits.
            try:
                for sprite in self.overlapping_sprites:
                    sprite.structure -= 1

                    if not sprite.structure:
                        sprite.die()
            except:
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

        # Add new object to the Game's belt collection.
        self.game.belt.append(self)

    def die(self):
        # Remove debris from Game's asteroid collector.
        self.game.belt.remove(self)

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

        # Add some value to the score.
        if self.size == Debris.BIG:
            self.game.score.value += 1
        elif self.size == Debris.MEDIUM:
            self.game.score.value += 2
        elif self.size == Debris.SMALL:
            self.game.score.value += 3

        self.game.score.value += int(30/self.size)

        # If there are no space rocks left...
        if not self.game.belt:
            # ... appeal to the Game class and it's advance method
            # in order to get to higher level.
            self.game.advance()


class ToughDebris(Debris):

    VELOCITY = 3
    CRASH_SPAWNS = 2

    # Asteroids classification constants.
    SMALL = 1
    MEDIUM = 2
    BIG = 3

    # Load assets.
    TOUGH_ASTEROID_IMAGES = {
        SMALL: games.load_image('./assets/graphics/tough-asteroid-small.png'),
        MEDIUM: games.load_image('./assets/graphics/tough-asteroid-medium.png'),
        BIG: games.load_image('./assets/graphics/tough-asteroid-big.png')
    }

    def __init__(self, game, x, y, size):
        # Appeal to the ScreenWrapper constructor in order
        # to set up the image and call upon coordinates.
        super(ScreenWrapper, self).__init__(
            image=ToughDebris.TOUGH_ASTEROID_IMAGES[size],
            x=x,
            y=y,
            # Just like w/ normal debris -- set up speed randomly:
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
        self.structure = 2

        # Add new object to the Game's belt collection.
        self.game.belt.append(self)

    def die(self):
        # Remove debris from Game's asteroid collector.
        self.game.belt.remove(self)

        # Make space rocks break up until there is no smaller size.
        if self.size != ToughDebris.SMALL:
            for _ in range(ToughDebris.CRASH_SPAWNS):
                # Spawn two smaller sized asteroids in the place of the crash.
                new_tough_debris = ToughDebris(
                    game=self.game,
                    x=self.x,
                    y=self.y,
                    size=self.size-1
                )
                games.screen.add(new_tough_debris)

        super(Debris, self).die()

        # Add some value to the score.
        if self.size == ToughDebris.BIG:
            self.game.score.value += 2
        elif self.size == ToughDebris.MEDIUM:
            self.game.score.value += 4
        elif self.size == ToughDebris.SMALL:
            self.game.score.value += 6

        self.game.score.value += int(30/self.size)*2

        # If there are no space rocks left...
        if not self.game.belt:
            # ... appeal to the Game class and it's advance method
            # in order to get to higher level.
            self.game.advance()


class SuperToughDebris(ToughDebris):

    CRASH_SPAWNS = 2

    # Asteroids classification constants.
    SMALL = 1
    MEDIUM = 2
    BIG = 3

    # Load assets.
    SUPER_TOUGH_ASTEROID_IMAGES = {
        SMALL: games.load_image('./assets/graphics/super-tough-asteroid-small.png'),
        MEDIUM: games.load_image('./assets/graphics/super-tough-asteroid-medium.png'),
        BIG: games.load_image('./assets/graphics/super-tough-asteroid-big.png')
    }

    def __init__(self, game, x, y, size):
        # Appeal to the ScreenWrapper constructor in order
        # to set up the image and call upon coordinates.
        super(ScreenWrapper, self).__init__(
            image=SuperToughDebris.SUPER_TOUGH_ASTEROID_IMAGES[size],
            x=x,
            y=y,
            # Just like w/ normal debris -- set up speed randomly:
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
        self.structure = 3

        # Add new object to the Game's belt collection.
        self.game.belt.append(self)

    def die(self):
        # Remove debris from Game's asteroid collector.
        self.game.belt.remove(self)

        # Make space rocks break up until there is no smaller size.
        if self.size != SuperToughDebris.SMALL:
            for _ in range(SuperToughDebris.CRASH_SPAWNS):
                # Spawn two smaller sized asteroids in the place of the crash.
                new_super_tough_debris = SuperToughDebris(
                    game=self.game,
                    x=self.x,
                    y=self.y,
                    size=self.size-1
                )
                games.screen.add(new_super_tough_debris)

        super(Debris, self).die()

        # Add some value to the score.
        if self.size == SuperToughDebris.BIG:
            self.game.score.value += 3
        elif self.size == SuperToughDebris.MEDIUM:
            self.game.score.value += 6
        elif self.size == SuperToughDebris.SMALL:
            self.game.score.value += 9

        self.game.score.value += int(30/self.size)*3

        # If there are no space rocks left...
        if not self.game.belt:
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
        # ... and remove it from the screen if it's lifetime parameter reaches 0.
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

    def __init__(self, game, x, y):
        # Appeal to the ScreenWrapper constructor in order
        # to set up the image and call upon coordinates.
        super(Spacecraft, self).__init__(
            image=Spacecraft.SPACECRAFT_IMG,
            x=x,
            y=y,
            is_collideable=True
        )

        self.game = game
        self.blaster_cooldown = 0
        self.coordinates = games.Text(
            value=None,
            size=0,
            color=color.gray
        )

    # Check for important object events in real time.
    def update(self):
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

        # Activate reverse pull via DOWN KEY.
        if games.keyboard.is_pressed(games.K_DOWN):
            self.dx -= Spacecraft.REVERSE_PULL_FACTOR * math.sin(math.radians(self.angle))
            self.dy -= Spacecraft.REVERSE_PULL_FACTOR * -math.cos(math.radians(self.angle))

        # Decelerate the ship until [almost] stillness via R KEY.
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

        # Shoot a projectile via SPACE KEY or F KEY.
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

        # Clear coordinates display (keep it updated).
        games.screen.remove(self.coordinates)

        # Show spacecraft coordinate speedometer.
        self.coordinates = games.Text(
            value=f"[ dx: {self.dx} dy: {self.dy} ]",
            size=20,
            color=color.gray,
            x=SCREEN_WIDTH_CENTER,
            y=575,
            is_collideable=False
        )
        games.screen.add(self.coordinates)

        # Evoke help screen layer via C KEY.
        if games.keyboard.is_pressed(games.K_c):
            self.game.display_help()

    # Velocity is regulated via update() method itself -- the craft cannot go faster
    # than value specified in VELOCITY_MAX constant.
    # Basically these two lines are picking the velocity factor between:
    # 0, which is game starting value -
    # and 4, which is max speed (VELOCITY_MAX).
    # Everything happens in terms of (x, y) coordinate system.
    def regulate_velocity(self):
        self.dx = min(max(self.dx, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)
        self.dy = min(max(self.dy, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)


class GameStarter(games.Sprite):

    def __init__(self):
        super(GameStarter, self).__init__(
            image=Blast.BLAST_IMG,
            is_collideable=False
        )

        self.start_key = games.Text(
            value="[ press S to start ]",
            size=60,
            color=color.gray,
            x=SCREEN_WIDTH_CENTER,
            y=SCREEN_HEIGHT_CENTER,
            is_collideable=False
        )
        games.screen.add(self.start_key)

    def update(self):
        if games.keyboard.is_pressed(games.K_s):
#            space_pressed = games.Message(
#                value="SPACE pressed",
#                size=30,
#                color=color.light_gray,
#                x=SCREEN_WIDTH_CENTER,
#                y=SCREEN_HEIGHT_CENTER + 50,
#                lifetime=120,
#                is_collideable=False,
#                after_death=None
#            )
#            games.screen.add(space_pressed)

            games.screen.remove(self.start_key)
            self.destroy()

            # Create Game instance.
            asteroblast = Game()
            # Defend these skies!
            asteroblast.play()


class StartScreen(object):

    def __init__(self):
        self.starter = GameStarter()
        games.screen.add(self.starter)


class Game(object):
    """Gameplay core mechanics."""

    # Load assets.
    ORBIT_IMG = games.load_image(
        filename="./assets/graphics/orbit.png",
        transparent=False
    )

    # Set up handy constants.
    TEXT_HEIGHT = 25

    def __init__(self):
        # View starter help screen.
        self.display_help()

        # This defines level number and it's difficulty.
        # Look up advance() below for details.
        self.depth = 0

        # Depth level text sprite init.
        self.depth_txt = games.Text(
            value=None,
            size=0,
            color=color.gray
        )

        # Asteroids per level collection.
        self.belt = []

        # Score and it's display.
        self.score = games.Text(
            value=0,
            size=20,
            color=color.gray,
            x=WINDOW_WIDTH-25,
            top=25,
            is_collideable=False
        )
        games.screen.add(self.score)

        # Construct spacecraft object
        # and add it to the screen.
        self.spacecraft = Spacecraft(
            x=SCREEN_WIDTH_CENTER,
            y=SCREEN_HEIGHT_CENTER,
            game=self
        )
        games.screen.add(self.spacecraft)

    # Allow the player to perform an actual gameplay -- level by level.
    def play(self):
        # Set up chosen background.
        games.screen.background = Game.ORBIT_IMG

        # Start particular level.
        self.advance()

    def advance(self):
        # Increment the level depth and it's difficulty.
        # Player gets more debris to shoot with each level iteration.
        self.depth += 1

        # Clear old depth number from the screen.
        games.screen.remove(self.depth_txt)

        # Update and display level number on the screen.
        self.depth_txt = games.Text(
            value=f"Depth: {self.depth}",
            size=25,
            color=color.gray,
            x=SCREEN_WIDTH_CENTER,
            y=Game.TEXT_HEIGHT,
            is_collideable=False
        )
        games.screen.add(self.depth_txt)

        for _ in range(self.depth):
            # Avoid spawning debris on the ship or close to it.
            MIN_SPAWN_BUFFER_PX = 300
            MAX_SPAWN_BUFFER_PX = 350

            x_shift = self.spacecraft.x + random.randint(MIN_SPAWN_BUFFER_PX, MAX_SPAWN_BUFFER_PX)
            y_shift = self.spacecraft.y + random.randint(MIN_SPAWN_BUFFER_PX, MAX_SPAWN_BUFFER_PX)

#            if random.randrange(2) == 0:
            new_debris = Debris(
                game=self,
                x=x_shift,
                y=y_shift,
                size=random.randint(Debris.MEDIUM, Debris.BIG)
            )
            games.screen.add(new_debris)
#            else:
#                new_tough_debris = ToughDebris(
#                        game=self,
#                        x=x_shift,
#                        y=y_shift,
#                        size=random.randint(ToughDebris.MEDIUM, ToughDebris.BIG),
#                )
#                games.screen.add(new_tough_debris)

    def display_help(self):
        Y_AXIS_ALIGNMENT = 320
        MESSAGES_INTERSPACE = 25

        y_position = Y_AXIS_ALIGNMENT + MESSAGES_INTERSPACE
        duration = 180

        title = games.Message(
            value="asteroblast v1.0",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        h = games.Message(
            value="[ h ] -- show this message",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        up = games.Message(
            value="[ up ] -- accelerate",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        down = games.Message(
            value="[ down  ] -- deccelerate",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        left = games.Message(
            value="[ left ] -- turn left",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        right = games.Message(
            value="[ right ] -- turn right",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        shoot = games.Message(
            value="[ space / f ] -- shoot",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        r = games.Message(
            value="[ r ] -- stop the craft",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        c = games.Message(
            value="[ c ] -- change controls",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        esc = games.Message(
            value="[ ESC ] -- quit",
            size=25,
            color=color.light_gray,
            left=25,
            y=y_position,
            lifetime=duration,
            is_collideable=False,
            after_death=None
        )
        y_position += MESSAGES_INTERSPACE
        duration += 2

        help_items = [title, h, up, down, left, right, shoot, r, c, esc]
        for item in help_items:
            games.screen.add(item)


def main():
    intro = StartScreen()

    # Run the actual game -- keep the screen running
    # by evoking the main loop.
    games.screen.mainloop()


if __name__ == "__main__":
    main()
