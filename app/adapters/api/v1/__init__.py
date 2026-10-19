from fastapi import APIRouter

from app.adapters.api.v1 import (
    auth,
    committee,
    draw,
    events,
    groups,
    juries,
    organizers,
    participant_rankings,
    participant_scores,
    participants,
    people,
    person,
    poster_contents,
    score_history,
    section_juries,
    sections,
    technical_requirements,
    topics,
    universities,
    venues,
)

router = APIRouter()
router.include_router(auth.router, prefix="/auth")
router.include_router(universities.router, prefix="/universities")
router.include_router(technical_requirements.router, prefix="/technical-requirements")
router.include_router(events.router, prefix="/events")
router.include_router(venues.router, prefix="/venues")
router.include_router(people.router, prefix="/people")
router.include_router(organizers.router, prefix="/organizers")
router.include_router(poster_contents.router, prefix="/poster-contents")
router.include_router(juries.router, prefix="/juries")
router.include_router(participant_scores.router, prefix="/participants/{participant_id}/scores")
router.include_router(score_history.router, prefix="/score-history")
router.include_router(participant_rankings.router, prefix="/participant-rankings")
router.include_router(participants.router, prefix="/participants")
router.include_router(sections.router, prefix="/sections")
router.include_router(section_juries.router, prefix="/section-juries")
router.include_router(committee.router)
router.include_router(groups.router, prefix="/groups")
router.include_router(person.router, prefix="/person")
router.include_router(topics.router, prefix="/topics")
router.include_router(draw.router)
