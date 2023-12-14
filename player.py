from time import perf_counter
from multiprocessing import Process
import numpy as np
import pygame
from pygamevideo import Video
import requests
import json
import time


def play_video(path, duration_local):
    i = 0
    while i < 1:
        pygame.init()
        window = pygame.display.set_mode((1920, 1080))
        clock = pygame.time.Clock()

        start = perf_counter()
        video = Video(path)

        video.play(loop=False)

        titlebar_surf = pygame.Surface((1280, 35)).convert()
        titlebar_surf.set_alpha(180)

        control_surf = pygame.Surface((1280, 50)).convert()
        control_surf.set_alpha(180)

        pygame.draw.rect(control_surf, (100, 100, 100), (153, 22, 1100, 4), 0)
        while True:
            if np.round(perf_counter() - start) == duration_local:
                break
            clock.tick(0)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit(0)
            window.fill((1, 1, 1))

            video.draw_to(window, (0, 0))
            pygame.display.flip()
        pygame.quit()
        continue


if __name__ == "__main__":
    video_player = None
    webhook_url = "http://127.0.0.1/webhook"
    code = "0"
    duration = -1

    while True:
        data = {
            "current_code": code,
            "duration": duration
        }

        r = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
        response = json.loads(r.text)
        next_code = response["next_code"]
        duration = response["duration"]
        if next_code != code:
            if video_player is not None:
                video_player.terminate()
            code = next_code

            video_player = Process(target=play_video,
                                   args=(f"P:/Video-Player-With-Remote/static/videos/{code}.mp4", duration+2))
            video_player.start()
        time.sleep(1)
