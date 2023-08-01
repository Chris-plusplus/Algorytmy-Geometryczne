import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os.path as path
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon
import matplotlib.animation as animation
from copy import copy

class Drawable():
    def __init__(self):
        self.array = []
        self.frames_stamps = []
        self.frame_idx = 0
    
    def draw_all(self, ax):
        for index in range(len(self.array)):
            self.draw(ax, index)

    def add(self, *args):
        self.array.append(args)

    def array_len(self):
        return len(self.array)
    
    def new_frame(self):
        self.frames_stamps.append(len(self.array))


class Points(Drawable):
    def draw(self, ax, index):
        points, color = self.array[index]
        artist = ax.scatter(points[:, 0], points[:, 1], color=color)
        return [artist]

    def add(self, points, color=None):
        points = np.array(points)

        if len(points.shape) >= 2 and points.shape[1:] == (2, ):
            super().add(points, color)
        else:
            raise ValueError('dimension mismatch')
        
        
class LineSegments(Drawable):
    def draw(self, ax, index):
        line_segments, color = self.array[index]
        line_collection = LineCollection(line_segments, color=color)
        artist = ax.add_collection(line_collection)
        return [artist]

    def add(self, line_segments, color=None):
        line_segments = np.array(line_segments)

        if len(line_segments.shape) >= 2 and line_segments.shape[1:] == (2, 2):
            super().add(line_segments, color)
        else:
            raise ValueError('dimension mismatch')


class Polygons(Drawable):
    def draw(self, ax, index):
        polygons, color = self.array[index]
        artist_arr = []
        for polygon in polygons:
            p = Polygon(polygon, color=color, alpha=0.4, zorder=0)
            artist = ax.add_patch(p)
            artist_arr.append(artist)
        return artist_arr

    def add(self, polygons, color=None):
        polygons = np.array(polygons)

        if len(polygons.shape) >= 3 and polygons.shape[2:] == (2, ):
            super().add(polygons, color)
        else:
            raise ValueError('dimension mismatch')


class Visualizer():
    def __init__(self):
        self.points = Points()
        self.line_segments = LineSegments()
        self.polygons = Polygons()


        self.frames_count = 0
        self.animated_objects = [self.points, self.line_segments, self.polygons]
        self.anim = None

    def add_points(self, points, color=None):
        self.points.add(points, color)
        
    def add_line_segments(self, line_segments, color=None):
        self.line_segments.add(line_segments, color)
        
    def add_polygons(self, polygons, color=None):
        self.polygons.add(polygons, color)

    def new_frame(self):
        for obj in self.animated_objects:
            obj.new_frame()
        self.frames_count += 1

    def make_gif(self, interval=600):
        if self.frames_count == 0:
            raise RuntimeError("No frames were added")
        
        fig, ax = plt.subplots()

        frame = 0

        artists = []
        artist_frame = []

        artist_x = ax.set_xlabel('x')
        artist_y = ax.set_ylabel('y')

        artist_frame.append(artist_x)
        artist_frame.append(artist_y)

        while frame < self.frames_count:
            for obj in self.animated_objects:
                idx_end = obj.frames_stamps[frame]

                while obj.frame_idx < idx_end:
                    obj_artist = obj.draw(ax, obj.frame_idx)
                    artist_frame.append(*obj_artist)
                    obj.frame_idx += 1

            artists.append(copy(artist_frame))
            frame += 1

        self.anim = animation.ArtistAnimation(fig=fig, artists=artists, interval=interval, blit=False)
        plt.show()

    def save_gif(self, filename):
        if self.anim == None:
            raise RuntimeError("No animation detected")

        self.anim.save(filename=filename, writer="pillow")

    def __build_plot(self):
        fig, ax = plt.subplots()

        ax.set_xlabel('x')
        ax.set_ylabel('y')

        for obj in self.animated_objects:
            obj.draw_all(ax)

        ax.autoscale()

        return fig, ax

    def show(self):
        fig, _ = self.__build_plot()
        fig.show(warn=False)

    # save information about figure to file of given $file_name
    def save_plot(self, file_name):
        with open(file_name, "w") as file:
            for points, color in self.points_array:
                file.write(color+"\n")
                file.write("".join(f"{p[0]}, {p[1]}\n" for p in points))
            file.write("points_end\n")
            for line_segments, color in self.line_segments_array:
                raise RuntimeError("writing line_segments not implement yet")
                file.write(color)
                file.write(str(line_segments))

    def clear(self):
        self.points_array.clear()
        self.line_segments_array.clear()

    # clear current visualizer and fill it with elements from file of given name
    def open_plot(self, file_name):
        if not path.isfile(file_name):
            raise ValueError(f"{file_name} IS NOT A FILE")
        self.clear()
        with open(file_name, "r") as file:
            readed_color = file.readline()
            while "points_end\n" != readed_color:
                color = readed_color[:-1]
                points = []
                readed_point = file.readline()
                while "," in readed_point:
                    points.append(list(map(float, readed_point.split(","))))
                    readed_point = file.readline()
                self.add_points(points, color=color)
                readed_color = readed_point
            raise RuntimeError("load lines segments not implement yet")
        
    # save plot image to file of given $file_name
    def save_picture(self, file_name):
        fig, _ = self.__build_plot()
        fig.savefig(file_name)
        plt.close()
