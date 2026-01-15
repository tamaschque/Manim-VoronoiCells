from typing import Sequence
import random

from manim import *
import shapely.geometry as shapely
from geovoronoi import voronoi_regions_from_coords 

from manim.typing import (
    Point3DLike,
    Point2DLike
)


DEFAULT_BOUNDING_POLYGON = [
            [-config.frame_width/2,  config.frame_height],
            [ config.frame_width/2,  config.frame_height],
            [ config.frame_width/2, -config.frame_height],
            [-config.frame_width/2, -config.frame_height],
        ]
ALL_COLORS = [x for x in globals().values() if isinstance(x, ManimColor)]


class VornoiCells(VGroup):
    """Generates a Voronoi Tessellation around a set of given points. 

    Parameters
    ----------
    points : Sequence[Point3DLike] | Sequence[Mobject],
        Points around which the Voronoi Cells should be generated.
    bounding_polygon : Sequence[Point2DLike]
        Polygon to which the Voronoi Cells should be containted to. By defaults its the entire screen. 
    color_scheme : Sequence[ManimColor]
        Array of ManimColors from which the cells get colored. If no color_scheme is provided a random selection from all preset manim colors will be chosen.
    stroke_color : ManimColor
        Stroke Color of the polygons.
    stroke_width : float
        Stroke Width of the polygons.
    color_match_points : bool
        If set to True the polygons will retain their assigned color. Usefull when animating the cells.
    """
    def __init__(
        self,
        points: Sequence[Point3DLike] | Sequence[Mobject],
        bounding_polygon: Sequence[Point2DLike] = DEFAULT_BOUNDING_POLYGON,
        color_scheme: Sequence[ManimColor] = None,
        stroke_color = WHITE,
        stroke_width = DEFAULT_STROKE_WIDTH,
        color_match_points = True,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.scattered_points = points
        bounding_poly = shapely.Polygon(bounding_polygon)
        self.color_scheme = color_scheme
        
        if color_scheme is None:
            self.color_scheme = ALL_COLORS 
            random.shuffle(self.color_scheme)

        self.stroke_color = stroke_color
        self.stroke_width = stroke_width

        self.color_match_points = color_match_points

        self._generate_voronoi_poly(
            self._points_to_coords(),
            bounding_poly
        )

    @classmethod
    def to_axes(
        cls,
        points: Sequence[Point3DLike] | Sequence[Mobject],
        axes: Axes,
        **kwargs
    ):
        """Generates a voronoi tessellation around a set of given points that are drawn on a :class:`Axes`. This changes the confinement of the diagram to the bounds of the axes.

        Parameters
        ----------
        points : Sequence[Point3DLike] | Sequence[Mobject]
            Points around which the Voronoi Cells should be generated.
        axes : Axes
            Axes to which the points are drawn to.
        """
        coords = []
        for point in points:
            if isinstance(point, Mobject):
                coords.append(point.get_center()[:2])
            else:
                coords.append(axes.c2p(*point)[:2])

        bounding_poly = shapely.Polygon([
            axes.get_corner(UL)[:2],
            axes.get_corner(UR)[:2],
            axes.get_corner(DR)[:2],
            axes.get_corner(DL)[:2],
        ])

        return cls(coords, bounding_poly, **kwargs)

    def _points_to_coords(self):
        coords = []
        for point in self.scattered_points:
            if isinstance(point, Mobject):
                coords.append(point.get_center()[:2])
            else:
                coords.append(point)
        
        return coords
    
    def _generate_voronoi_poly(self, coords, bounding_poly):
        coords = np.array(coords)
        regions, _ = voronoi_regions_from_coords(
            coords,
            bounding_poly
        )

        colors = self.color_scheme[:]
        for poly, color in zip(regions.values(), self.color_scheme):
            verticies = np.array(poly.exterior.coords)
            verticies_3d = np.pad(verticies, (0,1))[:-1]

            poly = Polygon(*verticies_3d).set_stroke(color=self.stroke_color, width=self.stroke_width)

            # Check which Point the Polygon should match its color
            colors = self.color_scheme[:]
            if self.color_match_points:
                for i, point in enumerate(self.scattered_points):
                    if isinstance(point, Mobject):
                        point_pos = point.get_center()
                    else:
                        point_pos = point

                    if shapely.Polygon(verticies).contains(shapely.Point(point_pos)):
                        poly_color = colors[i]
                        break
            else:
                poly_color = color

            poly.set_fill(color=poly_color, opacity=1)
            self.add(poly)
          
