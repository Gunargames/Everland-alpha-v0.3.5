from ursinanetworking import *
import uuid
Client = UrsinaNetworkingClient("localhost", 25565)
my_id = str(uuid.uuid4())
other_players = {}

def handle_player_position(message_type, msg):
    if message_type == 'player_position':
        print(f"Received player_position: {msg}")
        client_id = msg['client']
        pos = msg['position']
        if client_id == my_id:
            print("Ignoring own position update.")
            return  # Don't update self
        if client_id not in other_players:
            print(f"Creating new remote player entity for {client_id} at {pos}")
            other_players[client_id] = Entity(model='cube', color=color.red, scale=1, position=Vec3(*pos))
        else:
            print(f"Updating position for remote player {client_id} to {pos}")
            other_players[client_id].position = Vec3(*pos)
    elif message_type == 'player_disconnect':
        client_id = msg['client']
        if client_id in other_players:
            print(f"Removing remote player entity for {client_id}")
            destroy(other_players[client_id])
            del other_players[client_id]

Client.on_message_received = handle_player_position
from ursina import *
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.trail_renderer import TrailRenderer
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.conversation import Conversation
from ursina.prefabs.health_bar import HealthBar
from main_menu1 import MainMenu
import math
import pygame
import random


# Initialize the game

clock = pygame.time.Clock


app = Ursina()


player = FirstPersonController(collider='box', model='cube', color=color.white, position=Vec3(0, -17, 0))
player_damage_timer = 0


king_has_died = False

window.vsync = False  # Disable VSync to avoid interference





# shops an things

class human(Entity):
    def __init__(self, player=None, position=(0,0,0), health=100, model='cube', color=color.red, name='mob'):
        super().__init__(
            model=model,
            color=color,
            position=position,
            collider='box',
            scale=1,
            name=name
        )
        self.health = health
        self.max_health = health
        self.is_alive = True
        self.speed = 4
        self.direction = Vec3(0, 0, 0)
        self.player = player  # Optional reference to player

        self.wander_timer = 0
        self.change_direction()

    def update(self):
        if not self.is_alive:
            return

        if king_has_died and self.player:
            # Chase the player
            direction = (self.player.position - self.position).normalized()
            self.position += direction * self.speed * time.dt

            if direction.length() > 0:
                angle = math.degrees(math.atan2(direction.x, direction.z))
                self.rotation_y = angle
        else:
            #  Wander normally
            self.wander_timer -= time.dt
            if self.wander_timer <= 0:
                self.change_direction()

            self.position += self.direction * self.speed * time.dt

            if self.direction.length() > 0:
                angle = math.degrees(math.atan2(self.direction.x, self.direction.z))
                self.rotation_y = angle

    def change_direction(self):
        angle = random.uniform(0, 360)
        self.direction = Vec3(math.sin(math.radians(angle)), 0, math.cos(math.radians(angle)))
        self.wander_timer = random.uniform(2, 5)

    def take_damage(self, amount):
        if not self.is_alive:
            return

        self.health -= amount
        print(f"{self.name} took {amount} damage. Health: {self.health}")

        Audio('audio/young-man-being-hurt-95628.mp3')

        if self.health <= 0:
            self.die()

    def die(self):
        death_sounds = [
            'audio/male-death-scream-horror-352706.mp3',
            'audio/woman-scream-136558.mp3'
        ]
        chosen_sound = random.choice(death_sounds)
        Audio(chosen_sound, volume=2.0)
        print(f"{self.name} has died.")
        self.is_alive = False
        destroy(self)

class king(Entity):
    def __init__(self, position=(0,0,0), health=100, model='cube', color=color.gold, name='mob'):
        super().__init__(
            model='statue',
            color=color,
            position=position,
            collider='box',
            scale=1,
            name=name
        )
        self.health = health
        self.max_health = health
        self.is_alive = True
        self.speed = 4

    def update(self):
        if not self.is_alive:
            return

    def take_damage(self, amount):
        if not self.is_alive:
            return

        self.health -= amount
        print(f"{self.name} took {amount} damage. Health: {self.health}")

        if self.health <= 0:
            self.die()

    def die(self):
        global king_has_died
        king_has_died = True  # Trigger the global flag
        Audio('audio/male-death-scream-horror-352706.mp3', volume=2.0)
        print(f"{self.name} has died.")
        self.is_alive = False
        destroy(self)

class coal(Entity):
    def __init__(self, position=(0,0,0), health=3, model='cube', color=color.black, name='coal'):
        super().__init__(
            model='coal_rock',  # Replace with your actual coal model name
            color=color,
            position=position,
            collider='box',
            scale=0.4,
            name=name
        )
        self.health = health
        self.max_health = health
        self.is_alive = True

    def update(self):
        if not self.is_alive:
            return
        # No movement logic needed for coal

    def take_damage(self, amount):
        if not self.is_alive:
            return

        self.health -= amount
        print(f"{self.name} took {amount} damage. Health: {self.health}")

        if self.health <= 0:
            self.die()

    def die(self):
        print(f"{self.name} has been mined.")
        self.is_alive = False
        destroy(self)

class bunny(Entity):
    def __init__(self, position=(0,0,0), health=100, model='cube', color=color.orange, name='mob'):
        super().__init__(
            model='bunny1',
            color=color,
            position=position,
            collider='box',
            scale=1,
            name=name
        )
        self.health = health
        self.max_health = health
        self.is_alive = True
        self.speed = 4
        self.direction = Vec3(0, 0, 0)

        # Start wandering
        self.wander_timer = 0
        self.change_direction()

    def update(self):
        if not self.is_alive:
            return

        self.wander_timer -= time.dt
        if self.wander_timer <= 0:
            self.change_direction()

        self.position += self.direction * self.speed * time.dt

        # Rotate to face movement direction
        if self.direction.length() > 0:
            angle = math.degrees(math.atan2(self.direction.x, self.direction.z))
            self.rotation_y = angle

    def change_direction(self):
        angle = random.uniform(0, 360)
        self.direction = Vec3(math.sin(math.radians(angle)), 0, math.cos(math.radians(angle)))
        self.wander_timer = random.uniform(2, 5)  # change direction every 2–5 seconds

    def take_damage(self, amount):
        if not self.is_alive:
            return

        self.health -= amount
        print(f"{self.name} took {amount} damage. Health: {self.health}")

        if self.health <= 0:
            self.die()

    def die(self):
        print(f"{self.name} has died.")
        self.is_alive = False
        destroy(self)

