"""Explicit routes and approved scientific input identities. No scene imports."""
from dataclasses import dataclass


LEGACY_FIXTURE_HASH = 'd4204afd2e4ee8e8bcac9cd6d5842a4dbe172932a250930516d5f62b1922407b'


@dataclass(frozen=True)
class Film:
    goal: str
    cut: str
    slug: str
    scene: str
    scene_class: str
    story_module: str | None
    fixture_path: str = 'data/manim_fixtures.json'
    fixture_hash: str = LEGACY_FIXTURE_HASH
    dependencies: tuple[str, ...] = ()

    @property
    def narrated(self):
        return self.cut == 'clinical'


FILMS = {
    ('preflight', 'original'): Film('preflight', 'original', 'preflight', 'preflight.py', 'DiagnosticPreflight', None),
}
for goal, stem, scene, cls, clinical_scene, clinical_cls, dependencies in [
    ('01', 'uncertainty_increases', 'uncertainty_increases.py', 'UncertaintyIncreases', 'clinical_uncertainty.py', 'ClinicalUncertainty', ()),
    ('02', 'coordinate_systems', 'coordinate_systems.py', 'OneEvidenceThreeCoordinates', 'clinical_coordinates.py', 'ClinicalCoordinates', ('core/rulers.py',)),
    ('03', 'entropy_area', 'entropy_area.py', 'EntropyAsArea', 'clinical_entropy_area.py', 'ClinicalEntropyArea', ('core/entropy_geometry.py', 'core/entropy_components.py')),
    ('04', 'trajectory_atlas', 'trajectory_atlas.py', 'DiagnosticTrajectoryAtlas', 'clinical_trajectory_atlas.py', 'ClinicalTrajectoryAtlas', ('core/atlas_geometry.py', 'core/atlas_components.py')),
]:
    FILMS[goal, 'original'] = Film(goal, 'original', f'{goal}_{stem}', scene, cls, f'core.story{goal}', dependencies=dependencies)
    FILMS[goal, 'clinical'] = Film(goal, 'clinical', f'{goal}_{stem}_clinical_v2', clinical_scene, clinical_cls, f'core.story{goal}_clinical', dependencies=dependencies)

for goal, stem, cls, fixture, sha, extra in [
    ('05', 'test_results', 'ClinicalTestResults', 'test_results_fixtures.json',
     'd550bb878421bfe75f52361b3987e2059b618fa9c920249608f73dc22118564a', ('core/cohort_components.py',)),
    ('06', 'beliefs_actions', 'ClinicalBeliefsActions', 'beliefs_actions_fixtures.json',
     '86ec0d9fd6553915c92bc70f1fc3af40a3df0424ef7d26772f3df54a39384251',
     ('core/leaf_plots.py', 'core/decision_math.py', 'core/leaf_components.py')),
]:
    FILMS[goal, 'clinical'] = Film(goal, 'clinical', f'{goal}_{stem}_clinical_v1',
        f'clinical_{stem}.py', cls, f'core.story{goal}_clinical', f'data/{fixture}', sha,
        ('core/teaching_scene.py', 'core/subtitles.py') + extra)


def resolve_film(goal, cut=None):
    selected = cut if cut is not None else ('clinical' if goal in ('05', '06') else 'original')
    try:
        return FILMS[goal, selected]
    except KeyError as exc:
        raise ValueError(f'Unsupported goal/cut: {goal}/{selected}') from exc


def film_for_slug(slug):
    for film in FILMS.values():
        if film.slug == slug:
            return film
    raise ValueError(f'Unregistered film slug: {slug}')
