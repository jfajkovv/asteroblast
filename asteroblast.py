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

# Useful global assets.
DUMMY_PXL = games.load_image('./assets/graphics/dummy-pixel.png')
ORBIT_BACKGROUND = games.load_image(
    filename="./assets/graphics/orbit.png",
    transparent=False
)


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

    # Load assets.
    # All credit goes to:
    # https://freesound.org/people/timgormly/sounds/170144/
    SOUND = games.load_sound('./assets/sounds/170144__timgormly__8-bit-explosion2.wav')

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
        # Play explosion sound.
        Bumper.SOUND.play()

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


class SpacecraftExhaust(games.Animation):
    """Ship exhaust animation-overlapper."""

    # Load assets.
    ANIMATION_IMGS = [
        "./assets/graphics/exhaust-1.png",
        "./assets/graphics/exhaust-2.png"
    ]

    def __init__(self, craft_x, craft_y, craft_angle, ship_x_vel, ship_y_vel):
        # Object image representation shall spawn itself at the spacecraft.
        x = craft_x
        y = craft_y
        angle = craft_angle

        # In order to create the illusion, exhaust animation shall move onwards
        # just like the ship itself.
        dx = ship_x_vel
        dy = ship_y_vel

        # Appeal to the games.Animation constructor in order
        # to set up frames and call upon coordinates.
        super(SpacecraftExhaust, self).__init__(
            images=SpacecraftExhaust.ANIMATION_IMGS,
            x=x,
            y=y,
            angle=angle,
            dx=dx,
            dy=dy,
            # Configure animation FPS.
            repeat_interval=1,
            # Set how many times animation shall display itself.
            n_repeats=1,
            is_collideable=False,
        )


class SpacecraftTurnAround(games.Animation):
    """Craft's turning around animation sequence"""

    # Load assets.
    ANIMATION_IMGS = [
        "./assets/graphics/qturn-anim-1.png",
        "./assets/graphics/qturn-anim-2.png",
        "./assets/graphics/qturn-anim-3.png",
        "./assets/graphics/qturn-anim-4.png",
        "./assets/graphics/qturn-anim-5.png",
        "./assets/graphics/qturn-anim-6.png"
    ]

    def __init__(self, craft_x, craft_y, craft_angle, craft_x_vel, craft_y_vel):
        # Object image representation shall spawn itself at the spacecraft.
        x = craft_x
        y = craft_y
        angle = craft_angle

        # In order to create the illusion, exhaust animation shall move onwards
        # just like the ship itself.
        dx = craft_x_vel
        dy = craft_y_vel

        # Appeal to the games.Animation constructor in order
        # to set up frames and call upon coordinates.
        super(SpacecraftTurnAround, self).__init__(
            images=SpacecraftTurnAround.ANIMATION_IMGS,
            x=x,
            y=y,
            angle=angle,
            dx=dx,
            dy=dy,
            # Configure animation FPS.
            repeat_interval=5,
            # Set how many times animation shall display itself.
            n_repeats=1,
            is_collideable=False,
        )