class horse(Entity):
    def __init__(self, position=(0,0,0), health=100, model='cube', color=color.brown, name='mob'):
        super().__init__(
            model=model,
            color=color,
            position=position,
            collider='box',
            scale=1.5,
            name=name
        )
        self.health = health
        self.max_health = health
        self.is_alive = True
        self.speed = 2
        self.direction = Vec3(0, 0, 0)

        # Start wandering
        self.wander_timer = 0
        self.change_direction()

    def update(self):
        if not self.is_alive:
            return

        self.wander_timer -= time.dt
        if self.wander_timer <= 0:
            self.change_direction()

        self.position += self.direction * self.speed * time.dt

        # Rotate to face movement direction
        if self.direction.length() > 0:
            angle = math.degrees(math.atan2(self.direction.x, self.direction.z))
            self.rotation_y = angle

    def change_direction(self):
        angle = random.uniform(0, 360)
        self.direction = Vec3(math.sin(math.radians(angle)), 0, math.cos(math.radians(angle)))
        self.wander_timer = random.uniform(2, 5)  # change direction every 2–5 seconds

    def take_damage(self, amount):
        if not self.is_alive:
            return

        self.health -= amount
        print(f"{self.name} took {amount} damage. Health: {self.health}")

        if self.health <= 0:
            self.die()

    def die(self):
        print(f"{self.name} has died.")
        self.is_alive = False
        destroy(self)

class bear(Entity):
    def __init__(self, position=(0,0,0), health=100, model='cube', color=color.orange, name='mob'):
        super().__init__(
            model=model,
            color=color,
            position=position,
            collider='box',
            scale=1,
            name=name
        )
        self.health = health
        self.max_health = health
        self.is_alive = True
        self.speed = 2
        self.direction = Vec3(0, 0, 0)

        # Start wandering
        self.wander_timer = 0
        self.change_direction()

    def update(self):
        if not self.is_alive:
            return

        self.wander_timer -= time.dt
        if self.wander_timer <= 0:
            self.change_direction()

        self.position += self.direction * self.speed * time.dt

        # Rotate to face movement direction
        if self.direction.length() > 0:
            angle = math.degrees(math.atan2(self.direction.x, self.direction.z))
            self.rotation_y = angle

    def change_direction(self):
        angle = random.uniform(0, 360)
        self.direction = Vec3(math.sin(math.radians(angle)), 0, math.cos(math.radians(angle)))
        self.wander_timer = random.uniform(2, 5)  # change direction every 2–5 seconds

    def take_damage(self, amount):
        if not self.is_alive:
            return

        self.health -= amount
        print(f"{self.name} took {amount} damage. Health: {self.health}")

        if self.health <= 0:
            self.die()

    def die(self):
        print(f"{self.name} has died.")
        self.is_alive = False
        destroy(self)

class wizard(Entity):
    def __init__(self, position=(0,0,0), health=100, model='cube', name='mob'):
        super().__init__(
            model=model,
            color=color,
            position=position,
            collider='box',
            scale=1,
            name=name
        )
        self.health = health
        self.max_health = health
        self.is_alive = True
        self.speed = 2
        self.direction = Vec3(0, 0, 0)

        # Wandering behavior
        self.wander_timer = 0
        self.change_direction()

        # Combat behavior
        self.target = None
        self.attack_range = 3.0
        self.attack_cooldown = 1.5
        self.attack_timer = 0
        self.damage = 10

    def set_target(self, target):
        self.target = target

    def update(self):
        if not self.is_alive:
            return

        self.attack_timer -= time.dt

        if self.target and self.target.is_alive:
            distance = self.distance_xz(self.position, self.target.position)
            if distance <= self.attack_range:
                self.direction = Vec3(0, 0, 0)  # Stop moving
                self.attack()
            else:
                # Move toward the target
                direction_to_target = (self.target.position - self.position).normalized()
                self.direction = Vec3(direction_to_target.x, 0, direction_to_target.z)
        else:
            # Wander if no target
            self.wander_timer -= time.dt
            if self.wander_timer <= 0:
                self.change_direction()

        self.position += self.direction * self.speed * time.dt

        # Rotate to face movement direction
        if self.direction.length() > 0:
            angle = math.degrees(math.atan2(self.direction.x, self.direction.z))
            self.rotation_y = angle

    def change_direction(self):
        angle = random.uniform(0, 360)
        self.direction = Vec3(math.sin(math.radians(angle)), 0, math.cos(math.radians(angle)))
        self.wander_timer = random.uniform(2, 5)

    def take_damage(self, amount):
        if not self.is_alive:
            return

        self.health -= amount
        print(f"{self.name} took {amount} damage. Health: {self.health}")

        if self.health <= 0:
            self.die()

    def attack(self):
        if not self.target or not self.target.is_alive:
            return

        if self.attack_timer > 0:
            return  # still on cooldown

    def die(self):
        print(f"{self.name} has died.")
        Audio('audio/young-man-being-hurt-95628.mp3', volume=3)
        self.is_alive = False
        destroy(self)

    def distance_xz(self, pos1, pos2):
        return math.sqrt((pos1.x - pos2.x)**2 + (pos1.z - pos2.z)**2)

class goblin(Entity):
    def __init__(self, position=(0,0,0), health=100, model='cube', color=color.orange, name='mob'):
        super().__init__(
            model=model,
            color=color,
            position=position,
            collider='box',
            scale=2,
            name=name
        )
        self.health = health
        self.max_health = health
        self.is_alive = True
        self.speed = 2
        self.direction = Vec3(0, 0, 0)

        # Wandering behavior
        self.wander_timer = 0
        self.change_direction()

        # Combat behavior
        self.target = None
        self.attack_range = 3.0
        self.attack_cooldown = 1.5
        self.attack_timer = 0
        self.damage = 10

    def set_target(self, target):
        self.target = target

    def update(self):
        if not self.is_alive:
            return

        self.attack_timer -= time.dt

        if self.target and self.target.is_alive:
            distance = self.distance_xz(self.position, self.target.position)
            if distance <= self.attack_range:
                self.direction = Vec3(0, 0, 0)  # Stop moving
                self.attack()
            else:
                # Move toward the target
                direction_to_target = (self.target.position - self.position).normalized()
                self.direction = Vec3(direction_to_target.x, 0, direction_to_target.z)
        else:
            # Wander if no target
            self.wander_timer -= time.dt
            if self.wander_timer <= 0:
                self.change_direction()

        self.position += self.direction * self.speed * time.dt

        # Rotate to face movement direction
        if self.direction.length() > 0:
            angle = math.degrees(math.atan2(self.direction.x, self.direction.z))
            self.rotation_y = angle

    def change_direction(self):
        angle = random.uniform(0, 360)
        self.direction = Vec3(math.sin(math.radians(angle)), 0, math.cos(math.radians(angle)))
        self.wander_timer = random.uniform(2, 5)

    def take_damage(self, amount):
        if not self.is_alive:
            return

        self.health -= amount
        print(f"{self.name} took {amount} damage. Health: {self.health}")

        if self.health <= 0:
            self.die()

    def attack(self):
        if not self.target or not self.target.is_alive:
            return

        if self.attack_timer > 0:
            return  # still on cooldown

    def die(self):
        print(f"{self.name} has died.")
        Audio('audio/goblin-death-6729.mp3', volume=3)
        self.is_alive = False
        destroy(self)

    def distance_xz(self, pos1, pos2):
        return math.sqrt((pos1.x - pos2.x)**2 + (pos1.z - pos2.z)**2)
    

