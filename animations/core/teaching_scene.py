"""Absolute, frame-aligned timing and stable zones for the new teaching films."""
from manim import Scene, VGroup, Group, FadeIn, FadeOut, Succession, config
from .components import BG, MUTED, label, fade_replace


class TeachingScene(Scene):
    def setup_story(self, data, title):
        self.camera.background_color = BG
        self.data, self.cues = data, data['cues']
        self.events = {row['id']: row for row in data['events']}
        self.body = VGroup()
        self.header = self.heading(title)
        self.caption = self.caption_label(self.cues[0].caption)
        self.footer = label('TOY MODEL  •  ILLUSTRATIVE VALUES', 20, MUTED).move_to([0, 3.68, 0])
        self.chrome = (self.footer, self.header, self.caption)
        self.add(*self.chrome)

    @staticmethod
    def heading(text):
        return label(text, 38, max_width=12.4).move_to([0, 3.13, 0])

    @staticmethod
    def caption_label(text):
        return label(text, 27, max_width=12.4).move_to([0, -3.27, 0])

    def at(self, seconds):
        fps = float(config.frame_rate)
        target, current = round(seconds*fps), round(self.time*fps)
        if current > target:
            raise ValueError(f'Scene passed scheduled event: {self.time:g} > {seconds:g}')
        if current < target:
            self.wait((target-current)/fps, frozen_frame=True)

    def cue(self, index, title):
        self.at(self.cues[index].start)
        self.play(fade_replace(self.header, self.heading(title)),
                  fade_replace(self.caption, self.caption_label(self.cues[index].caption)), run_time=.4)

    def event(self, name, *animations):
        row = self.events[name]
        self.at(row['start'])
        self.play(*animations, run_time=row['settled']-row['start'])

    def replace_body(self, name, body):
        row = self.events[name]
        self.at(row['start'])
        # Manim may promote late-added group children to top-level mobjects.
        # Clear the actual scene inventory, not just the original parent group.
        outgoing = [m for m in self.mobjects if m not in self.chrome]
        transition = (Succession(FadeOut(Group(*outgoing)), FadeIn(body))
                      if outgoing else FadeIn(body))
        self.play(transition, run_time=row['settled']-row['start'])
        self.clear()
        self.add(*self.chrome, body)
        self.body = body

    def finish(self):
        self.at(self.cues[-1].end)


def lines(texts, *, x=0, top=1.5, spacing=.75, size=30, width=11, color=None):
    return VGroup(*[label(text, size, max_width=width, **({'color': color} if color else {}))
                   .move_to([x, top-i*spacing, 0]) for i, text in enumerate(texts)])
