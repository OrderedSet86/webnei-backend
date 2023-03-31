import strawberry

from src.graphql.fragments.stickynotes_fragments import AddStickyNotesResponse, DeleteStickyNotesResponse, UpdateStickyNotesResponse
from src.graphql.fragments.user_fragments import AddUserResponse, DeleteUserResponse
from src.graphql.resolvers.stickynote_resolver import add_stickynotes, delete_stickynotes, update_stickynotes
from src.graphql.resolvers.user_resolver import add_user, delete_user


@strawberry.type
class Mutation:
    # FIXME: Later add mutations for user data
    # This doesn't do anything, I'm leaving it in for later reference
    @strawberry.mutation
    async def add_stickynotes(self, text: str, user_id: int) -> AddStickyNotesResponse:
        """ Add sticky note """
        add_stickynotes_resp = await add_stickynotes(text, user_id)
        return add_stickynotes_resp