class goblin_king(Entity):
    global goblin_king1_is_alive
    def __init__(self, position=(0,0,0), health=10000, model='cube', entity_color=color.green, name='Goblin King'):
        super().__init__(
            model=model,
            color=entity_color,
            position=position,
            collider='box',
            scale=40,
            speed=2,
            name=name
        )
        self.health = health
        self.max_health = health
        self.is_alive = True
        self.speed = 2
        self.direction = Vec3(0, 0, 0)

        # Wandering behavior
        self.wander_timer = 0
        self.change_direction()

        # Combat behavior
        self.target = None
        self.attack_range = 3.0
        self.attack_cooldown = 1.5
        self.attack_timer = 0
        self.damage = 10

        # Random scream timer
        self.scream_timer = random.uniform(10, 15)

        # Health bar UI
        self.health_bar = Entity(
            parent=camera.ui,
            model='quad',
            color=color.red,
            scale=(0.8, 0.05),
            position=(0, 0.45),
            enabled=False
        )

        self.health_fill = Entity(
            parent=self.health_bar,
            model='quad',
            color=color.green,
            origin=(-0.5, 0),
            scale=(1, 1)
        )

        self.health_text = Text(
            text=self.name,
            parent=self.health_bar,
            position=(0, 0.1),
            origin=(0, 0),
            scale=1.5,
            color=color.white,
            enabled=False
        )

    def set_target(self, target):
        self.target = target

    def update(self):
        if not self.is_alive:
            return

        self.attack_timer -= time.dt
        self.scream_timer -= time.dt

        # Combat behavior
        if self.target and self.target.is_alive:
            distance = self.distance_xz(self.position, self.target.position)
            if distance <= self.attack_range:
                self.direction = Vec3(0, 0, 0)
                self.attack()
            else:
                direction_to_target = (self.target.position - self.position).normalized()
                self.direction = Vec3(direction_to_target.x, 0, direction_to_target.z)
        else:
            # Wander if no target
            self.wander_timer -= time.dt
            if self.wander_timer <= 0:
                self.change_direction()

        self.position += self.direction * self.speed * time.dt

        # Rotate to face movement direction
        if self.direction.length() > 0:
            angle = math.degrees(math.atan2(self.direction.x, self.direction.z))
            self.rotation_y = angle

        # Health bar visibility and update
        if self.target and self.distance_xz(self.position, self.target.position) <= 1000:
            self.health_bar.enabled = True
            self.health_text.enabled = True
            health_ratio = max(0, self.health / self.max_health)
            self.health_fill.scale_x = health_ratio
        else:
            self.health_bar.enabled = False
            self.health_text.enabled = False

        # Random scream behavior
        if self.scream_timer <= 0 and self.is_alive:
            Audio('audio/kaiju-growl-368659.mp3', volume=2)  # Replace with your actual scream file
            print(f"{self.name} lets out a terrifying scream!")
            self.scream_timer = random.uniform(10, 15)

    def change_direction(self):
        angle = random.uniform(0, 360)
        self.direction = Vec3(math.sin(math.radians(angle)), 0, math.cos(math.radians(angle)))
        self.wander_timer = random.uniform(2, 5)

    def take_damage(self, amount):
        if not self.is_alive:
            return

        self.health -= amount
        print(f"{self.name} took {amount} damage. Health: {self.health}")

        if self.health <= 0:
            self.die()

    def attack(self):
        if not self.target or not self.target.is_alive:
            return

        if self.attack_timer > 0:
            return

        distance = self.distance_xz(self.position, self.target.position)
        if distance <= self.attack_range:
            print(f"{self.name} attacks {self.target.name}!")
            self.target.take_damage(self.damage)
            self.attack_timer = self.attack_cooldown

    def die(self):
        print(f"{self.name} has died.")
        Audio('audio/monster-roar-slowed-reverb-368664.mp3', volume=3)
        self.is_alive = False
        goblin_king1_is_alive == False
        self.health_bar.enabled = False
        self.health_text.enabled = False
        destroy(self)

    def distance_xz(self, pos1, pos2):
        return math.sqrt((pos1.x - pos2.x)**2 + (pos1.z - pos2.z)**2)
               
# evil
king = king(model='statue', position=(-440, -61, 3000), name='Evil king')


# oh no!
goblin_king1 = goblin_king(model='goblin', position=(-4100, -60, -1200), name='goblin king')
goblin_king1_is_alive = True


goblin1 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin2 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin3 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin4 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin5 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin6 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin7 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin8 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin9 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')


mob1 = bunny(position=(-10, -60, -200), model='bunny1', name='bunny')
mob2 = bunny(position=(-10, -60, -180), model='bunny1', name='bunny')
mob3 = bunny(position=(-20, -60, -200), model='bunny1', name='bunny')

mob4 = bear(position=(-20, -60, -200), model='bear2', color=color.brown, name='bear')
mob5 = bear(position=(-20, -60, -200), model='bear2', color=color.brown, name='bear')
mob6 = bear(position=(-20, -60, -200), model='bear2', color=color.brown, name='bear')
mob7 = bear(position=(-20, -60, -200), model='bear2', color=color.brown, name='bear')

mob8 = bunny(position=(-10, -60, -200), model='bunny1', name='bunny')
mob9 = bunny(position=(-10, -60, -180), model='bunny1', name='bunny')
mob10 = bunny(position=(-20, -60, -200), model='bunny1', name='bunny')
mob11 = bunny(position=(-10, -60, -200), model='bunny1', name='bunny')
mob12 = bunny(position=(-10, -60, -180), model='bunny1', name='bunny')
mob13 = bunny(position=(-20, -60, -200), model='bunny1', name='bunny')
mob14 = bunny(position=(-10, -60, -200), model='bunny1', name='bunny')
mob15 = bunny(position=(-10, -60, -180), model='bunny1', name='bunny')
mob16 = bunny(position=(-20, -60, -200), model='bunny1', name='bunny')

mob4 = bear(position=(-3200, -17, 2000), model='bear2', color=color.brown, name='bear')
mob5 = bear(position=(-20, -60, -100), model='bear2', color=color.brown, name='bear')
mob6 = bear(position=(-20, -60, -100), model='bear2', color=color.brown, name='bear')
mob7 = bear(position=(-20, -60, -100), model='bear2', color=color.brown, name='bear')
mob4 = bear(position=(-20, -60, -100), model='bear2', color=color.brown, name='bear')
mob5 = bear(position=(-20, -60, -80), model='bear2', color=color.brown, name='bear')
mob6 = bear(position=(-20, -60, -80), model='bear2', color=color.brown, name='bear')
mob7 = bear(position=(-20, -60, -80), model='bear2', color=color.brown, name='bear')

