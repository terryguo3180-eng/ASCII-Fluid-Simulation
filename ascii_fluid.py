from dataclasses import dataclass
import math


@dataclass
class Particle:
    x: float = 0.
    y: float = 0.
    fx: float = 0.
    fy: float = 0.
    vx: float = 0.
    vy: float = 0.
    dens: float = 0.

    is_wall: bool = False


class AsciiFluid:
    def __init__(
        self,
        width: int,
        height: int,
        gravity: float = 1.,
        pressure: float = 4.,
        viscosity: float = 7.,
    ):
        self.width = width
        self.height = height
        self.gravity = gravity
        self.pressure = pressure
        self.viscosity = viscosity

        self.particles: list[Particle] = []

    def input_file(self, filename: str):
        with open(filename, 'r') as f:
            text = f.read().expandtabs(4)

        x = y = 0

        for char in text:
            if char == ' ':
                x += 1
                continue

            if char == '\n':
                x = 0
                y += 2
                continue
        
            p1 = Particle(x, y)
            p2 = Particle(x, y + 1)

            if char == '#':  # '#' represents a wall particle
                p1.is_wall = True
                p2.is_wall = True

            self.particles.extend([p1, p2])
        
            x += 1
    
    def update(self):
        # Update the densities
        for p1 in self.particles:
            if p1.is_wall:
                p1.dens = 9
            else:
                p1.dens = 0

            for p2 in self.particles:
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                dist = math.sqrt(dx ** 2 + dy ** 2)

                if dist <= 2:
                    interaction = dist / 2 - 1
                    p1.dens += interaction ** 2
            
        # Update the forces
        for p1 in self.particles:
            p1.fx = 0
            p1.fy = self.gravity

            for p2 in self.particles:
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                dist = math.sqrt(dx ** 2 + dy ** 2)

                if dist <= 2:
                    interaction = dist / 2 - 1
                    p1.fx += interaction * (
                        dx * (3 - p1.dens - p2.dens) * self.pressure
                        + p1.vx * self.viscosity - p2.vx * self.viscosity
                    ) / p1.dens
                    p1.fy += interaction * (
                        dy * (3 - p1.dens - p2.dens) * self.pressure
                        + p1.vy * self.viscosity - p2.vy * self.viscosity
                    ) / p1.dens
        
        for p in self.particles:
            if not p.is_wall:
                if math.sqrt(p.fx ** 2 + p.fy ** 2) < 4.2:
                    p.vx += p.fx / 10
                    p.vy += p.fy / 10
                else:
                    p.vx += p.fx / 11
                    p.vy += p.fy / 11
                
                p.x += p.vx
                p.y += p.vy
        
    def render(self):
        screen = [0] * (self.width * self.height)
        for p in self.particles:
            i = p.x
            j = p.y // 2
            idx = int(i + self.width * j)

            if j >= 0 and j < self.height - 1 and i >= 0 and i < self.width - 1:
                screen[idx] |= 8
                screen[idx + 1] |= 4
                screen[idx + self.width] |= 2
                screen[idx + self.width + 1] |= 1
        
        display = '\x1b[1;1H'
        for i in range(len(screen)):
            if i % self.width == self.width - 1:
                display += '\n'
            else:
                display += " '`-.|//,\\|\\_\\/#"[screen[i]]
        
        print(display)

if __name__ == '__main__':
    ascii_fluid = AsciiFluid(80, 24)
    ascii_fluid.input_file('pour_out.txt')
    print('\x1b[2J')
    while True:
        ascii_fluid.update()
        ascii_fluid.render()