class Debris(ScreenWrapper):
    """Space rock -- enemy in the gameplay. An asteroid to be shot."""

    VELOCITY = 3  # The actual speed factor.
    CRASH_SPAWNS = 2  # Number of pieces to spawn after crash.

    # Asteroids classification constants.
    SMALL = 1
    MEDIUM = 2
    BIG = 3

    # Load assets.
    ASTEROID_IMAGES = {
        SMALL: games.load_image('./assets/graphics/debris-small-tier-1.png'),
        MEDIUM: games.load_image('./assets/graphics/debris-medium-tier-1.png'),
        BIG: games.load_image('./assets/graphics/debris-big-tier-1.png')
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
#        if not self.game.belt:
            # ... appeal to the Game class and it's advance method
            # in order to get to higher level.
#            self.game.advance()


class ToughDebris(Debris):
    """Space rock -- enemy in the gameplay. An asteroid to be shot. Tough version."""

    VELOCITY = 3  # The actual speed factor.
    CRASH_SPAWNS = 2  # Number of pieces to spawn after crash.

    # Asteroids classification constants.
    SMALL = 1
    MEDIUM = 2
    BIG = 3

    # Load assets.
    TOUGH_ASTEROID_IMAGES = {
        SMALL: games.load_image('./assets/graphics/debris-small-tier-2.png'),
        MEDIUM: games.load_image('./assets/graphics/debris-medium-tier-2.png'),
        BIG: games.load_image('./assets/graphics/debris-big-tier-2.png')
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
#        if not self.game.belt:
            # ... appeal to the Game class and it's advance method
            # in order to get to higher level.
#            self.game.advance()


class SuperToughDebris(ToughDebris):
    """Space rock -- enemy in the gameplay. An asteroid to be shot. Super tough version."""

    VELOCITY = 3  # The actual speed factor.
    CRASH_SPAWNS = 2  # Number of pieces to spawn after crash.

    # Asteroids classification constants.
    SMALL = 1
    MEDIUM = 2
    BIG = 3

    # Load assets.
    SUPER_TOUGH_ASTEROID_IMAGES = {
        SMALL: games.load_image('./assets/graphics/debris-small-tier-3.png'),
        MEDIUM: games.load_image('./assets/graphics/debris-medium-tier-3.png'),
        BIG: games.load_image('./assets/graphics/debris-big-tier-3.png')
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
#        if not self.game.belt:
            # ... appeal to the Game class and it's advance method
            # in order to get to higher level.
#            self.game.advance()


class Blast(games.Animation, Bumper):
    """A projectile. Spacecraft's blaster weapon system. Also has visual effect."""

    SPAWN_BUFFER_PX = 60  # Spawn distance from the ship.
    VELOCITY_FACTOR = 10  # An actual speed factor.
    BLAST_LIFETIME = 30  # Blast lifetime duration.

    # Load assets.
    ANIMATION_IMGS = [
        "./assets/graphics/blast-bounce-1.png",
        "./assets/graphics/blast-bounce-2.png",
        "./assets/graphics/blast-bounce-3.png",
        "./assets/graphics/blast-bounce-4.png",
    ]

    # All credit goes to:
    # https://freesound.org/people/colmmullally/sounds/462220/
    SOUND = games.load_sound('./assets/sounds/462220__colmmullally__zap.wav')

    def __init__(self, craft_x, craft_y, craft_angle):
        # Play projectile sound.
        Blast.SOUND.play()

        # Object animation representation shall spawn itself in front of the spacecraft.
        # Projectile position is calculated similarly to the Spacecraft class method.
        # The only difference is the shift in pixels by adding SPAWN_BUFFER_PX value.
        x = craft_x + Blast.SPAWN_BUFFER_PX * math.sin(math.radians(craft_angle))
        y = craft_y + Blast.SPAWN_BUFFER_PX * -math.cos(math.radians(craft_angle))
        angle = craft_angle

        # Projectile shall fly freely onwards from shooting spot.
        # Again, the movement calculation is along the x, y coordinate system --
        # crunched similarly to the Spaceship positioning method.
        dx = Blast.VELOCITY_FACTOR * math.sin(math.radians(craft_angle))
        dy = Blast.VELOCITY_FACTOR * -math.cos(math.radians(craft_angle))

        # Appeal to the ScreenWrapper constructor in order
        # to set up the image and call upon coordinates.
        super(Blast, self).__init__(
            images=Blast.ANIMATION_IMGS,
            x=x,
            y=y,
            angle=angle,
            dx=dx,
            dy=dy,
            # Configure animation FPS.
            repeat_interval=5,
            # Set how many times animation shall display itself.
            n_repeats=5,
            is_collideable=True,
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


class BlasterViewfinder(games.Sprite):
    """Spacecraft's aim assistance."""

    # Load assets.
    IMG = games.load_image("./assets/graphics/viewfinder-gray.png")

    def __init__(self, craft_x, craft_y, craft_angle):
        # Appeal to the games.Sprite constructor in order
        # to set up the image and call upon coordinates.
        super(BlasterViewfinder, self).__init__(
            image=BlasterViewfinder.IMG,
            is_collideable=False
        )


class Spacecraft(Bumper):
    """An actual player."""

    TURN_FACTOR = 3  # Turn angle factor.
    TURN_AROUND_DELAY = 25  # Time unit to prevent overlapping turnings around of the ship.
    VELOCITY_FACTOR = 0.1  # An actual speed factor.
    VELOCITY_MAX = 4  # Top speed limit.
    REVERSE_PULL_FACTOR = 0.07  # An actual reverse speed factor.
    BLASTER_DELAY = 30  # Time unit until next shot.
    VIEWFINDER_DISPLAY_BUFFER = 150  # Blaster viewfinder display distance from the craft.
    VIEWFINDER_DISPLAY_DELAY = 10  # Time unit to slow down viewfinder toggle.
    COOMETER_DISPLAY_DELAY = 15  # Time unit to slow down coordinates display refresh.

    # Load assets.
    SPACECRAFT_IMG = games.load_image("./assets/graphics/spacecraft-1.png")

    # All credit goes to:
    # https://freesound.org/people/BloodPixelHero/sounds/572623/
    SOUND = games.load_sound('./assets/sounds/572623__bloodpixelhero__spaceship-flight.wav')

    def __init__(self, game, x, y):
        # Appeal to the Bumper constructor in order
        # to set up the image and call upon coordinates.
        super(Spacecraft, self).__init__(
            image=Spacecraft.SPACECRAFT_IMG,
            x=x,
            y=y,
            is_collideable=True
        )

        self.game = game
        self.blaster_cooldown = 0
        self.coordinates_txt = games.Text(
            value=None,
            size=0,
            color=color.gray
        )

        self.show_viewfinder()
        self.viewfinder_on = True
        self.viewfinder_cooldown = 0

        self.coometer_cooldown = 0
        self.turn_around_delay = 0

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

        # Quickly turn the ship by 180 degrees via T KEY.
        if games.keyboard.is_pressed(games.K_t) and self.turn_around_delay == 0:

            new_turn_around = SpacecraftTurnAround(
                craft_x=self.x,
                craft_y=self.y,
                craft_angle=self.angle,
                craft_x_vel=self.dx,
                craft_y_vel=self.dy
            )
            games.screen.add(new_turn_around)

            self.turn_around()
            self.turn_around_delay = Spacecraft.TURN_AROUND_DELAY

        # Delay consecutive turns so they won't overlap.
        if self.turn_around_delay:
            self.turn_around_delay -= 1

        # Propel ship forward.
        if games.keyboard.is_pressed(games.K_UP):
            # Play acceleration sound.
            Spacecraft.SOUND.play()

            # The trick is to shift the craft along coordinate system:
            # using math sine and cosine functions here to determine the exact placement;
            # the actual angle of the sprite has to be converted from degrees to radians,
            # because superwires uses degrees and math trigonometric functions are running
            # on radians;
            # speed is incremented by the VELOCITY_FACOTR constant via UP KEY.
            self.dx += Spacecraft.VELOCITY_FACTOR * math.sin(math.radians(self.angle))
            self.dy += Spacecraft.VELOCITY_FACTOR * -math.cos(math.radians(self.angle))

            # Display exhaust animation.
            new_exhaust_anim = SpacecraftExhaust(
                craft_x=self.x,
                craft_y=self.y,
                craft_angle=self.angle,
                ship_x_vel=self.dx,
                ship_y_vel=self.dy
            )
            games.screen.add(new_exhaust_anim)

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

        # If coordinates timer is 0...
        if self.coometer_cooldown == 0:
            # ...clear coordinates display (keep it updated)...
            self.remove_coordinates()
            # ...show spacecraft coordinate speedometer.
            self.coordinates_txt = games.Text(
                value=f"[ dx: {self.dx} dy: {self.dy} ]",
                size=20,
                color=color.gray,
                x=SCREEN_WIDTH_CENTER,
                y=575,
                is_collideable=False
            )
            games.screen.add(self.coordinates_txt)
            self.coometer_cooldown = Spacecraft.COOMETER_DISPLAY_DELAY

        # Keep coordinates timer synchro.
        if self.coometer_cooldown:
            self.coometer_cooldown -= 1

        # Evoke help screen layer via H KEY.
        if games.keyboard.is_pressed(games.K_h):
            self.game.display_help()

        # Toggle viewfinder on/off.
        if games.keyboard.is_pressed(games.K_v) and self.viewfinder_cooldown == 0:
            if self.viewfinder_on:
                self.remove_viewfinder()
                self.viewfinder_on = False
            else:
                self.show_viewfinder()
                self.viewfinder_on = True

            self.viewfinder_cooldown = Spacecraft.VIEWFINDER_DISPLAY_DELAY

        # Mainloop reacts too quickly, so this is for slowing down
        # game's reaction to viewfinder toggle key.
        if self.viewfinder_cooldown:
            self.viewfinder_cooldown -= 1

        # Calibrate viewfinder assistance so it moves with the craft.
        self.viewfinder.angle = self.angle
        self.viewfinder.x = self.x + Spacecraft.VIEWFINDER_DISPLAY_BUFFER * math.sin(math.radians(self.angle))
        self.viewfinder.y = self.y + Spacecraft.VIEWFINDER_DISPLAY_BUFFER * -math.cos(math.radians(self.angle))

        # If there are no space rocks left...
        if not self.game.belt:
            # ... appeal to the Game class and it's advance method
            # in order to get to higher level.
            self.game.advance()

    # Velocity is regulated via update() method itself -- the craft cannot go faster
    # than value specified in VELOCITY_MAX constant.
    # Basically these two lines are picking the velocity factor between:
    # 0, which is game starting value -
    # and 4, which is max speed (VELOCITY_MAX).
    # Everything happens in terms of (x, y) coordinate system.
    def regulate_velocity(self):
        self.dx = min(max(self.dx, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)
        self.dy = min(max(self.dy, -Spacecraft.VELOCITY_MAX), Spacecraft.VELOCITY_MAX)

    def show_viewfinder(self):
        self.viewfinder = BlasterViewfinder(craft_x=self.x, craft_y=self.y, craft_angle=self.angle)
        games.screen.add(self.viewfinder)

    def turn_around(self):
        self.angle += 180

    def remove_viewfinder(self):
        games.screen.remove(self.viewfinder)

    def remove_coordinates(self):
        games.screen.remove(self.coordinates_txt)

    def clear_screen_data(self):
        # Remove gameplay components.
        games.screen.remove(self.game.depth_txt)
        games.screen.remove(self.game.score)
        self.remove_viewfinder()
        self.remove_coordinates()

    def die(self):
        # Inherit all die() functionality.
        super(Spacecraft, self).die()
        self.clear_screen_data()

        ending = EndingScreen(
            final_score=self.game.score.value,
            reached_depth=self.game.depth,
            debris_left=self.game.belt
        )
        games.screen.add(ending)


class Gameplay(object):
    """Gameplay core mechanics."""

    # Set up handy constants.
    TEXT_HEIGHT = 25

    # Load assets.

    # All credit goes to: PUBLIC DOMAIN.
    ADVANCE_SOUND = games.load_sound('./assets/sounds/level-advance.wav')

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
        games.screen.background = ORBIT_BACKGROUND

        # Start particular level.
        self.advance()

    # Proceed to the next level.
    def advance(self):
        # Play level adavnce sound.
        Gameplay.ADVANCE_SOUND.play()

        # Clear old depth number from the screen.
        games.screen.remove(self.depth_txt)

        # Increment the level depth and it's difficulty.
        # Player gets more debris to shoot with each level iteration.
        self.depth += 1

        # Update and display level number on the screen.
        self.depth_txt = games.Text(
            value=f"Depth: {self.depth}",
            size=25,
            color=color.gray,
            x=SCREEN_WIDTH_CENTER,
            y=Gameplay.TEXT_HEIGHT,
            is_collideable=False
        )
        games.screen.add(self.depth_txt)

        for _ in range(self.depth):
            # Avoid spawning debris on the ship or close to it.
            MIN_SPAWN_BUFFER_PX = 300
            MAX_SPAWN_BUFFER_PX = 350

            x_shift = self.spacecraft.x + random.randint(MIN_SPAWN_BUFFER_PX, MAX_SPAWN_BUFFER_PX)
            y_shift = self.spacecraft.y + random.randint(MIN_SPAWN_BUFFER_PX, MAX_SPAWN_BUFFER_PX)

            # Tier 3 debris spawns very rarely...
            if random.randrange(20) == 0:
                new_super_tough_debris = SuperToughDebris(
                    game=self,
                    x=x_shift,
                    y=y_shift,
                    size=random.randint(SuperToughDebris.MEDIUM, SuperToughDebris.BIG)
                )
                games.screen.add(new_super_tough_debris)
            # Tier 2 debris sprawns just rarely...
            elif random.randrange(10) == 0:
                new_tough_debris = ToughDebris(
                        game=self,
                        x=x_shift,
                        y=y_shift,
                        size=random.randint(ToughDebris.MEDIUM, ToughDebris.BIG),
                )
                games.screen.add(new_tough_debris)
            else:
            # In any other case, just sprawn normal asteroids.
                new_debris = Debris(
                    game=self,
                    x=x_shift,
                    y=y_shift,
                    size=random.randint(Debris.MEDIUM, Debris.BIG)
                )
                games.screen.add(new_debris)

    # Show help screen.
    def display_help(self):
        Y_AXIS_ALIGNMENT = 320
        MESSAGES_INTERSPACE = 25

        y_position = Y_AXIS_ALIGNMENT + MESSAGES_INTERSPACE
        duration = 180

        title_msg = games.Message(
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

        help_msg = games.Message(
            value="[h] -- show this message",
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

        up_msg = games.Message(
            value="[up] -- accelerate",
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

        down_msg = games.Message(
            value="[down] -- deccelerate",
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

        left_msg = games.Message(
            value="[left] -- turn left",
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

        right_msg = games.Message(
            value="[right] -- turn right",
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

        shoot_msg = games.Message(
            value="[space] / [f] -- shoot",
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

        viewfinder_msg = games.Message(
            value="[v] -- toggle viewfinder on/off",
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

        stop_msg = games.Message(
            value="[r] -- stop the craft",
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

        esc_msg = games.Message(
            value="[ESC] -- quit",
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

        help_items = [title_msg, help_msg, up_msg, down_msg, left_msg, right_msg, shoot_msg, viewfinder_msg, stop_msg, esc_msg]
        for item in help_items:
            games.screen.add(item)


class IntroScreen(games.Sprite):
    """Asteroblast welcome screen."""

    def __init__(self):
        # The image parameter is necessary for games.Sprite creation,
        # but it's totally unnecessary in such usage context.
        super(IntroScreen, self).__init__(
            image=DUMMY_PXL,
            is_collideable=False
        )

        # Set up chosen background.
        games.screen.background = ORBIT_BACKGROUND

        # Create and view game title.
        self.logo_txt = games.Text(
            value="asteroblast",
            size=40,
            color=color.gray,
            x=SCREEN_WIDTH_CENTER,
            y=SCREEN_HEIGHT_CENTER-50,
            is_collideable=False
        )
        games.screen.add(self.logo_txt)

        # Create and view help hint key.
        self.help_text = games.Text(
            value="you can see [h]elp chart while in game",
            size=30,
            color=color.light_gray,
            x=SCREEN_WIDTH_CENTER,
            y=SCREEN_HEIGHT_CENTER,
            is_collideable=False
        )
        games.screen.add(self.help_text)

        # Create and view game starter key prompt.
        self.start_txt = games.Text(
            value="[s]tart",
            size=35,
            color=color.light_gray,
            x=SCREEN_WIDTH_CENTER-150,
            y=SCREEN_HEIGHT_CENTER+150,
            is_collideable=False
        )
        games.screen.add(self.start_txt)

        # Create and view game exit key prompt.
        self.quit_txt = games.Text(
            value="[q]uit",
            size=35,
            color=color.light_gray,
            x=SCREEN_WIDTH_CENTER+150,
            y=SCREEN_HEIGHT_CENTER+150,
            is_collideable=False
        )
        games.screen.add(self.quit_txt)

    # Check for important object events in real time.
    def update(self):
        # S KEY starts the game (intro screen is cleared beforehand).
        if games.keyboard.is_pressed(games.K_s):
            self.clear_start_screen()

            # Create Game instance.
            asteroblast = Gameplay()
            # Defend these skies!
            asteroblast.play()

        # Q simply quits the game and closes the program.
        if games.keyboard.is_pressed(games.K_q):
            games.screen.quit()

    # Screen shall be cleared and dummy pixel removed before game start.
    def clear_start_screen(self):
        games.screen.remove(self.logo_txt)
        games.screen.remove(self.start_txt)
        games.screen.remove(self.help_text)
        games.screen.remove(self.quit_txt)

        self.destroy()


class EndingScreen(games.Sprite):
    """Asteroblast replay/quit screen."""

    def __init__(self, debris_left, final_score=1, reached_depth=1):
        # The image parameter is necessary for games.Sprite creation,
        # but it's totally unnecessary in such usage context.
        super(EndingScreen, self).__init__(
            image=DUMMY_PXL,
            is_collideable=False
        )

        self.final_score = final_score
        self.reached_depth = reached_depth
        self.debris_left = debris_left

        # Create and view game over text.
        self.game_over_txt = games.Text(
            value="GAME OVER",
            size=50,
            color=color.gray,
            x=SCREEN_WIDTH_CENTER,
            y=SCREEN_HEIGHT_CENTER-50,
            is_collideable=False
        )
        games.screen.add(self.game_over_txt)

        # Create and view final score.
        self.final_score_txt = games.Text(
            value=f"final score: {self.final_score}",
            size=30,
            color=color.yellow,
            x=SCREEN_WIDTH_CENTER,
            y=SCREEN_HEIGHT_CENTER,
            is_collideable=False
        )
        games.screen.add(self.final_score_txt)

        # Create and view reached depth.
        self.depth_reached_txt = games.Text(
            value=f"depth reached: {self.reached_depth}",
            size=30,
            color=color.yellow,
            x=SCREEN_WIDTH_CENTER,
            y=SCREEN_HEIGHT_CENTER+30,
            is_collideable=False
        )
        games.screen.add(self.depth_reached_txt)

        # Create and view play again key prompt.
        self.replay_txt = games.Text(
            value="play [a]gain",
            size=35,
            color=color.light_gray,
            x=SCREEN_WIDTH_CENTER-150,
            y=SCREEN_HEIGHT_CENTER+150,
            is_collideable=False
        )
        games.screen.add(self.replay_txt)

        # Create and view game exit key prompt.
        self.quit_txt = games.Text(
            value="[q]uit",
            size=35,
            color=color.light_gray,
            x=SCREEN_WIDTH_CENTER+150,
            y=SCREEN_HEIGHT_CENTER+150,
            is_collideable=False
        )
        games.screen.add(self.quit_txt)

    # Check for important object events in real time.
    def update(self):
        # A KEY starts the game anew (ending screen is cleared beforehand).
        if games.keyboard.is_pressed(games.K_a):
            self.clear_ending_screen()

            for rock in self.debris_left:
                games.screen.remove(rock)

            # Create Game instance.
            asteroblast = Gameplay()
            # Defend these skies!
            asteroblast.play()

        if games.keyboard.is_pressed(games.K_q):
            games.screen.quit()

    # Screen shall be cleared and dummy pixel removed before game start.
    def clear_ending_screen(self):
        games.screen.remove(self.game_over_txt)
        games.screen.remove(self.final_score_txt)
        games.screen.remove(self.depth_reached_txt)
        games.screen.remove(self.replay_txt)
        games.screen.remove(self.quit_txt)

        self.destroy()


class GameHandler(games.Sprite):
    """Intro screen and gameplay wrapper."""

    def __init__(self):
        self.intro = IntroScreen()
        games.screen.add(self.intro)


def main():
    game = GameHandler()
    # Run the actual game -- keep the screen running
    # by evoking the main loop.
    games.screen.mainloop()


if __name__ == "__main__":
    main()