goblin1 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin2 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin3 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin4 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin5 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin6 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin7 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin8 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin9 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin10 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin11 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin12 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin13 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin14 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin15 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin16 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin17 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin18 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin') 
goblin19 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin20 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin21 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin22 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin23 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin24 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin25 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin26 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')
goblin27 = goblin(model='goblin', position=(3110, -60, 1900), color=color.green, name='goblin')

villager2 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager3 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager4 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager5 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager6 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager7 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager8 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')

villager2 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager3 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager4 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager5 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager6 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager7 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')
villager8 = human(model='statue', position=(75, -61, -230), color=color.red, name='villager')

villager2 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager3 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager4 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager5 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager6 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager7 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager8 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager2 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager2 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager3 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager4 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager5 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager6 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager7 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager8 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager2 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager3 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager4 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager5 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager6 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager7 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager8 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager2 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager3 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager4 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager5 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager6 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager7 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager8 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager2 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager3 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager4 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager5 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager6 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager7 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager8 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager2 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager3 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager4 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager5 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager6 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager7 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')
villager8 = human(player=player, model='statue', position=(-400, -61, 3000), color=color.red, name='villager')


horse1 = horse(model='horse', position=(-1000, -59.5, 3000), name='horse')

# ore




def switch_to_bow():
    sword.enabled = False
    bow.enabled = True

def switch_to_sword():
    bow.enabled = False
    sword.enabled = True

# Attack state flag

