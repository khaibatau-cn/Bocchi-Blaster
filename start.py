import pygame
from game import Game

if __name__ == "__main__":
    pygame.init()
    game = Game() #calling the class Game (main features)
    game.run() #def run in class Game
    pygame.quit()