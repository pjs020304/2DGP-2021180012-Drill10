# 이것은 각 상태들을 객체로 구현한 것임.
import pico2d
from pico2d import get_time, load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, load_font
from state_machine import *
from ball import Ball
import game_world
import game_framework
import random

# Bird Run Speed
BIRD_PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm
BIRD_RUN_SPEED_KMPH = 20.0 # Km / Hour
BIRD_RUN_SPEED_MPM = (BIRD_RUN_SPEED_KMPH * 1000.0 / 60.0)
BIRD_RUN_SPEED_MPS = (BIRD_RUN_SPEED_MPM / 60.0)
BIRD_RUN_SPEED_PPS = (BIRD_RUN_SPEED_MPS * BIRD_PIXEL_PER_METER)
# Bird Action Speed
BIRD_TIME_PER_ACTION = 1.5
BIRD_ACTION_PER_TIME = 1.0 / BIRD_TIME_PER_ACTION
BIRD_FRAMES_PER_ACTION = 8


class Idle:
    @staticmethod
    def enter(bird, e):
        bird.dir = 1
        bird.action = 3
        bird.face_dir = 1
        bird.frame = 0
        bird.action = 2

    @staticmethod
    def exit(bird, e):
        pass

    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + BIRD_FRAMES_PER_ACTION * BIRD_ACTION_PER_TIME * game_framework.frame_time) % 5
        bird.x += bird.dir * BIRD_RUN_SPEED_PPS * game_framework.frame_time
        bird.wait_time = get_time()
        if (bird.x >800):
            bird.dir = -1
        if (bird.x < 50):
            bird.dir = 1
    @staticmethod
    def draw(bird):
        if bird.dir == 1:
            bird.image.clip_draw(int(bird.frame) * 190, bird.action * 170, 100, 100, int(bird.x), bird.y, 50, 50)
        else:
            bird.image.clip_composite_draw(int(bird.frame) * 190, bird.action * 170, 100, 100,0,'h', int(bird.x), bird.y, 50, 50)



class Sleep:
    @staticmethod
    def enter(bird, e):
        if start_event(e):
            bird.face_dir = 1
            bird.action = 3
        bird.frame = 0

    @staticmethod
    def exit(bird, e):
        pass

    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + 1) % 8


    @staticmethod
    def draw(bird):
        if bird.face_dir == 1:
            bird.image.clip_composite_draw(bird.frame * 100, 300, 100, 100,
                                          3.141592 / 2, '', bird.x - 25, bird.y - 25, 100, 100)
        else:
            bird.image.clip_composite_draw(bird.frame * 100, 200, 100, 100,
                                          -3.141592 / 2, '', bird.x + 25, bird.y - 25, 100, 100)

class Run:
    @staticmethod
    def enter(bird):
        bird.dir = 1

    @staticmethod
    def exit(bird, e):
        if space_down(e):
            bird.fire_ball()


    @staticmethod
    def do(bird):
        bird.frame = (bird.frame + BIRD_FRAMES_PER_ACTION * BIRD_ACTION_PER_TIME * game_framework.frame_time) % 5
        bird.x += bird.dir * BIRD_RUN_SPEED_PPS * game_framework.frame_time
        if (bird.x >800):
            bird.dir = -1
        if (bird.x < 50):
            bird.dir = 1

    @staticmethod
    def draw(bird):
        if( bird.dir == 1):
            bird.image.clip_draw(int(bird.frame) * 200, bird.action * 170, 100, 100, int(bird.x), bird.y)
        else:
            bird.image.clip_composite_draw(int(bird.frame) * 180, bird.action * 170, 100, 100,0,'v', int(bird.x), bird.y)




class Bird:

    def __init__(self):
        self.font = load_font('ENCR10B.TTF', 16)
        self.x, self.y = random.randint(100, 700), 500
        self.face_dir = 1
        self.image = load_image('bird_animation.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, space_down: Idle},
                Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, space_down: Run},
                Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        # 여기서 받을 수 있는 것만 걸러야 함. right left  등등..
        self.state_machine.add_event(('INPUT', event))
        pass

    def draw(self):
        self.font.draw(self.x - 60, self.y + 50, f'(Time: {get_time():.2f})', (255, 255, 0))
        self.state_machine.draw()

    def fire_ball(self):
        ball = Ball(self.x, self.y, self.face_dir * 10)
        game_world.add_object(ball)