def distance_3d(a, b):
    return ((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)**0.5

is_attacking = False

# Dummy enemies for demo
enemies = []
for i in range(1):
    enemy = Entity(
        model='target',
        position=Vec3(i -4, -60, -200),
        scale=1,
        parent=scene,
        collider='box',
        name='enemy_target'
    )
    enemy.health = 100
    enemies.append(enemy)

def sword_attack():
    Audio('audio/sword-sound-260274.mp3')
    for e in scene.entities:
        if hasattr(e, 'take_damage') and distance(e.position, player.position) < 2:
            e.take_damage(30)
    global is_attacking
    if is_attacking:
        return

    is_attacking = True

    sword.animate_rotation(Vec3(40, 0, 0), duration=0.1)
    invoke(lambda: sword.animate_rotation(Vec3(0, 0, 0), duration=0.1), delay=0.1)
    invoke(apply_area_damage, delay=0.2)
    invoke(lambda: unlock_attack(), delay=0.2)


def unlock_attack():
    global is_attacking
    is_attacking = False

def apply_area_damage():
    player_pos = camera.world_position
    damage_radius = 2

    for enemy in enemies:
        if not enemy.has_parent or not enemy.enabled:
            continue  # Skip entities not in the scene

        try:
            distance = distance_3d(player_pos, enemy.world_position)
            if distance <= damage_radius:
                enemy.health -= 10
                print(f"Hit enemy at {enemy.position}, health now {enemy.health}")
        except Exception as e:
            print(f"Error with enemy {enemy}: {e}")

def kill_enemy(enemy):
    print(f"Destroying enemy at {enemy.position}")
    destroy(enemy)
    if enemy in enemies:
        enemies.remove(enemy)
        enemy.visible = False


class achievement():
    def reactions(key):
        global jumping_achievement
        if key == 'space':
            jumping_achievement.visible == True

            invoke(setattr, jumping_achievement, 'visible', False, delay=6)
        if key == 'e' and distance(player.position, elder_miro.position) < 5:
            pass


class UnderwaterEffect(Entity):
    def __init__(self, blur_texture=None, fog_density=0.03, tint_color=color.rgba(50, 100, 255, 100), enabled=False):
        super().__init__()
        self.tint_color = tint_color
        self.fog_density = fog_density
        self.blur_texture = blur_texture
        self.blur_overlay = None
        self.active = False

        if enabled:
            self.enable()

    def enable(self):
        if self.active:
            return
        self.active = True
        window.fog_color = self.tint_color
        window.fog_density = self.fog_density
        camera.overlay_color = self.tint_color
        if self.blur_texture:
            self.blur_overlay = Entity(
                model='quad',
                texture=self.blur_texture,
                scale=2,
                color=color.rgba(255, 255, 255, 80),
                parent=camera.ui,
                z=-1
            )

    def disable(self):
        if not self.active:
            return
        self.active = False
        window.fog_density = 0
        camera.overlay_color = color.clear
        if self.blur_overlay:
            destroy(self.blur_overlay)
            self.blur_overlay = None

def shoot_arrow():
    Audio('audio/arrow-swish_03-306040.mp3')
    direction = camera.forward.normalized()

    arrow = Entity(
        model='arrow5',
        position=camera.world_position + direction * 1.5,
        scale=0.5,
        collider='box'
    )

    arrow.look_at(arrow.position + direction)
    arrow.speed = 50
    arrow.lifetime = 20
    arrow.birth_time = time.time()
    arrow.has_hit = False

    def update_arrow():
        if arrow.has_hit:
            return
  

        arrow.position += direction * time.dt * arrow.speed

        hit_info = arrow.intersects()

        if hit_info.hit:
            target = hit_info.entity
            if target and hasattr(target, 'take_damage') and target.is_alive:
                target.take_damage(50)
                arrow.has_hit = True


#            if hit_info.entity.name == 'enemy_target':

        elapsed = time.time() - arrow.birth_time
        remaining = max(0.1, arrow.lifetime - elapsed)
        invoke(lambda: destroy(arrow), delay=remaining)

    arrow.update = update_arrow

    # Only destroy if it never hits anything
    def destroy_if_not_hit():
        if not arrow.has_hit:
            destroy(arrow)

    invoke(destroy_if_not_hit, delay=arrow.lifetime)

def blast_ice():
    # Play ice blast sound
    Audio('audio/ice-blast.mp3')  # Replace with your actual sound file

    direction = camera.forward.normalized()

    # Create iceball entity
    ball = Entity(
        model='sphere',
        position=camera.world_position + direction * 1.5,
        scale=0.5,
        collider='box',
        color=color.cyan,
        shader=lit_with_shadows_shader,
        glow=0.5
    )

    ball.look_at(ball.position + direction)
    ball.speed = 25
    ball.lifetime = 4  # seconds
    ball.birth_time = time.time()
    ball.has_hit = False


    def update_ball():
        if ball.has_hit:
            return

        ball.position += direction * time.dt * ball.speed

        hit_info = ball.intersects()
        if hit_info.hit:
            target = hit_info.entity
            if target and hasattr(target, 'is_alive') and target.is_alive:
                ball.has_hit = True

                # Freeze logic for 5 seconds
                if hasattr(target, 'speed'):
                    target.original_speed = target.speed
                    target.speed = 0
                    print(f"{target.name} has been frozen for 5 seconds!")

                    def unfreeze():
                        if hasattr(target, 'original_speed'):
                            target.speed = target.original_speed
                            print(f"{target.name} has thawed.")

                    invoke(unfreeze, delay=5)

                # Ice impact effect scaled to target
                impact_scale = target.scale * 1.5 if hasattr(target, 'scale') else 5

                impact = Entity(
                    model='sphere',
                    position=ball.position,
                    scale=impact_scale,
                    texture='build/exe.win-amd64-3.13/Assets_for_Everland/Textures/ice.png',
                    shader=lit_with_shadows_shader,
                    rotation_y=90,
                    glow=10,
                    billboard=True
                )

                # Destroy the impact cube after 5 seconds
                invoke(lambda: destroy(impact), delay=5)

                destroy(ball)

        # Auto-destroy after lifetime
        elapsed = time.time() - ball.birth_time
        if elapsed > ball.lifetime:
            destroy(ball)

    ball.update = update_ball

    # Failsafe destroy
    invoke(lambda: destroy(ball), delay=ball.lifetime)

def blast_fire():
    # Play fire whoosh sound
    Audio('audio/short-fire-whoosh_1-317280.mp3')

    direction = camera.forward.normalized()

    # Create fireball entity
    ball = Entity(
        model='sphere',
        position=camera.world_position + direction * 1.5,
        scale=0.5,
        collider='box',
        color=color.orange,
        shader=lit_with_shadows_shader,
        glow=0.5
    )

    ball.look_at(ball.position + direction)
    ball.speed = 25
    ball.lifetime = 4  # seconds
    ball.birth_time = time.time()
    ball.has_hit = False



    def update_ball():
        if ball.has_hit:
            return

        ball.position += direction * time.dt * ball.speed

        hit_info = ball.intersects()
        if hit_info.hit:
            target = hit_info.entity
            if target and hasattr(target, 'take_damage') and target.is_alive:
                target.take_damage(500)
                ball.has_hit = True

                # Impact explosion
                Entity(
                    model='cube',
                    position=ball.position,
                    scale=5,
                    texture='build/exe.win-amd64-3.13/Assets_for_Everland/Textures/fireball.png',
                    shader=lit_with_shadows_shader,
                    rotation_y=90,
                    glow=10,
                    billboard=True,
                    duration=0.3
                )

                destroy(ball)

        # Auto-destroy after lifetime
        elapsed = time.time() - ball.birth_time
        if elapsed > ball.lifetime:
            destroy(ball)

    ball.update = update_ball

    # Failsafe destroy
    invoke(lambda: destroy(ball), delay=ball.lifetime)




# Player stats
HB1 = HealthBar(position=Vec2(-0.5, -0.4), value=100, scale_x=1)
HB1.bar.texture = 'build/exe.win-amd64-3.13/Assets_for_Everland/Textures/light-purple-pink-texture-with-colorful-hexagons-vector.jpg'
HB1.bar.color = color.white

gold_gates = Entity(model='gold gates', scale=6, position=(1000, 220, 3020), collider='mesh', color=color.gold)
cloud_land = Entity(model='could_lannd', scale=60, position=(1000, 200, 3000), collider='mesh', color=color.gray)
kingdom = Entity(model='kkingdom', scale=60, texture_scale=(60, 60), texture='Textures/House wall.jpeg', position=(-400, -60, 3000), double_sided=True, collider='mesh')
continent = Entity(model='ccontinent', scale=300, texture_scale=(60*2, 60*2), texture='Textures/Grasss.jpg', position=(0, -60, 4000), collider='mesh')
arrow_count = 20
volcano = Entity(model='volcano', texture='Textures/Rock.jpg', position=(-1000, -60, 600), scale=60, collider='mesh')
temple = Entity(model='temple', texture='Textures/House wall.jpeg', position=(-3500, -90, 1000), scale=5)
shrine_gem = Entity(model='gems', scale=2, color=color.green, collider='mesh', position=(3500, -73, 3000), rotation_y=-130)
shrine = Entity(model='shrine', scale=5, texture='Textures/House wall.jpeg', collider='mesh', position=(3500, -80, 3000), rotation_y=-130)
island = Entity(model='iisland', scale=60, texture='Textures/Grasss.jpg', collider='mesh', position=(1000, -60, 300), rotation_y=-130)
statue = Entity(model='statue', scale=60, texture='Textures/House wall.jpeg', collider='mesh', position=(1000, -60, 300), rotation_y=-130)
sword = Entity(model='sword oof doom', parent=camera, position=Vec3(0.5, -0.5, 1), scale=(0.2), origin_z=-5, enabled=False)
shield1 = Entity(model='shield1', scale=0.5, parent=camera, position=Vec3(-0.6, -0.3, 1), rotation_y=-90, enabled=False)
world = Entity(model='everythiing', scale=5, texture='build/exe.win-amd64-3.13/Assets_for_Everland/Textures/Grass.jpg', collider='mesh', position=(0, -60, 0))
house_layout = Entity(model='House layooout', double_sided=True, scale=5, texture='Textures/House wall.jpeg', collider='mesh', texture_scale=(2, 2), position=(0, -60, 0))
water = Entity(model='cube', double_sided=True, scale=(10000, 100, 10000), texture='Water', texture_scale=(40, 40), position=(0, -120, 0))
under_sea = Entity(model='plane', scale=10000, texture='Textures/Sand.jpg', texture_scale=(80, 80), collider='box', position=(0, -90, 0))
#boat = Entity(model='booat', scale=5, texture='Textures/Tree texture.jpg', collider='mesh', position=(0, -64, 0), offset=(500, -64, 500))
Tree_layout = Entity(model='Treeee pattern', scale=5, texture='Textures/Tree texture.jpg', collider='mesh', position=(0, -60, 0))
everland = Entity(model='Everland', scale=5, texture='Textures/House wall.jpeg', collider='mesh', position=(0, -60, 0))
relic = Entity(model='relic', scale=5, texture='Textures/Tree texture.jpg', position=(200, -80, -50), collider='box')
sunroot = Entity(model='flower', scale=6, color=color.pink, position=(1000, 120, 300), collider='box')
dont_touch_this = Entity(model='cube', scale=1, color=color.red, collider='box', enabled=False)
castle_island = Entity(model='castle island', scale=60, texture='Textures/Grasss.jpg', collider='mesh', position=Vec3(-3000, -60, 2000))
castle = Entity(model='castle', scale=60, texture='Textures/House wall.jpeg', collider='mesh', position=Vec3(-3000, -60, 2000), double_sided=True)

bow = Entity(model='bow', texture='Textures/Tree texture.jpg', parent=camera, position=Vec3(1, -0.6, 2), color=color.brown, rotation=Vec3(0, 180, 90))


underwater_fx = UnderwaterEffect(blur_texture='build/exe.win-amd64-3.13/Assets_for_Everland/Textures/Blur-PNG-Image.png', enabled=False)

banner1 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2930), rotation_y=90)
banner2 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2910), rotation_y=90)
banner3 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2890), rotation_y=90)
banner4 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2870), rotation_y=90)
banner5 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2850), rotation_y=90)
banner6 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2830), rotation_y=90)
banner7 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2810), rotation_y=90)
banner8 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2790), rotation_y=90)
banner9 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2770), rotation_y=90)
banner10 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2750), rotation_y=90)
banner11 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2730), rotation_y=90)
banner12 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2710), rotation_y=90)
banner13 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2690), rotation_y=90)
banner14 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2670), rotation_y=90)
banner15 = Entity(model='banner', scale=3, color=color.green, position=(-400, -57, 2650), rotation_y=90)

