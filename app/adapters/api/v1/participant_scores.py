from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.adapters.api.dependencies import get_jury_score_service
from app.schemas import JuryScoreCreate, JuryScoreRead, JuryScoreUpdate, ParticipantScoreSummary
from app.services.jury_score import JuryScoreService

router = APIRouter(tags=["participant-scores"])


@router.get("/", response_model=ParticipantScoreSummary)
async def list_participant_scores(
    participant_id: int,
    service: Annotated[JuryScoreService, Depends(get_jury_score_service)],
) -> ParticipantScoreSummary:
    """
    Retrieve all jury scores for a participant with calculated average.

    Returns a summary containing:
    - List of all individual jury scores
    - Calculated average score across all criteria and all jury members

    The average is computed as: (sum of all 5 criteria from all jury members) / (total count)

    Args:
        participant_id: ID of the participant

    Returns:
        ParticipantScoreSummary with scores and average

    Raises:
        HTTPException: 404 if participant not found
    """
    return await service.list_scores_for_participant(participant_id)


@router.get("/{score_id}", response_model=JuryScoreRead)
async def get_participant_score(
    participant_id: int,
    score_id: int,
    service: Annotated[JuryScoreService, Depends(get_jury_score_service)],
) -> JuryScoreRead:
    """
    Retrieve a specific jury score for a participant.

    Args:
        participant_id: ID of the participant
        score_id: ID of the jury score

    Returns:
        JuryScore details

    Raises:
        HTTPException: 404 if score not found or doesn't belong to participant
    """
    score = await service.get_score_by_id(participant_id, score_id)
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score with id {score_id} not found for participant {participant_id}",
        )
    return JuryScoreRead.model_validate(score)


@router.post("/", response_model=JuryScoreRead, status_code=status.HTTP_201_CREATED)
async def create_participant_score(
    participant_id: int,
    payload: JuryScoreCreate,
    service: Annotated[JuryScoreService, Depends(get_jury_score_service)],
) -> JuryScoreRead:
    """
    Create a new jury score for a participant.

    Validations:
    - Each score criterion must be between 0.0 and 10.0
    - Jury member must exist
    - Jury member must be assigned to the participant's section
    - One jury member can only score a participant once (uniqueness)

    If a jury member has already scored this participant, a 422 error
    will be returned with the existing score ID. Use PATCH to update.

    Args:
        participant_id: ID of the participant (from URL)
        payload: Score creation data

    Returns:
        Created jury score

    Raises:
        HTTPException: 404 for missing entities, 422 for validation failures
    """
    score = await service.create_score(participant_id, payload)
    return JuryScoreRead.model_validate(score)


@router.patch("/{score_id}", response_model=JuryScoreRead)
async def update_participant_score(
    participant_id: int,
    score_id: int,
    payload: JuryScoreUpdate,
    service: Annotated[JuryScoreService, Depends(get_jury_score_service)],
    x_jury_id: Annotated[int | None, Header()] = None,
) -> JuryScoreRead:
    """
    Update an existing jury score.

    This operation creates an audit trail entry in the jury_scores_changes table
    recording who made the update and when.

    All fields are optional - only provided fields will be updated.

    Args:
        participant_id: ID of the participant (from URL)
        score_id: ID of the score to update
        payload: Update data (all fields optional)
        x_jury_id: ID of jury member making the update (from header, for audit trail)

    Returns:
        Updated jury score

    Raises:
        HTTPException: 404 if score not found, 422 if validation fails
    """
    if x_jury_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="X-Jury-Id header is required for audit trail",
        )

    score = await service.update_score(participant_id, score_id, payload, x_jury_id)
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score with id {score_id} not found for participant {participant_id}",
        )
    return JuryScoreRead.model_validate(score)


@router.delete("/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_participant_score(
    participant_id: int,
    score_id: int,
    service: Annotated[JuryScoreService, Depends(get_jury_score_service)],
) -> None:
    """
    Delete a jury score.

    Args:
        participant_id: ID of the participant (from URL)
        score_id: ID of the score to delete

    Raises:
        HTTPException: 404 if score not found or doesn't belong to participant
    """
    deleted = await service.delete_score(participant_id, score_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score with id {score_id} not found for participant {participant_id}",
        )
