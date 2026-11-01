"""Twelve-second synthetic typography, math, motion, and encoding preflight."""
from pathlib import Path
import numpy as np
from matplotlib import rc_context
from matplotlib.mathtext import math_to_image
from manim import (
    Scene, Text, SVGMobject, VGroup, Line, Dot, Square, ValueTracker,
    DecimalNumber, FadeIn, UP, DOWN, LEFT, RIGHT, always_redraw, linear, config,
)

OUTPUT = Path(config.media_dir).resolve().parent
FONT = "Arial"
WHITE, BLUE, ORANGE = "#F3F4F6", "#56B4E9", "#E69F00"


def equation(source, name, width):
    """Local mathtext SVG fallback: TeX is not installed on this host."""
    path = OUTPUT / f"{name}.svg"
    with rc_context({"savefig.transparent": True}):
        math_to_image(source, path, format="svg", color=WHITE)
    return SVGMobject(str(path)).set_width(width)


class DiagnosticPreflight(Scene):
    def construct(self):
        self.camera.background_color = "#111827"
        title = Text("One finding changes the probability", font=FONT, font_size=44, color=WHITE).to_edge(UP, buff=.45)
        subtitle = Text("Synthetic binary example  |  LR = 2", font=FONT, font_size=28, color=WHITE).next_to(title, DOWN, buff=.2)
        bayes = equation(r"$p(D\mid E)=\frac{p(D)\,\mathrm{LR}}{1-p(D)+p(D)\,\mathrm{LR}}$", "bayes", 7.5).move_to(UP*1.45)
        logs = equation(r"$\ln\frac{p(D\mid E)}{1-p(D\mid E)}=\ln\frac{p(D)}{1-p(D)}+\ln 2$", "logodds", 8.0).move_to(UP*.15)
        entropy = equation(r"$H(p)=-\sum_j p_j\log_2 p_j\quad\mathrm{bits}$", "entropy", 5.0).move_to(DOWN*1.0)
        alpha = ValueTracker(0)
        def probability():
            return 2**alpha.get_value() / (1 + 2**alpha.get_value())
        ruler = Line(LEFT*4+DOWN*2.0, RIGHT*4+DOWN*2.0, color=WHITE)
        before = Dot(ruler.point_from_proportion(.5), radius=.09, color=BLUE, fill_opacity=0, stroke_width=3)
        after = always_redraw(lambda: Square(color=ORANGE, fill_opacity=1).rotate(np.pi/4).scale(.08).move_to(ruler.point_from_proportion(probability())))
        ends = VGroup(*[Text(label, font=FONT, font_size=26, color=WHITE).move_to(ruler.point_from_proportion(x)+DOWN*.35) for label,x in [("0",0),("1",1)]])
        number = DecimalNumber(.5, mob_class=Text, num_decimal_places=3, font_size=32, color=ORANGE).move_to(RIGHT*4.8+DOWN*2)
        number.add_updater(lambda m: m.set_value(probability()))
        unit = Text("Probability of D", font=FONT, font_size=26, color=WHITE).move_to(LEFT*3+DOWN*1.6)
        caption = Text("Movement illustrates one update.\nIt does not represent extra observations.", font=FONT, font_size=30, color=WHITE, line_spacing=.8).to_edge(DOWN, buff=.35)
        self.play(FadeIn(VGroup(title, subtitle, bayes, logs, entropy, ruler, before, ends, unit, caption)), run_time=1)
        self.add(after, number)
        self.wait(3)
        self.play(alpha.animate.set_value(1), run_time=4, rate_func=linear)
        self.wait(4)
        assert np.isclose(probability(), 2/3)