player.disable()
main_menu = MainMenu(player)

if main_menu.enabled == True:
    sword.disable()
sky = Entity(model='sphere', scale=10000, texture='sky_sunset', double_sided=True, rotation=(0, 180, 0))


glow_mist = Entity(
    model='circle',
    texture='Textures/Blur-Effect-PNG-HD-Image.png',
    position=volcano.world_position + Vec3(0, 30, 0),
    scale=30,
    double_sided=True,
    billboard=True,
    collider='box'
)

# Add gentle animation to enhance atmospheric feel



#text

inscription_text = Text('here lies hope', origin=(0,0), background=True)
inscription_text.visible = False

# Audio

WalkingSound = Audio('audio/walking-sound-effect-272246.mp3', loop=False, volume=1)
GameMusic = Audio('audio/koden-348767.mp3', loop=True, volume=0.5, autoplay=True)




# Create quest progress text
quest_text = Text(text='Fragments: 0/3', position=(-0.85, 0.4), scale=2, enabled=False)
# arrow count
arrow_text = Text(text=arrow_count, position=(-0.4, -0.35))


eruption_rate = 5  # eruptions per second

from ursina import *


# Update function now also refreshes progress display
def update():
    # Multiplayer: update camera to show all players
    if other_players:
        # Get all positions (including self)
        positions = [player.position] + [e.position for e in other_players.values()]
        # Center camera between all players
        avg_pos = sum(positions, Vec3(0,0,0)) / len(positions)
        camera.position = avg_pos + Vec3(0, 20, -30)
        camera.look_at(avg_pos)
    # Multiplayer: send this player's position to the server
    if hasattr(player, 'position'):
        print(f"Sending position_update: client={my_id}, position=({player.position.x}, {player.position.y}, {player.position.z})")
        Client.send_message('position_update', {'client': my_id, 'position': (player.position.x, player.position.y, player.position.z)})
    # Multiplayer: send this player's position to the server
    # ...existing code...
    global player_damage_timer
    player_damage_timer -= time.dt
    if player_damage_timer <= 0:
        if goblin1.is_alive and goblin1.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin2.is_alive and goblin2.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin3.is_alive and goblin3.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin4.is_alive and goblin4.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin5.is_alive and goblin5.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin6.is_alive and goblin6.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin7.is_alive and goblin7.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin8.is_alive and goblin8.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin9.is_alive and goblin9.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin10.is_alive and goblin10.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        if goblin11.is_alive and goblin11.intersects(player).hit:
            HB1.value -= 10
            player_damage_timer = 1.0
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
        # king of doom
        if goblin_king1.is_alive and goblin_king1.intersects(player).hit:
            HB1.value -= 25
            camera.shake(duration=0.8, magnitude=10)
            Audio('audio/homemadeoof-47509.mp3', volume=2.0)
            player_damage_timer = 1.0

    global time_of_day, enemy_spawned
    time_of_day += time.dt / 300
    if time_of_day > 1:
        time_of_day = 0

    # adjust sky brightness and color
    sky.rotation_y += time.dt * 5
    if time_of_day < 0.5:
        sky.color = color.white
    else:
        sky.color = color.gray

    # Water FX
    water_surface_y = water.y + water.scale_y / 2
    if camera.world_position.y < water_surface_y:
        underwater_fx.enable()
    else:
        underwater_fx.disable()

    # Walking sound logic
    if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']:
        if not WalkingSound.playing:
            WalkingSound.play()
    else:
        WalkingSound.stop()

    # Quest progress update
    if quest_manager.quest_active and not quest_manager.quest_completed:
        quest_text.text = f'Fragments: {quest_manager.fragments_collected}/{quest_manager.total_fragments}'
    elif quest_manager.quest_completed:
        quest_text.text = "Quest Complete"

    if distance(player.position, fara.position) < 5:
        fara_name.visible = True
    else:
        fara_name.visible = False

    if distance(player.position, elder_miro.position) < 5:
        npc_name.visible = True
    else:
        npc_name.visible = False
    if distance(player.position, zintra.position) < 5:
        zintra_name.visible = True
    else:
        zintra_name.visible = False


relic_found = False



# Simple inventory implementation
class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, item_name):
        self.items[item_name] = self.items.get(item_name, 0) + 1
        self.update_ui()

    def remove_item(self, item_name):
        if item_name in self.items:
            self.items[item_name] -= 1
            if self.items[item_name] <= 0:
                del self.items[item_name]
            self.update_ui()

    def has_item(self, item_name):
        return item_name in self.items

    def update_ui(self):
        content = '\n'.join([f'{name}: {amount}' for name, amount in self.items.items()])
        inventory_panel.content.text = content



# goblin = Entity(model='goblin', position=Vec3(0, -20, 0), collider='mesh')
# goblin.add_script(SmoothFollow(target=player, speed=1))

inventory_panel = WindowPanel(
    title='Inventory',
    content=[Text(text='', scale=1)],  # Bigger text
    enabled=False,
    scale=0.5,
    scale_x=0.9,  # Make the panel larger overall
    position=(-0.6, 0.5),  # Position it to the right side of the screen
)
# Create an inventory instance
player_inventory = Inventory()


fara = Entity(model='statue', color=color.green, scale=(1,1,1), position=(1000, -6, 305), collider='box', rotation_y=160)
fara_name = Text(text='Fara the Herbalist', position=(0, 0.42), scale=1.2, background=True)
fara_name.visible = False

zintra = Entity(model='statue', color=color.cyan, scale=(1, 1, 1), position=(1000, -4, 290), collider='box')
zintra_name = Text(text='Zintra the Memory Keeper', position=(0, 0.42), scale=1.2, background=True)
zintra_name.visible = False
zintra_dialog = [
    "Memories whisper through the sands...",
    "Would you like to remember who you were before the light scattered?",
    "The relic remembers. Now... do you?"
]
zintra_dialog3 = [
    "You have fragments, let me help you remember."
    "Your dad was a hero, a guardian of light."
    "But darkness fell, scattering the light and your memories."
    "Now, you must gather the fragments to restore his past."
]
zintra_dialog_index = 0
zintra_dialog_text = Text(text='', color=color.violet, position=(0, -0.35), scale=1.5, background=False)
zintra_dialog_text.visible = False

allGemsCollected = False
relicCollected = False
sunrootCollected = False


# Camera cutscene logic
cutscene_camera = EditorCamera(enabled=False)  # Disable manual control
camera.position = Vec3(-100, 0, -200)
camera.look_at(Vec3(-150, -40, -70))

#a_random_ogar = Entity(model='statue', color=color.red, scale=600, position=Vec3(1000, 50, 600), collider='box')

elder_miro = Entity(model='statue', color=color.gold, scale=(1, 1, 1), position=(-55, -18, -12), collider='box')
npc_name = Text(text='Elder Miro', position=(0, 0.45), scale=1.5, background=True)
npc_name.visible = False

# Villager entity
villager = Entity(
    model='statue',
    color=color.red,
    position=(3110, -61, 1850),
    collider='box'
)

# Floating name label
villager_name = Text(
    text='Villager',
    position=(0, 0.45),
    scale=1.5,
    background=True
)

villager_name.visible = False


dialog_lines = [
    'Help, these goblins are attacking our village!',
    'It has been ages and only half of us are left.',
    'Please help us!'
]


dialog_box = Text(
    text='',
    position=(0, -0.35),
    scale=1.25,
    color=color.red
)
dialog_box.visible = False

# Track which line we're on
dialog_index1 = 0

# Villager1 entity
villager1 = Entity(
    model='statue',
    color=color.red,
    position=(100, -61, -200),
    collider='box'
)

# Floating name label
villager_name = Text(
    text='Villager',
    position=(0, 0.45),
    scale=1.5,
    background=True
)

villager_name.visible = False


dialog_lines1 = [
    'Hero, there is danger',
    'you must travel to island 3',
    'and kill him. kill him now'
]


dialog_box1 = Text(
    text='',
    position=(0, -0.35),
    scale=1.25,
    color=color.black
)
dialog_box1.visible = False

# Track which line we're on
dialog_index2 = 0

# Villager1 entity
villager9 = Entity(
    model='statue',
    color=color.red,
    position=(-1000, -61, 3000),
    collider='box'
)

# Floating name label
villager_name1 = Text(
    text='rebel',
    position=(0, 0.45),
    scale=1.5,
    background=True
)

villager_name1.visible = False


dialog_lines2 = [
    "You don't know me, I don't know you",
    'I am part of the rebel force to kill the king',
    'talk to rebel leader he is in the castle'
]


dialog_box2 = Text(
    text='',
    position=(0, -0.35),
    scale=1.25,
    color=color.black
)
dialog_box2.visible = False

# Track which line we're on
dialog_index3 = 0

# Villager1 entity
rebel_leader = Entity(
    model='statue',
    color=color.red,
    rotation_y=90,
    position=(-999, -61, 3300),
    collider='box'
)

# Floating name label
villager_name2 = Text(
    text='rebel',
    position=(0, 0.45),
    scale=1.5,
    background=True
)

villager_name2.visible = False


dialog_lines3 = [
    "psst. . . Over here",
    'I am the leader of the rebel force to kill the king',
    'He has killed and starved so many',
    'But every body who tried to stad up died',
    'will you kill him once and for all',
    'as soon as you do everyone will turn on you all humans will hate you',
    'I trust that in the grater good you will proceed with this oporation'
]


dialog_box3 = Text(
    text='',
    position=(0, -0.35),
    scale=1.25,
    color=color.black
)
dialog_box3.visible = False

# Track which line we're on
dialog_index4 = 0

# Define QuestManager
class QuestManager:
    def __init__(self):
        self.fragments_collected = 0
        self.total_fragments = 3
        self.quest_active = True
        self.quest_completed = False

    def collect_fragment(self):
        if self.quest_active and not self.quest_completed:
            self.fragments_collected += 1
            print(f'Fragment collected: {self.fragments_collected}/{self.total_fragments}')
            if self.fragments_collected >= self.total_fragments:
                self.complete_quest()

    def complete_quest(self):
        self.quest_completed = True
        print("Quest Complete: Echoes of the Forgotten Light")
        sword.color = color.yellow
        sword.scale *= 1
        sword.tooltip = Tooltip("Empowered Sword")
        Audio('audio/success.mp3', loop=False, volume=1).play()

quest_manager = QuestManager()

fragments = []

for pos in [(-55, -15, -3), (3220, -45, 1900), (-3990, -10, -1100)]:
    frag = Entity(model='gems', scale=0.5, color=color.azure, position=pos, collider='box')
    
    
    fragments.append(frag)

def frags(key):
    if key == 'e' and quest_manager.quest_active:  # <-- Add this check
        for frag in fragments[:]:
            if distance(player.position, frag.position) < 4:
                quest_manager.collect_fragment()
                fragments.remove(frag)
                gem_button.visible = True
                destroy(frag)
                allGemsCollected == True
                break
    elif key == 'e' and quest_manager.quest_active == False:
        pass


fara_dialog = [
    "Shh! The statue listens...",
    "Bring me a sunroot and I'll brew a potion of clarity."
]

npc_dialog = [
    "Welcome to Everland, Hero"
    "Darkness fell, light scattered…",
    "Bring me the relic and I shall restore hope."
]

zintra_dialog = [
    "Memories whisper through the sands.",
    "Would you like to remember who you were before the light scattered?"
    "I can help you with that, but it will cost you a fragment of your past."
    "collect fragments to remember your past."
]

zintra_dialog2 = [
    "You have fragments, let me help you remember."
    "You were a hero, a guardian of light."
    "But darkness fell, scattering the light and your memories."
    "Now, you must gather the fragments to restore your past."
]

pause_handler = Entity(ignore_paused=True)
pause_text = Text('PAUSED', origin=(0,0), scale=2, enabled=False) # Make a Text saying "PAUSED" just to make it clear when it's paused.

def pause_handler_input(key):
    if key == 'p':
        application.paused = not application.paused # Pause/unpause the game.
        pause_text.enabled = application.paused     # Also toggle "PAUSED" graphic.
        

pause_handler.input = pause_handler_input   # Assign the input function to the pause handler.
if pause_handler.enabled == True:
    player.disable()
dialog_index = 0
dialog_text = Text(text='', color=color.blue, position=(0, -0.35), scale=1.5, background=False)
dialog_text.visible = False

sunroot_found = False

# player inreactions
# input funks
def input(key):
    global zintra_dialog_index
    global zintra_dialog3
    global dialog_index1
    global dialog_index2
    global dialog_index3
    global dialog_index4
    if key == 'right mouse down':
        switch_to_bow()
        shoot_arrow()

    elif key == 'left mouse down':
        switch_to_sword()
        sword_attack()

    if key == 'shift':
        player.speed = 10
    if key == 'e' and distance(player.position, shrine_gem) < 10:
        if not quest_manager.quest_completed:
            shrine_gem.color = color.yellow
            shrine_gem.tooltip = Tooltip("Shrine Gem")
            destroy(shrine_gem)
    if key == '5':
        player.position = Vec3(-1000, 30, 590)
    if key == 'shift up':
        player.speed = 5
    if key == 'i':
        inventory_panel.enabled = not inventory_panel.enabled
        if inventory_panel.enabled:
            application.paused = True
            mouse.visible = True
            mouse.locked = False
        else:
            application.paused = False
            mouse.visible = False
            mouse.locked = True
    if key == '9':
        sword.enable()
    if key == 'i':
        inventory_panel.enabled = not inventory_panel.enabled

        if inventory_panel.enabled:
            application.paused = True
            mouse.visible = True
            mouse.locked = False
        else:
            application.paused = False
            mouse.visible = False
            mouse.locked = True
    if key == 'm':
        player.speed=100
    if key == 'm up':
        player.speed=5
    # Keep your other key events here...
    if key == '1':
        player.position = Vec3(0, -17, 0)
    if key == '4':
        player.position = Vec3(1000, -2, 300)
    if key == '2':
        player.position = Vec3(3200, -17, 2000)
    if key == '3':
        player.position = Vec3(-4000, -17, -1200)
    if key == '6':
        player.position = Vec3(-3000, -17, 2040)
    if key == 'g':
        blast_fire()
    if key == '7':
        player.position = Vec3(-500, -60, 2600)
    if main_menu.main_menu.enabled == False:
        if key == "escape":
            main_menu.pause_menu.enabled = not main_menu.pause_menu.enabled
            mouse.locked = not mouse.locked
            application.pause = True
        else:
            application.pause = False
    global relic_found
    if key == 'e' and not relic_found and distance(player.position, relic.position) < 20:
        relic_found = True
        destroy(relic)
        inscription_text.text = "Good job, hero! You found the relic!, now return to the Elder." \
        " he has much to say."
        inscription_text.visible = True
        inscription_text.background = False
        invoke(setattr, inscription_text, 'visible', False, delay=6)
        Audio('audio/success.mp3', loop=False, volume=1).play()
        relicCollected == True
        global dialog_index
    if key == 'e' and distance(player.position, sunroot.position) < 20:
        destroy(sunroot)
        sunroot_button.visible = True
        global dialog_index
    if key == "f":
        player.gravity = -1
    if key == 'f up':
        player.gravity = 1
    if key == 'q':
        quest_text.enable = True
    else:
        quest_text.enable = False
    if key == 'h':
        blast_ice()
    if key == 'e' and distance(player.position, elder_miro.position) < 5:
        dialog_text.visible = True
        dialog_text.text = npc_dialog[dialog_index]
        dialog_index = (dialog_index + 1) % len(npc_dialog)
        invoke(setattr, dialog_text, 'visible', False, delay=4)
    if key == 'e' and distance(player.position, villager.position) < 5:
        dialog_box.visible = True
        dialog_box.text = dialog_lines[dialog_index1]
        dialog_index1 = (dialog_index1 + 1) % len(dialog_lines)
        invoke(setattr, dialog_box, 'visible', False, delay=4)
    if key == 'e' and distance(player.position, rebel_leader.position) < 5:
        dialog_box3.visible = True
        dialog_box3.text = dialog_lines3[dialog_index4]
        dialog_index4 = (dialog_index4 + 1) % len(dialog_lines3)
        invoke(setattr, dialog_box3, 'visible', False, delay=4)
    if key == 'e' and distance(player.position, villager1.position) < 5:
        dialog_box1.visible = True
        dialog_box1.text = dialog_lines1[dialog_index2]
        dialog_index2 = (dialog_index2 + 1) % len(dialog_lines1)
        invoke(setattr, dialog_box1, 'visible', False, delay=4)
    if key == 'e' and distance(player.position, villager9.position) < 5:
        dialog_box2.visible = True
        dialog_box2.text = dialog_lines2[dialog_index3]
        dialog_index3 = (dialog_index3 + 1) % len(dialog_lines2)
        invoke(setattr, dialog_box2, 'visible', False, delay=4)
    if key == 'e' and distance(player.position, fara.position) < 5:
        dialog_text.visible = True
        invoke(setattr, dialog_text, 'visible', False, delay=4)
    if key == 'e' and distance(player.position, zintra.position) < 5:
        zintra_dialog_text.visible = True
        zintra_dialog_text.text = zintra_dialog[zintra_dialog_index]
        zintra_dialog_index = (zintra_dialog_index + 1) % len(zintra_dialog)
        invoke(setattr, zintra_dialog_text, 'visible', False, delay=4)
#    if key == 'e' and distance(player.position, dont_touch_this.position) < 5:
#        destroy(dont_touch_this)
    if key == 'e' and distance(player.position, island.position) < 100*100*100:
        print('glad you did not die')
    if key == '8':
        global shield_equipped
        shield1.enabled = True
        shield_equipped = True  # Show the bow when key 8 is pressed
        player.speed = 2
        if key == 'shift':
            player.speed = 2
        if key == 'shift up':
            player.speed = 2
    if key == '8 up':
        shield_equipped = False
        shield1.enabled = False
        player.speed = 5

    frags(key)


from ursina import time

time_of_day = 0  # ranges from 0 to 1 (0 = dawn, 0.5 = noon, 1 = midnight)


shield = Entity(
    model='shield',  # Use a custom model if you have one!
    parent=camera,
    position=Vec3(0, 5, 0),
    scale=(1),
    origin_z=-5,
    enabled=True,
    rotation_y=90,
    rotation_x=90
)

class allTheItems(Entity):
    if allGemsCollected == True and relicCollected == True and sunrootCollected == True:
        player.position = Vec3(0, 0, 0)





shield.enabled = False
sword.enabled = True  # Start with sword equipped

def update_ui(self):
    text_element = inventory_panel.content[0]
    content = '\n'.join([f'{name}: {amount}' for name, amount in self.items.items()])
    text_element.text = content

        
# Add a simple UI

version_text = 'version alpha: 0.3.5, gunargamesAB, do not distribute'
version = Text(text=version_text, position=Vec2(-0.86, -0.45), scale=0.7)

sword_button = Button(color=color.black, icon='sword', scale=0.1, position=Vec2(0.8, 0.43))
shield_button = Button(color=color.black, text='Shield', scale=0.1, position=Vec2(0.8, 0.32))
sunroot_button = Button(color=color.black, text='Sunroot', scale=0.1, position=Vec2(0.8, 0.10), visible=False)
gem_button = Button(color=color.black, text='Fragment', scale=0.1, position=Vec2(0.8, 0.21), visible=False)

# Crosshair
crosshair = Entity(model='quad', scale=0.02, color=color.white, position=(0, 0, 0.1), origin=(0.5, 0.5))

shield_equipped = False


# Lighting + shadows
ambient = AmbientLight(color = Vec4(0.5, 0.55, 0.66, 0) * 1.5)

sun = DirectionalLight(shadow_map_resolution=(3000, 3000))
sun.look_at = Vec3(1, -1, -1,)

# Run the game
window.title = 'Everland'

window.fullscreen = True

EditorCamera

# death
if HB1.value >= 0:
    print('loser, L rizz is you')

update()

app.run()